# CyberHunter CLIRSec - Customer Ticket Portal
## Technical Specification Document

### Project Overview
Emergency after-hours technical support portal for registered CyberHunter CLIRSec clients to submit critical security incidents and support requests with automated email alerting to the support team.

---

## System Architecture

### Core Components
1. **Web Application** - Flask/Django-based portal
2. **Authentication System** - OAuth integration (Microsoft/Google)
3. **Database** - PostgreSQL for ticket management and user data
4. **Email System** - SMTP integration with monitoring capabilities
5. **File Storage** - Secure document/screenshot uploads
6. **Admin Panel** - Customer and user management interface

### Technology Stack
- **Backend**: Python (Flask/Django)
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap for responsive design)
- **Authentication**: OAuth 2.0 (Microsoft Graph API, Google OAuth)
- **Email**: SMTP with IMAP monitoring
- **File Upload**: Secure file handling with virus scanning
- **Hosting**: Docker containerized deployment

---

## User Roles & Access Control

### 1. Client Users
- **Access**: Company-specific ticket view only
- **Permissions**: Create tickets, view own tickets, reply to tickets
- **Authentication**: Microsoft/Google OAuth

### 2. CyberHunter Administrators
- **Access**: All client tickets and system administration
- **Permissions**: View all tickets, manage clients, onboard users, system configuration
- **Authentication**: Dedicated admin credentials + MFA

### 3. CyberHunter Support Staff
- **Access**: All client tickets (read/respond)
- **Permissions**: Respond to tickets, update status, internal notes
- **Authentication**: Dedicated staff credentials

---

## Core Features

### UI/UX Design Specifications

#### Dark Cyber Theme
```css
/* Color Palette */
:root {
  --primary-bg: #0a0a0a;           /* Deep black background */
  --secondary-bg: #1a1a1a;        /* Lighter black for cards */
  --accent-bg: #2a2a2a;           /* Hover states */
  --primary-text: #ffffff;         /* White text */
  --secondary-text: #cccccc;       /* Light gray text */
  --accent-color: #00ff88;         /* Cyber green */
  --warning-color: #ff6b35;        /* Orange for alerts */
  --danger-color: #ff3333;         /* Red for critical */
  --border-color: #333333;         /* Subtle borders */
  --glow-color: #00ff8844;         /* Subtle glow effects */
}

/* Typography */
body {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
  color: var(--primary-text);
}

/* Cyber effects */
.cyber-border {
  border: 1px solid var(--accent-color);
  box-shadow: 0 0 10px var(--glow-color);
  border-radius: 4px;
}

.priority-1 { 
  border-left: 4px solid var(--danger-color);
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0% { box-shadow: 0 0 5px #ff3333; }
  50% { box-shadow: 0 0 20px #ff3333, 0 0 30px #ff3333; }
  100% { box-shadow: 0 0 5px #ff3333; }
}
```

#### Login Page Layout
```html
<!-- Login page structure -->
<div class="login-container">
  <div class="logo-section">
    <img src="logo.png" alt="CyberHunter CLIRSec" class="company-logo">
    <h1 class="portal-title">CyberHunter CLIRSec</h1>
    <h2 class="portal-subtitle">Customer Ticket Portal</h2>
  </div>
  
  <div class="disclaimer-box cyber-border">
    <p>⚠️ RESTRICTED ACCESS</p>
    <p>This portal is restricted to registered CyberHunter CLIRSec clients only. 
       Unauthorized access is prohibited. All activities are logged and monitored.</p>
  </div>
  
  <div class="oauth-buttons">
    <button class="oauth-btn microsoft-btn cyber-border">
      <i class="fab fa-microsoft"></i> Sign in with Microsoft
    </button>
    <button class="oauth-btn google-btn cyber-border">
      <i class="fab fa-google"></i> Sign in with Google
    </button>
  </div>
  
  <div class="emergency-contact">
    <p>🚨 Critical Emergency? Call: +1-XXX-XXX-XXXX</p>
  </div>
</div>
```

### Ticket Creation Form
**Pre-populated Fields:**
- Company Name (from OAuth profile)
- User Name (from OAuth profile)  
- Email Address (from OAuth profile)
- Timestamp (auto-generated)

**User Input Fields:**
- **Priority Level** (Dropdown):
  - Priority 1: Critical Emergency (Security breach, system down)
  - Priority 2: High (Significant impact, degraded service)
  - Priority 3: Medium (Moderate impact, workaround available)
  - Priority 4: Low (Minor issue, informational)

- **Issue Description** (Rich text area)
- **File Attachments** (Multiple file upload with support for):
  - Screenshots (.png, .jpg, .jpeg, .gif)
  - Documents (.pdf, .doc, .docx, .txt)
  - Log files (.log, .txt, .csv)
  - Evidence files (.zip, .7z)
  - Maximum file size: 25MB per file, 100MB total per ticket

### Ticket Management System
- **Unique Ticket ID Generation**: 
  - Format: `CH-YYYYMMDD-XXXX` (e.g., CH-20250730-0001)
  - Sequential numbering with date prefix
  
- **Ticket Status Tracking**:
  - New
  - In Progress  
  - Pending Client Response
  - Resolved
  - Closed

- **Communication Trail**:
  - Chronological message thread
  - Timestamp for each interaction
  - User identification (Client vs CyberHunter staff)
  - File attachment history

### Email Integration System

#### Outbound Email Automation
1. **Ticket Acknowledgment Email** (Auto-sent on ticket creation):
   ```
   Subject: [Ticket #CH-YYYYMMDD-XXXX] - Acknowledgment - [Priority Level]
   
   Content:
   - Ticket number and priority
   - Summary of reported issue
   - Expected response time based on priority
   - Portal link for updates
   - Emergency contact procedures
   ```

2. **Alert Email to Support Team** (Auto-sent on ticket creation):
   ```
   Subject: [ALERT] New Priority X Ticket - #CH-YYYYMMDD-XXXX
   
   Content:
   - Client information
   - Priority level (highlighted for P1/P2)
   - Issue summary
   - Direct link to ticket in admin panel
   ```

#### Inbound Email Monitoring
- **IMAP Integration**: Monitor designated support email for replies
- **Ticket Matching**: Parse email subjects for ticket numbers
- **Auto-Update**: Add email replies to ticket communication trail
- **Attachment Processing**: Handle reply attachments automatically

---

## Admin Panel Features

### Client Management
- **Company Onboarding**:
  - Add new client companies
  - Configure OAuth domains
  - Set priority level permissions
  - Contact information management

- **User Management**:
  - Add/remove authorized users per company
  - Email domain verification
  - Access level configuration
  - Deactivation capabilities

### System Administration
- **Dashboard Analytics**:
  - Ticket volume by priority
  - Response time metrics
  - Client activity overview
  - System health monitoring

- **Configuration Management**:
  - Email server settings
  - Priority level definitions
  - Alert thresholds
  - Maintenance mode controls

---

## Security Requirements

### Data Protection
- **Encryption**: All data encrypted at rest and in transit (TLS 1.3)
- **File Scanning**: Uploaded files scanned for malware
- **Access Logs**: Comprehensive audit trail for all user actions
- **Session Management**: Secure session handling with timeout controls

### Authentication Security
- **OAuth Implementation**: Secure token handling and validation
- **MFA Support**: Multi-factor authentication for admin accounts
- **Rate Limiting**: Prevent brute force attacks
- **Domain Validation**: Restrict access to pre-approved email domains

### Infrastructure Security
- **Container Security**: Docker security best practices
- **Database Security**: Encrypted connections, principle of least privilege
- **Backup Strategy**: Automated encrypted backups
- **Monitoring**: Security event logging and alerting

---

## Database Schema

### Tables Required
```sql
-- Companies
companies (id, name, domain, created_at, active, contact_info)

-- Users  
users (id, company_id, email, name, oauth_provider, oauth_id, created_at, active)

-- Tickets
tickets (id, ticket_number, company_id, user_id, priority, status, subject, description, created_at, updated_at)

-- Ticket Messages
ticket_messages (id, ticket_id, user_id, message, is_internal, created_at)

-- File Attachments
attachments (id, ticket_id, filename, file_path, file_size, uploaded_by, created_at)

-- Admin Users
admin_users (id, username, email, password_hash, role, mfa_enabled, created_at)
```

---

## Email Configuration Requirements

### SMTP Settings
- **Server**: TLS-enabled SMTP server
- **Authentication**: Service account credentials
- **Rate Limiting**: Configured to prevent spam flagging
- **Templates**: HTML email templates with company branding

### IMAP Monitoring
- **Polling Frequency**: Every 60 seconds for new emails
- **Processing Rules**: Parse ticket numbers, validate senders
- **Error Handling**: Failed processing alerts to admin
- **Archive Management**: Automatic cleanup of processed emails

---

## Deployment Specifications

### Environment Requirements
```dockerfile
# Production Deployment Stack
FROM python:3.11-slim

# System Dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    clamav \
    clamav-daemon \
    fail2ban \
    nginx \
    supervisor

# Python Dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# requirements.txt content:
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Authlib==1.2.1
requests==2.31.0
psycopg2-binary==2.9.7
redis==4.6.0
celery==5.3.1
python-dotenv==1.0.0
cryptography==41.0.4
Pillow==10.0.0
python-magic==0.4.27
email-validator==2.0.0
```

### Hetzner Server Setup Script
```bash
#!/bin/bash
# Initial server configuration for Ubuntu 22.04

# System updates
apt update && apt upgrade -y

# Install required packages
apt install -y python3.11 python3-pip postgresql postgresql-contrib \
               redis-server nginx clamav clamav-daemon fail2ban \
               certbot python3-certbot-nginx ufw git

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Configure fail2ban
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Configure PostgreSQL
sudo -u postgres createdb cyberhunter_portal
sudo -u postgres createuser cyberhunter_user
sudo -u postgres psql -c "ALTER USER cyberhunter_user PASSWORD 'SECURE_PASSWORD_HERE';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cyberhunter_portal TO cyberhunter_user;"

# Configure ClamAV
freshclam
systemctl enable clamav-daemon
systemctl start clamav-daemon

echo "Server setup complete. Deploy application and configure SSL."
```

### Infrastructure Requirements
- **Server**: Minimum 4GB RAM, 2 CPU cores, 100GB storage
- **SSL**: TLS certificate for HTTPS
- **Domain**: Dedicated subdomain (e.g., support.cyberhunter.com)
- **Email**: Dedicated email account for system operations
- **Backup**: Automated daily backups with 30-day retention

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Core Infrastructure:**
- Set up Hetzner server with security hardening
- Configure PostgreSQL database with encryption
- Implement basic Flask application structure
- Set up OAuth providers (Microsoft + Google)
- Create basic authentication system
- Implement session management with Redis

**Deliverables:**
- Working login system with OAuth
- Basic database schema
- Secure server environment
- SSL certificate installation

### Phase 2: Core Portal Features (Weeks 3-4)
**Ticket System:**
- Implement ticket creation form with file uploads
- Create unique ticket ID generation system
- Build ticket viewing and communication trail
- Implement email acknowledgment system
- Set up ClamAV malware scanning for uploads

**Admin Panel:**
- Create admin authentication system
- Build client onboarding interface
- Implement user management features
- Create basic dashboard with ticket overview

**Deliverables:**
- Working ticket creation and viewing
- File upload with security scanning
- Basic admin panel functionality
- Email acknowledgment system

### Phase 3: Advanced Features (Weeks 5-6)
**Email Integration:**
- Implement IMAP monitoring for guardian@clirsec.com
- Create email parsing for ticket replies
- Build automated ticket updates from email replies
- Implement email threading and attachment handling

**Push Notifications:**
- Integrate ntfy.sh for Priority 1/2 alerts
- Create notification preferences system
- Implement admin notification settings
- Test emergency alert delivery

**Deliverables:**
- Full email integration (inbound/outbound)
- Push notification system
- Complete communication trail
- Admin notification management

### Phase 4: UI/UX & Polish (Weeks 7-8)
**Professional Interface:**
- Implement dark cyber theme
- Integrate company logo and branding
- Create responsive design for mobile devices
- Add loading animations and micro-interactions
- Implement accessibility features

**Security Hardening:**
- Complete security audit
- Implement comprehensive logging
- Set up monitoring and alerting
- Create backup and disaster recovery procedures

**Deliverables:**
- Production-ready interface
- Complete security implementation
- Monitoring and backup systems
- Documentation and user guides

### Phase 5: Testing & Deployment (Week 9)
**Quality Assurance:**
- User acceptance testing with sample clients
- Security penetration testing
- Load testing and performance optimization
- Email delivery testing across providers

**Production Deployment:**
- Deploy to production environment
- Configure monitoring and alerting
- Train CyberHunter admin team
- Onboard initial 10 client companies

**Deliverables:**
- Production deployment
- Admin training materials
- Client onboarding documentation
- Go-live support

---

## Monitoring & Maintenance

### System Monitoring
- **Uptime Monitoring**: 24/7 availability checking
- **Performance Metrics**: Response time and resource usage
- **Security Monitoring**: Intrusion detection and audit logs
- **Email Delivery**: Monitor bounce rates and delivery success

### Maintenance Procedures
- **Regular Updates**: Security patches and dependency updates
- **Database Maintenance**: Regular cleanup and optimization
- **Log Rotation**: Automated log management
- **Backup Testing**: Monthly backup restoration tests

---

## Testing Requirements

### Security Testing
- **Penetration Testing**: Third-party security assessment
- **OAuth Security**: Token validation and session security
- **File Upload Security**: Malware and exploit prevention
- **Input Validation**: SQL injection and XSS prevention

### Functional Testing
- **User Acceptance Testing**: Client workflow validation
- **Email Integration Testing**: End-to-end email functionality
- **Load Testing**: System performance under load
- **Mobile Responsiveness**: Cross-device compatibility

---

## Implementation Configuration

### Email System Configuration
- **Primary Email**: guardian@clirsec.com (Gmail)
- **SMTP Settings**: Gmail SMTP with App Password authentication
- **IMAP Monitoring**: Poll guardian@clirsec.com for ticket replies
- **Email Templates**: HTML templates with CyberHunter branding

### OAuth Provider Setup Required
**Microsoft Azure AD:**
- Create new App Registration in Azure Portal
- Configure redirect URIs for production domain
- Set up API permissions for profile and email access
- Generate client ID and secret

**Google Cloud Console:**
- Create new OAuth 2.0 Client ID
- Configure authorized redirect URIs
- Enable Google+ API for profile access
- Generate client credentials

### Service Level Agreements (SLAs)
- **Priority 1 (Critical Emergency)**: 15 minutes first response
- **Priority 2 (High)**: 1 hour first response, 2-3 hours analysis
- **Priority 3 (Medium)**: 4 hours during business hours
- **Priority 4 (Low)**: 1 business day, best effort

### Push Notification Integration
**ntfy.sh Configuration:**
- Create dedicated topic: `cyberhunter-alerts`
- Admin devices subscribe to topic
- Priority 1 tickets trigger immediate push notifications
- Integration via HTTP POST to ntfy.sh API

### Infrastructure Specifications
**Hetzner Cloud USA Deployment:**
- **Server Size**: CPX21 (3 vCPU, 4GB RAM, 80GB NVMe)
- **OS**: Ubuntu 22.04 LTS
- **Security**: fail2ban, UFW firewall, automatic security updates
- **SSL**: Let's Encrypt with auto-renewal
- **Backup**: Hetzner snapshot backups (daily)

### File Storage Configuration
- **Local Storage Path**: `/var/www/cyberhunter-portal/uploads/`
- **Security**: Segregated by ticket ID, no direct web access
- **Scanning**: ClamAV integration for malware detection
- **Retention**: Files retained for 1 year minimum

### Team Configuration
- **Admin Users**: 3 CyberHunter administrators
- **Initial Clients**: 10 client companies
- **Logo**: PNG format from working directory
- **Theme**: Dark, sleek, professional "cyber" aesthetic