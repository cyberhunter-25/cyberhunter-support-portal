# CyberHunter Security Portal - Quick Start Guide

## 🚀 5-Minute Cloud Deployment

### Prerequisites
- Ubuntu 22.04 cloud server (Hetzner, AWS, DigitalOcean, etc.)
- Domain name pointed to your server IP
- SSH access to the server

### Step 1: Connect to Your Server
```bash
ssh root@your-server-ip
```

### Step 2: Download and Run
```bash
# Download the repository
git clone https://github.com/cyberhunter/support-portal.git
cd support-portal

# Make deployment script executable
chmod +x scripts/deploy.sh

# Copy and edit configuration
cp .env.production.example .env.production
nano .env.production  # Add your settings

# Run deployment
./scripts/deploy.sh
```

### Step 3: Access Your Portal
- User Portal: `https://your-domain.com`
- Admin Panel: `https://your-domain.com/admin`

## 📋 Configuration Checklist

### Required OAuth Setup

#### Microsoft (5 minutes)
1. Visit [Azure Portal](https://portal.azure.com)
2. Create new app registration
3. Add redirect URI: `https://your-domain.com/auth/callback/microsoft`
4. Copy Client ID and Secret to `.env.production`

#### Google (5 minutes)
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add redirect URI: `https://your-domain.com/auth/callback/google`
4. Copy Client ID and Secret to `.env.production`

### Email Configuration (Gmail)
1. Enable 2-factor authentication on Gmail
2. Generate app-specific password
3. Add to `.env.production`:
   ```
   SMTP_USERNAME=guardian@clirsec.com
   SMTP_PASSWORD=your-app-password
   ```

## 🔧 Common Tasks

### Create Admin User
```bash
docker-compose exec web flask create-admin
```

### Add Client Company
```bash
docker-compose exec web python -c "
from app import create_app, db
from app.models import Company
app = create_app()
with app.app_context():
    company = Company(
        name='Client Company Name',
        domain='clientdomain.com',
        allow_local_auth=True
    )
    db.session.add(company)
    db.session.commit()
    print(f'Company {company.name} created!')
"
```

### View Logs
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### Restart Services
```bash
docker-compose restart
```

## 🆘 Troubleshooting

### Can't Access the Site
```bash
# Check if services are running
docker-compose ps

# Check nginx logs
docker-compose logs nginx

# Verify firewall
sudo ufw status
```

### OAuth Not Working
- Verify redirect URIs match exactly
- Check Client ID and Secret are correct
- Ensure domain is using HTTPS

### Email Issues
- Verify Gmail app password (not regular password)
- Check SMTP settings in logs
- Test with: `docker-compose logs celery`

## 📱 First Login

1. Navigate to `https://your-domain.com`
2. Choose authentication method:
   - **OAuth**: Click Microsoft or Google
   - **Local**: Register with email/password
3. Admins: Use `/admin` with MFA setup

## 🔐 Security Notes

- All admin accounts require MFA
- Local users can optionally enable MFA
- SSL certificates auto-renew with Let's Encrypt
- fail2ban protects against brute force

## 📞 Need Help?

- Logs: `docker-compose logs -f`
- Health Check: `curl https://your-domain.com/health`
- Emergency: Call support number in portal

---

**Next Steps:**
1. Configure OAuth providers ✓
2. Create admin account ✓
3. Add client companies ✓
4. Test ticket creation ✓
5. Monitor system health ✓