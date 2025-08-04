# CyberHunter Security Support Portal - CLAUDE.md

## Project Overview
This is the CyberHunter CLIRSec Customer Ticket Portal - an emergency after-hours technical support system for registered clients to submit critical security incidents with automated email alerting.

## Project Context
- **Type**: Security Support Portal
- **Stack**: Python (Flask), PostgreSQL, OAuth 2.0, Docker
- **Theme**: Dark cyber aesthetic with professional security focus
- **Purpose**: Handle emergency security incidents and support requests

## Key Requirements
1. **Authentication**: Dual authentication system
   - OAuth integration (Microsoft/Google) for corporate clients
   - Local username/password for non-OAuth users (contractors, special cases)
   - Separate admin authentication with MFA
2. **Ticket System**: Priority-based ticketing with unique ID generation
3. **Email Integration**: Automated alerts and IMAP monitoring for replies
4. **File Uploads**: Secure file handling with malware scanning
5. **Admin Panel**: Complete client and user management interface

## Important Commands
```bash
# Development
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
flask run --debug

# Testing
pytest tests/
python -m pytest tests/ -v --cov=app

# Linting & Type Checking
black .
isort .
flake8 .
mypy app/

# Database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Docker
docker build -t cyberhunter-portal .
docker-compose up -d
```

## Project Structure
```
SUPPORT-PORTAL/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── auth/                # OAuth authentication
│   ├── tickets/             # Ticket management
│   ├── admin/               # Admin panel
│   ├── email/               # Email integration
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
├── migrations/              # Database migrations
├── tests/                   # Test suite
├── docker/                  # Docker configuration
├── requirements.txt         # Python dependencies
├── config.py               # Configuration settings
├── .env.example            # Environment variables template
└── docker-compose.yml      # Docker compose configuration
```

## Critical Security Considerations
1. **OAuth Security**: Always validate tokens and implement proper session management
2. **File Upload Security**: Implement ClamAV scanning and strict file type validation
3. **SQL Injection**: Use SQLAlchemy ORM properly, never raw SQL with user input
4. **XSS Prevention**: Sanitize all user input and use Jinja2 auto-escaping
5. **Access Control**: Strict role-based permissions, users only see their company's tickets

## Email Configuration
- **Outbound**: SMTP via guardian@clirsec.com (Gmail)
- **Inbound**: IMAP monitoring of guardian@clirsec.com
- **Templates**: HTML emails with CyberHunter branding
- **Alerts**: Priority 1/2 tickets trigger immediate notifications

## Database Schema Summary
- **companies**: Client company information
- **users**: Both OAuth and local authenticated users
- **local_auth**: Password hashes and MFA secrets for local users
- **tickets**: Support tickets with priority levels
- **ticket_messages**: Communication trail
- **attachments**: Secure file storage
- **admin_users**: CyberHunter staff accounts with MFA

## UI/UX Guidelines
- **Color Scheme**: Deep black (#0a0a0a), cyber green (#00ff88), danger red (#ff3333)
- **Typography**: JetBrains Mono for that "hacker" aesthetic
- **Effects**: Subtle glow effects, pulse animations for critical alerts
- **Responsive**: Mobile-first design with Bootstrap

## Development Phases
1. **Foundation**: Server setup, database, basic Flask app, OAuth
2. **Core Features**: Ticket system, file uploads, email alerts
3. **Advanced**: Email monitoring, push notifications, admin panel
4. **Polish**: UI/UX implementation, security hardening
5. **Deployment**: Testing, production setup, client onboarding

## Testing Requirements
- Unit tests for all models and core functions
- Integration tests for OAuth flows
- Email delivery testing
- Security testing (penetration testing before launch)
- Load testing for concurrent users

## Deployment
- **Platform**: Hetzner Cloud USA (CPX21 instance)
- **OS**: Ubuntu 22.04 LTS
- **Security**: fail2ban, UFW, ClamAV, SSL/TLS
- **Monitoring**: Uptime monitoring, performance metrics
- **Backup**: Daily automated backups with 30-day retention

## Environment Variables Required
```
FLASK_SECRET_KEY=
DATABASE_URL=postgresql://user:password@localhost/cyberhunter_portal
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=guardian@clirsec.com
SMTP_PASSWORD=
IMAP_SERVER=imap.gmail.com
IMAP_USERNAME=guardian@clirsec.com
IMAP_PASSWORD=
REDIS_URL=redis://localhost:6379
NTFY_TOPIC=cyberhunter-alerts
```

## Priority Levels & SLAs
- **Priority 1**: Critical Emergency - 15 min response
- **Priority 2**: High Impact - 1 hour response
- **Priority 3**: Medium Impact - 4 hours response
- **Priority 4**: Low/Informational - 1 business day

## Key Features to Implement
1. **Secure Login**: 
   - OAuth with Microsoft/Google for corporate clients
   - Local username/password registration for non-OAuth users
   - Password reset via email
   - Admin accounts with MFA (TOTP)
   - Domain validation for OAuth users
2. **Ticket Creation**: Auto-populated user info, file uploads, priority selection
3. **Email Alerts**: Automatic acknowledgment and team notifications
4. **Admin Dashboard**: Analytics, client management, system configuration
5. **Communication Trail**: Threaded messages with timestamps
6. **IMAP Integration**: Monitor and parse email replies
7. **Push Notifications**: ntfy.sh for critical alerts
8. **Security Hardening**: Comprehensive audit logging, encryption

## Notes for AI Agents
- Always prioritize security in this defensive security application
- Use existing patterns and conventions from similar Flask projects
- Implement comprehensive error handling and logging
- Write tests alongside features
- Document API endpoints and complex logic
- Follow PEP 8 and use type hints where appropriate
- Consider scalability - this will handle multiple companies

---

## AI Development Team Configuration
*Updated by team-configurator on 2025-07-30*

Your project uses: Python (Flask), PostgreSQL, OAuth 2.0, Docker, Security-focused architecture

### Core Development Team

#### Security & Architecture
- **Security Architecture** → @security-auditor
  - OAuth implementation, session management, CSRF protection
  - Vulnerability assessment, OWASP compliance
  - Secure file upload implementation with ClamAV integration
  - Encryption strategies for sensitive data
  
- **API Design** → @api-architect
  - RESTful endpoints for ticket system
  - Secure API authentication and rate limiting
  - WebSocket setup for real-time notifications
  - API documentation with security considerations

#### Backend Development
- **Flask Backend** → @python-pro
  - Flask app factory pattern, blueprints, middleware
  - SQLAlchemy models with proper relationships
  - Celery task queue for async operations
  - Email integration (SMTP/IMAP)
  
- **Database Expert** → @database-optimizer
  - PostgreSQL schema design and optimization
  - Migration strategies with Flask-Migrate
  - Query optimization for ticket searches
  - Backup and recovery procedures

#### Frontend & UI
- **Frontend Development** → @frontend-developer
  - Dark cyber theme implementation
  - Responsive Bootstrap layouts
  - JavaScript for dynamic interactions
  - Progressive enhancement approach
  
- **UI/UX Specialist** → @tailwind-frontend-expert
  - Cyber aesthetic with JetBrains Mono
  - Glow effects and pulse animations
  - Accessibility compliance
  - Mobile-first responsive design

#### Infrastructure & DevOps
- **Deployment Engineer** → @deployment-engineer
  - Docker containerization setup
  - CI/CD pipeline configuration
  - Hetzner Cloud deployment
  - SSL/TLS certificate management
  
- **Cloud Infrastructure** → @cloud-architect
  - Ubuntu 22.04 server hardening
  - fail2ban and UFW configuration
  - Redis setup for caching/sessions
  - Monitoring and alerting setup

- **DevOps Troubleshooter** → @devops-troubleshooter
  - Production debugging and incident response
  - Flask application error diagnosis
  - Docker container troubleshooting
  - Log analysis and root cause identification
  - Configuration and dependency resolution
  - Service health monitoring and recovery

#### Quality Assurance
- **Test Automation** → @test-automator
  - pytest test suite implementation
  - Integration tests for OAuth flows
  - Email delivery testing
  - Security test scenarios
  
- **Code Review** → @code-reviewer
  - Security-focused code reviews
  - Python best practices enforcement
  - Performance bottleneck identification
  - Documentation quality checks

#### Specialized Features
- **Email Integration** → @backend-developer
  - SMTP configuration for guardian@clirsec.com
  - IMAP monitoring implementation
  - HTML email template design
  - Email threading and parsing
  
- **Real-time Features** → @network-engineer
  - WebSocket implementation for live updates
  - ntfy.sh push notification integration
  - Connection resilience and reconnection
  - Event-driven architecture

### Phase-Based Task Routing

#### Phase 1: Foundation (Week 1-2)
1. **Server Setup** → @deployment-engineer + @security-auditor
2. **Database Schema** → @database-optimizer + @python-pro
3. **Flask App Structure** → @python-pro + @api-architect
4. **OAuth Implementation** → @security-auditor + @python-pro

#### Phase 2: Core Features (Week 3-4)
1. **Ticket System** → @python-pro + @database-optimizer
2. **File Upload Security** → @security-auditor + @python-pro
3. **Email Alerts** → @backend-developer + @python-pro
4. **Basic UI** → @frontend-developer + @tailwind-frontend-expert

#### Phase 3: Advanced Features (Week 5-6)
1. **IMAP Monitoring** → @backend-developer + @python-pro
2. **Push Notifications** → @network-engineer + @backend-developer
3. **Admin Panel** → @python-pro + @frontend-developer
4. **Client Management** → @database-optimizer + @api-architect

#### Phase 4: Polish & Security (Week 7-8)
1. **UI/UX Refinement** → @tailwind-frontend-expert + @frontend-developer
2. **Security Hardening** → @security-auditor + @deployment-engineer
3. **Performance Optimization** → @performance-optimizer + @database-optimizer
4. **Comprehensive Testing** → @test-automator + @code-reviewer

#### Phase 5: Deployment (Week 9-10)
1. **Production Setup** → @deployment-engineer + @cloud-architect
2. **Load Testing** → @performance-optimizer + @test-automator
3. **Security Audit** → @security-auditor + @code-reviewer
4. **Documentation** → @api-documenter + @documentation-specialist

### Example Commands for Your Team

```bash
# Security architecture review
"Review OAuth implementation for security vulnerabilities"

# API endpoint creation
"Create secure ticket submission endpoint with file upload"

# Database optimization
"Optimize ticket search queries for 10k+ records"

# UI implementation
"Implement dark cyber theme with glow effects"

# Email integration
"Setup IMAP monitoring for guardian@clirsec.com"

# Deployment setup
"Configure Docker deployment for Hetzner Cloud"

# Testing implementation
"Create pytest suite for ticket workflow"
```

### Special Considerations for Security Portal

1. **Security-First Approach**: Every feature must be reviewed by @security-auditor
2. **Audit Logging**: All actions logged for compliance
3. **Data Protection**: Encryption at rest and in transit
4. **Access Control**: Strict role-based permissions
5. **Incident Response**: Built-in security incident handling

### Performance Targets

- Page load time: < 2 seconds
- API response time: < 200ms
- Email delivery: < 30 seconds
- File upload scanning: < 10 seconds
- Concurrent users: 100+ without degradation

Your specialized AI security team is configured and ready to build an enterprise-grade defensive security application!