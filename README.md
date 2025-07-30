# CyberHunter Security Support Portal

A professional emergency support ticketing system for CyberHunter CLIRSec clients with OAuth authentication, priority-based ticket management, and automated email alerts.

## Features

- 🔐 **OAuth Authentication** - Secure login via Microsoft/Google
- 🎫 **Priority Ticketing** - 4-level priority system with SLA tracking
- 📧 **Email Integration** - Automated alerts and IMAP monitoring
- 📎 **Secure File Uploads** - Malware scanning with ClamAV
- 👥 **Multi-tenant** - Company-based access control
- 🌙 **Dark Cyber Theme** - Professional security-focused UI
- 🔔 **Push Notifications** - Critical alerts via ntfy.sh
- 📊 **Admin Dashboard** - Complete management interface

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/cyberhunter/support-portal.git
   cd support-portal
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Initialize database**
   ```bash
   make migrate-init
   make migrate
   ```

5. **Run development server**
   ```bash
   make dev
   ```

Visit http://localhost:5000 to access the portal.

## Technology Stack

- **Backend**: Python 3.11, Flask 2.3
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Queue**: Celery with Redis broker
- **Authentication**: OAuth 2.0 (Microsoft Graph, Google)
- **Email**: SMTP/IMAP with Gmail
- **Security**: ClamAV, fail2ban, SSL/TLS
- **Deployment**: Docker, Nginx, Gunicorn

## Development

### Available Commands

```bash
make help          # Show all available commands
make test          # Run test suite
make lint          # Run code linting
make security      # Run security checks
make docker-build  # Build Docker images
make docker-up     # Start Docker containers
```

### Project Structure

```
app/              # Flask application
├── auth/         # OAuth authentication
├── tickets/      # Ticket management
├── admin/        # Admin panel
├── email/        # Email integration
├── security/     # Security utilities
└── static/       # Frontend assets
```

See `project_structure.md` for detailed layout.

## Testing

Run the complete test suite:
```bash
make test
```

Run specific test categories:
```bash
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-security    # Security tests
```

## Security

This application implements defense-in-depth security:

- OAuth 2.0 authentication with domain validation
- All data encrypted at rest and in transit
- Comprehensive audit logging
- File upload scanning with ClamAV
- Rate limiting and CSRF protection
- Regular security updates and monitoring

See `docs/SECURITY.md` for security guidelines.

## Deployment

### Production Setup

1. Configure production environment
2. Set up PostgreSQL and Redis
3. Configure OAuth providers
4. Install SSL certificates
5. Deploy with Docker

See `docs/DEPLOYMENT.md` for detailed instructions.

### System Requirements

- Ubuntu 22.04 LTS
- 4GB RAM minimum
- 2 CPU cores
- 100GB storage
- SSL certificate

## Support

- **Emergency**: Call +1-XXX-XXX-XXXX
- **Email**: support@cyberhunter.com
- **Documentation**: `docs/` directory

## License

Proprietary - CyberHunter CLIRSec. All rights reserved.

---

Built with security and reliability in mind for CyberHunter CLIRSec clients.