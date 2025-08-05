# CyberHunter Portal Setup Checklist

## ✅ Completed
- [x] Server provisioned (5.161.176.85)
- [x] Docker installed
- [x] Application deployed
- [x] Domain decided (guardian.clirsec.com)

## 📋 TODO Now

### 1. Google Workspace Setup (10 minutes)
- [ ] Log into admin.google.com
- [ ] Add alias `guardian` to alerts@clirsec.com user
- [ ] Enable 2-Step Verification on alerts@clirsec.com
- [ ] Generate App Password for alerts@clirsec.com
- [ ] Note the 16-character app password

### 2. OAuth Setup (20 minutes)

#### Microsoft Azure
- [ ] Go to portal.azure.com
- [ ] Create new app registration
- [ ] Add redirect URI: `https://guardian.clirsec.com/auth/callback/microsoft`
- [ ] Generate client secret
- [ ] Copy Client ID and Secret

#### Google Cloud
- [ ] Go to console.cloud.google.com
- [ ] Create OAuth credentials
- [ ] Add redirect URI: `https://guardian.clirsec.com/auth/callback/google`
- [ ] Copy Client ID and Secret

### 3. Update Server Configuration (5 minutes)
- [ ] SSH to server: `ssh root@5.161.176.85`
- [ ] Edit: `nano /opt/cyberhunter-portal/.env.production`
- [ ] Update these values:
  ```
  SMTP_USERNAME=alerts@clirsec.com
  SMTP_PASSWORD=[your-16-char-app-password]
  IMAP_USERNAME=alerts@clirsec.com
  IMAP_PASSWORD=[same-app-password]
  
  MICROSOFT_CLIENT_ID=[your-azure-client-id]
  MICROSOFT_CLIENT_SECRET=[your-azure-secret]
  
  GOOGLE_CLIENT_ID=[your-google-client-id]
  GOOGLE_CLIENT_SECRET=[your-google-secret]
  ```
- [ ] Restart: `docker-compose --env-file .env.production restart`

### 4. DNS & SSL Setup (10 minutes)
- [ ] Add DNS A record: `guardian.clirsec.com` → `5.161.176.85`
- [ ] Wait for DNS propagation
- [ ] Set up SSL certificate

### 5. Initial Testing
- [ ] Create admin user
- [ ] Test OAuth login
- [ ] Send test ticket
- [ ] Verify email delivery

## Quick Commands

```bash
# Copy configuration to server
scp .env.production.configured root@5.161.176.85:/opt/cyberhunter-portal/.env.production

# SSH and edit
ssh root@5.161.176.85
cd /opt/cyberhunter-portal
nano .env.production

# Restart after configuration
docker-compose --env-file .env.production restart

# View logs
docker-compose --env-file .env.production logs -f

# Create admin user
docker-compose --env-file .env.production exec web flask create-admin
```