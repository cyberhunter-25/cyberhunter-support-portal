# CyberHunter Portal - Configuration Questions

After the deployment script runs, you'll need to configure `.env.production` on the server.

## Required Information:

### 1. Domain Configuration
- **DOMAIN_NAME**: What domain/subdomain will you use? (e.g., support.cyberhunter.com)

### 2. OAuth Providers

#### Microsoft Azure:
- **MICROSOFT_CLIENT_ID**: Your Azure App ID
- **MICROSOFT_CLIENT_SECRET**: Your Azure App Secret
- Need to create at: https://portal.azure.com
- Redirect URI: `https://YOUR_DOMAIN/auth/callback/microsoft`

#### Google:
- **GOOGLE_CLIENT_ID**: Your Google OAuth Client ID
- **GOOGLE_CLIENT_SECRET**: Your Google OAuth Secret
- Need to create at: https://console.cloud.google.com
- Redirect URI: `https://YOUR_DOMAIN/auth/callback/google`

### 3. Email Configuration (guardian@clirsec.com)
- **Gmail App Password**: (NOT your regular Gmail password)
  - Enable 2FA on Gmail
  - Generate app password at: https://myaccount.google.com/apppasswords

### 4. SSL Certificate
- Will you use Let's Encrypt (free) or have your own certificate?

### 5. Initial Admin Account
- **Admin Email**: 
- **Admin Username**:
- **Initial Password**: (you'll change this on first login)

## Quick Setup Commands

Once deployed, SSH to your server and run:

```bash
cd /opt/cyberhunter-portal

# Edit configuration
nano .env.production

# After editing, restart services
docker-compose restart

# Create admin account
docker-compose exec web flask create-admin

# View logs
docker-compose logs -f
```

## Need These Values Now?

Let me know:
1. Your domain name
2. If you have OAuth credentials ready
3. If you need help setting up Gmail app password