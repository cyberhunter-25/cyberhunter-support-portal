"""
Admin panel routes
"""
from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, NumberRange, Optional
from app.admin import admin_bp
from app.auth.decorators import admin_required
from app.models.settings import SystemSettings
from app.extensions import db


class OAuthSettingsForm(FlaskForm):
    """OAuth settings form"""
    microsoft_client_id = StringField('Microsoft Client ID')
    microsoft_client_secret = PasswordField('Microsoft Client Secret')
    microsoft_tenant_id = StringField('Microsoft Tenant ID', default='common')
    google_client_id = StringField('Google Client ID')
    google_client_secret = PasswordField('Google Client Secret')
    allowed_domains = TextAreaField('Allowed Domains (one per line)')


class EmailSettingsForm(FlaskForm):
    """Email settings form"""
    smtp_server = StringField('SMTP Server', validators=[DataRequired()], default='smtp.gmail.com')
    smtp_port = IntegerField('SMTP Port', validators=[DataRequired(), NumberRange(min=1, max=65535)], default=587)
    smtp_username = StringField('SMTP Username', validators=[DataRequired()])
    smtp_password = PasswordField('SMTP Password')
    smtp_use_tls = BooleanField('Use TLS', default=True)
    from_address = StringField('From Address', validators=[DataRequired(), Email()], default='guardian@clirsec.com')
    from_name = StringField('From Name', validators=[DataRequired()], default='CyberHunter Support')
    imap_server = StringField('IMAP Server', validators=[DataRequired()], default='imap.gmail.com')
    imap_port = IntegerField('IMAP Port', validators=[DataRequired(), NumberRange(min=1, max=65535)], default=993)
    imap_username = StringField('IMAP Username', validators=[DataRequired()])
    imap_password = PasswordField('IMAP Password')
    imap_use_ssl = BooleanField('Use SSL', default=True)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin/dashboard.html')


@admin_bp.route('/settings')
@admin_required
def settings():
    """Main settings page"""
    return render_template('admin/settings.html')


@admin_bp.route('/settings/oauth', methods=['GET', 'POST'])
@admin_required
def settings_oauth():
    """OAuth configuration page"""
    form = OAuthSettingsForm()
    
    if form.validate_on_submit():
        try:
            # Parse allowed domains
            allowed_domains = []
            if form.allowed_domains.data:
                allowed_domains = [domain.strip() for domain in form.allowed_domains.data.split('\n') if domain.strip()]
            
            # Save OAuth settings
            oauth_settings = {
                'microsoft_client_id': form.microsoft_client_id.data or '',
                'microsoft_client_secret': form.microsoft_client_secret.data or '',
                'microsoft_tenant_id': form.microsoft_tenant_id.data or 'common',
                'google_client_id': form.google_client_id.data or '',
                'google_client_secret': form.google_client_secret.data or '',
                'allowed_domains': allowed_domains
            }
            
            SystemSettings.set_oauth_settings(oauth_settings)
            flash('OAuth settings saved successfully!', 'success')
            return redirect(url_for('admin.settings_oauth'))
            
        except Exception as e:
            flash(f'Error saving OAuth settings: {str(e)}', 'danger')
    
    # Load current settings
    current_settings = SystemSettings.get_oauth_settings()
    form.microsoft_client_id.data = current_settings['microsoft_client_id']
    form.microsoft_tenant_id.data = current_settings['microsoft_tenant_id']
    form.google_client_id.data = current_settings['google_client_id']
    form.allowed_domains.data = '\n'.join(current_settings['allowed_domains'])
    
    # Don't pre-populate sensitive fields for security
    return render_template('admin/settings_oauth.html', form=form)


@admin_bp.route('/settings/email', methods=['GET', 'POST'])
@admin_required
def settings_email():
    """Email configuration page"""
    form = EmailSettingsForm()
    
    if form.validate_on_submit():
        try:
            # Save email settings
            email_settings = {
                'smtp_server': form.smtp_server.data,
                'smtp_port': form.smtp_port.data,
                'smtp_username': form.smtp_username.data,
                'smtp_password': form.smtp_password.data or '',  # Only update if provided
                'smtp_use_tls': form.smtp_use_tls.data,
                'from_address': form.from_address.data,
                'from_name': form.from_name.data,
                'imap_server': form.imap_server.data,
                'imap_port': form.imap_port.data,
                'imap_username': form.imap_username.data,
                'imap_password': form.imap_password.data or '',  # Only update if provided
                'imap_use_ssl': form.imap_use_ssl.data
            }
            
            # Don't overwrite existing passwords if not provided
            current_settings = SystemSettings.get_email_settings()
            if not email_settings['smtp_password']:
                email_settings['smtp_password'] = current_settings['smtp_password']
            if not email_settings['imap_password']:
                email_settings['imap_password'] = current_settings['imap_password']
            
            SystemSettings.set_email_settings(email_settings)
            flash('Email settings saved successfully!', 'success')
            return redirect(url_for('admin.settings_email'))
            
        except Exception as e:
            flash(f'Error saving email settings: {str(e)}', 'danger')
    
    # Load current settings
    current_settings = SystemSettings.get_email_settings()
    form.smtp_server.data = current_settings['smtp_server']
    form.smtp_port.data = current_settings['smtp_port']
    form.smtp_username.data = current_settings['smtp_username']
    form.smtp_use_tls.data = current_settings['smtp_use_tls']
    form.from_address.data = current_settings['from_address']
    form.from_name.data = current_settings['from_name']
    form.imap_server.data = current_settings['imap_server']
    form.imap_port.data = current_settings['imap_port']
    form.imap_username.data = current_settings['imap_username']
    form.imap_use_ssl.data = current_settings['imap_use_ssl']
    
    # Don't pre-populate sensitive fields for security
    return render_template('admin/settings_email.html', form=form)