"""
OAuth authentication handlers for Microsoft and Google
"""
from flask import current_app, redirect, url_for, session, flash, request
from flask_login import login_user
from authlib.integrations.flask_client import OAuthError

from app.extensions import oauth, db
from app.models import User, Company
from app.utils import log_user_action, get_client_ip, get_user_agent


def init_oauth_routes(bp):
    """Initialize OAuth routes on the auth blueprint"""
    
    @bp.route('/login/<provider>')
    def oauth_login(provider):
        """Initiate OAuth login flow"""
        if provider not in ['microsoft', 'google']:
            flash('Invalid authentication provider', 'error')
            return redirect(url_for('auth.login'))
        
        client = oauth.create_client(provider)
        if not client:
            flash(f'{provider.capitalize()} authentication is not configured', 'error')
            return redirect(url_for('auth.login'))
        
        # Store the next URL in session
        session['next_url'] = request.args.get('next')
        
        redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
        return client.authorize_redirect(redirect_uri)
    
    @bp.route('/callback/<provider>')
    def oauth_callback(provider):
        """Handle OAuth callback"""
        if provider not in ['microsoft', 'google']:
            flash('Invalid authentication provider', 'error')
            return redirect(url_for('auth.login'))
        
        client = oauth.create_client(provider)
        if not client:
            flash(f'{provider.capitalize()} authentication is not configured', 'error')
            return redirect(url_for('auth.login'))
        
        try:
            # Get the OAuth token
            token = client.authorize_access_token()
            
            # Get user info from the provider
            if provider == 'microsoft':
                user_info = get_microsoft_user_info(client, token)
            else:  # google
                user_info = get_google_user_info(client, token)
            
            if not user_info:
                flash('Failed to retrieve user information', 'error')
                log_user_action(
                    action='oauth_login_failed',
                    details={'provider': provider, 'error': 'No user info'},
                    success=False
                )
                return redirect(url_for('auth.login'))
            
            # Process the user login
            user = process_oauth_login(provider, user_info)
            
            if user:
                login_user(user)
                user.update_last_login()
                
                log_user_action(
                    action='oauth_login_success',
                    user=user,
                    details={'provider': provider}
                )
                
                # Redirect to next URL or home
                next_url = session.pop('next_url', None)
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('tickets.index'))
            else:
                return redirect(url_for('auth.login'))
                
        except OAuthError as e:
            current_app.logger.error(f'OAuth error: {str(e)}')
            flash('Authentication failed. Please try again.', 'error')
            log_user_action(
                action='oauth_login_failed',
                details={'provider': provider, 'error': str(e)},
                success=False
            )
            return redirect(url_for('auth.login'))


def get_microsoft_user_info(client, token):
    """Get user information from Microsoft"""
    try:
        # Get user info from Microsoft Graph API
        resp = client.get('https://graph.microsoft.com/v1.0/me', token=token)
        resp.raise_for_status()
        user_info = resp.json()
        
        return {
            'id': user_info.get('id'),
            'email': user_info.get('mail') or user_info.get('userPrincipalName'),
            'name': user_info.get('displayName'),
            'given_name': user_info.get('givenName'),
            'family_name': user_info.get('surname'),
            'provider': 'microsoft'
        }
    except Exception as e:
        current_app.logger.error(f'Error getting Microsoft user info: {str(e)}')
        return None


def get_google_user_info(client, token):
    """Get user information from Google"""
    try:
        # Get user info from Google
        resp = client.get('userinfo', token=token)
        user_info = resp.json()
        
        return {
            'id': user_info.get('sub'),
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'given_name': user_info.get('given_name'),
            'family_name': user_info.get('family_name'),
            'email_verified': user_info.get('email_verified'),
            'picture': user_info.get('picture'),
            'provider': 'google'
        }
    except Exception as e:
        current_app.logger.error(f'Error getting Google user info: {str(e)}')
        return None


def process_oauth_login(provider, user_info):
    """Process OAuth login and create/update user"""
    email = user_info.get('email')
    oauth_id = user_info.get('id')
    
    if not email or not oauth_id:
        flash('Invalid user information received', 'error')
        return None
    
    # Normalize email
    email = email.lower()
    
    # Check if user exists by OAuth ID
    user = User.find_by_oauth(provider, oauth_id)
    
    if user:
        # Existing OAuth user
        if not user.active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            log_user_action(
                action='oauth_login_blocked',
                user=user,
                details={'reason': 'account_deactivated'},
                success=False
            )
            return None
        
        # Update user info if changed
        if user.name != user_info.get('name'):
            user.name = user_info.get('name')
            db.session.commit()
        
        return user
    
    # Check if user exists by email
    existing_user = User.find_by_email(email)
    
    if existing_user:
        # User exists with same email but different auth method
        if existing_user.auth_type == 'local':
            flash('An account with this email already exists. Please use your password to login.', 'error')
            return None
        else:
            # OAuth user with different provider
            flash(f'An account with this email already exists using {existing_user.oauth_provider} login.', 'error')
            return None
    
    # New user - check if email domain is allowed
    company = find_company_by_email(email)
    
    if not company:
        flash('Your email domain is not authorized. Please contact your administrator.', 'error')
        log_user_action(
            action='oauth_login_blocked',
            details={'email': email, 'reason': 'domain_not_authorized'},
            success=False
        )
        return None
    
    if not company.active:
        flash('Your company account has been deactivated. Please contact support.', 'error')
        log_user_action(
            action='oauth_login_blocked',
            details={'email': email, 'company': company.name, 'reason': 'company_deactivated'},
            success=False
        )
        return None
    
    # Create new user
    user = User(
        company_id=company.id,
        email=email,
        name=user_info.get('name', email.split('@')[0]),
        auth_type='oauth',
        oauth_provider=provider,
        oauth_id=oauth_id,
        active=True,
        email_verified=user_info.get('email_verified', True)  # Google provides this
    )
    
    db.session.add(user)
    db.session.commit()
    
    flash(f'Welcome {user.name}! Your account has been created.', 'success')
    log_user_action(
        action='oauth_user_created',
        user=user,
        details={'provider': provider}
    )
    
    return user


def find_company_by_email(email):
    """Find company by email domain"""
    if not email or '@' not in email:
        return None
    
    domain = email.split('@')[1].lower()
    
    # Find all active companies
    companies = Company.query.filter_by(active=True).all()
    
    for company in companies:
        if company.is_domain_allowed(email):
            return company
    
    return None