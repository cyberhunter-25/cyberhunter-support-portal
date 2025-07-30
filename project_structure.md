# Optimized Project Structure for CyberHunter Security Portal

## Enhanced Directory Structure
```
SUPPORT-PORTAL/
├── app/
│   ├── __init__.py              # Flask app factory with security middleware
│   ├── config.py                # Configuration classes (Dev, Prod, Test)
│   ├── extensions.py            # Flask extensions initialization
│   ├── models/
│   │   ├── __init__.py
│   │   ├── company.py           # Company model
│   │   ├── user.py              # User model
│   │   ├── ticket.py            # Ticket & message models
│   │   ├── attachment.py        # File attachment model
│   │   └── admin.py             # Admin user model
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── oauth.py             # OAuth handlers
│   │   ├── local.py             # Local auth (username/password)
│   │   ├── mfa.py               # Multi-factor authentication
│   │   ├── decorators.py        # Auth decorators
│   │   ├── forms.py             # Login/register forms
│   │   └── routes.py            # Auth routes
│   ├── tickets/
│   │   ├── __init__.py
│   │   ├── routes.py            # Ticket endpoints
│   │   ├── forms.py             # WTForms for tickets
│   │   ├── services.py          # Business logic
│   │   └── validators.py        # Input validation
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── routes.py            # Admin endpoints
│   │   ├── forms.py             # Admin forms
│   │   └── services.py          # Admin logic
│   ├── email/
│   │   ├── __init__.py
│   │   ├── sender.py            # SMTP email sending
│   │   ├── monitor.py           # IMAP monitoring
│   │   ├── templates.py         # Email templates
│   │   └── parser.py            # Email parsing
│   ├── security/
│   │   ├── __init__.py
│   │   ├── scanner.py           # ClamAV integration
│   │   ├── encryption.py        # Data encryption
│   │   ├── audit.py             # Audit logging
│   │   └── validators.py        # Security validators
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/                  # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── tickets.py       # Ticket API
│   │   │   └── auth.py          # Auth API
│   │   └── errors.py            # API error handlers
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css         # Main styles
│   │   │   └── cyber-theme.css  # Dark cyber theme
│   │   ├── js/
│   │   │   ├── app.js           # Main JavaScript
│   │   │   └── notifications.js  # Real-time updates
│   │   └── img/
│   │       └── logo.png         # CyberHunter logo
│   ├── templates/
│   │   ├── base.html            # Base template
│   │   ├── auth/
│   │   ├── tickets/
│   │   ├── admin/
│   │   └── errors/
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py           # Utility functions
│       ├── constants.py         # App constants
│       └── decorators.py        # Custom decorators
├── migrations/                  # Alembic migrations
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   ├── unit/
│   ├── integration/
│   └── security/
├── scripts/
│   ├── setup_dev.sh            # Development setup
│   ├── deploy.sh               # Deployment script
│   └── backup.sh               # Backup script
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── docs/
│   ├── API.md                  # API documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── SECURITY.md             # Security documentation
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline
│       └── security.yml        # Security scanning
├── requirements/
│   ├── base.txt                # Base requirements
│   ├── dev.txt                 # Development requirements
│   └── prod.txt                # Production requirements
├── .env.example                # Environment template
├── .gitignore
├── README.md
├── CLAUDE.md                   # AI agent documentation
├── pyproject.toml              # Python project config
└── Makefile                    # Common commands
```

## Optimization Improvements

### 1. Modular Architecture
- Separated models into individual files for better maintainability
- Created dedicated security module for all security operations
- API versioning support from the start
- Clear separation of concerns with services layer

### 2. Security Enhancements
- Dedicated security module with encryption utilities
- Audit logging built into the architecture
- Security validators for all user inputs
- ClamAV scanner integration centralized

### 3. Development Efficiency
- Makefile for common commands
- Scripts for setup and deployment
- Separate requirements files for different environments
- GitHub Actions for CI/CD

### 4. Testing Structure
- Unit, integration, and security test separation
- Shared fixtures in conftest.py
- Security-specific test suite

### 5. Documentation
- Comprehensive docs folder
- API documentation
- Security guidelines
- Deployment procedures

## Key Optimizations Made

1. **Performance**
   - Redis caching strategy built-in
   - Database query optimization patterns
   - Async email processing with Celery
   - Static file optimization

2. **Security**
   - Defense in depth approach
   - Input validation at multiple layers
   - Comprehensive audit logging
   - Encrypted file storage

3. **Scalability**
   - Microservice-ready architecture
   - API versioning from start
   - Horizontal scaling support
   - Queue-based email processing

4. **Maintainability**
   - Clear module boundaries
   - Consistent naming conventions
   - Comprehensive documentation
   - Type hints throughout

5. **Developer Experience**
   - Makefile for common tasks
   - Development setup script
   - Clear project structure
   - Extensive error handling

## Enhanced Database Schema for Dual Authentication

The database schema has been updated to support both OAuth and local authentication:

```sql
-- Companies (updated)
companies (
    id, name, domain, created_at, active, 
    contact_info, allow_local_auth -- New: flag to enable local auth
)

-- Users (updated to support both auth types)
users (
    id, company_id, email, name, 
    auth_type,      -- 'oauth' or 'local'
    oauth_provider, -- 'microsoft', 'google', or NULL
    oauth_id,       -- OAuth user ID or NULL
    created_at, active, last_login
)

-- Local Authentication (new table)
local_auth (
    id, user_id, username, password_hash,
    mfa_secret,     -- TOTP secret for 2FA
    mfa_enabled,    -- Boolean for MFA status
    password_reset_token, token_expiry,
    failed_attempts, locked_until,
    created_at, updated_at
)

-- Admin Users (updated with MFA)
admin_users (
    id, username, email, password_hash, role,
    mfa_secret,     -- TOTP secret (required for admins)
    mfa_enabled,    -- Always true for admins
    created_at, last_login, 
    failed_attempts, locked_until
)

-- Password History (new for compliance)
password_history (
    id, user_id, password_hash, created_at
)

-- Audit Log (expanded)
audit_log (
    id, user_id, user_type, action, 
    resource, details, ip_address, 
    user_agent, created_at
)
```

### Authentication Flow Updates

1. **Login Page** now offers three options:
   - Sign in with Microsoft
   - Sign in with Google  
   - Sign in with Username/Password

2. **Local Registration** (if enabled for company):
   - Username/email validation
   - Strong password requirements
   - Optional MFA setup
   - Email verification

3. **Password Management**:
   - Secure reset via email token
   - Password history to prevent reuse
   - Complexity requirements
   - Account lockout after failed attempts

4. **MFA Implementation**:
   - TOTP (Time-based One-Time Password)
   - QR code generation for authenticator apps
   - Backup codes for recovery
   - Required for all admin accounts