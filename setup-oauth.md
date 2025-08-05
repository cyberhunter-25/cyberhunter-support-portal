# OAuth Setup Guide for guardian.clirsec.com

## Microsoft Azure Setup

1. **Go to Azure Portal**
   - Navigate to: https://portal.azure.com
   - Sign in with your Microsoft account

2. **Create App Registration**
   - Go to "Azure Active Directory" → "App registrations"
   - Click "New registration"
   - Fill in:
     - Name: `CyberHunter Support Portal`
     - Supported account types: `Accounts in any organizational directory (Any Azure AD directory - Multitenant)`
     - Redirect URI: 
       - Type: `Web`
       - URL: `https://guardian.clirsec.com/auth/callback/microsoft`

3. **Get Credentials**
   - After creation, copy the **Application (client) ID**
   - Go to "Certificates & secrets" → "Client secrets" → "New client secret"
   - Add description: `Production Secret`
   - Copy the **Value** (not the Secret ID)

4. **Configure Permissions**
   - Go to "API permissions"
   - Should already have `User.Read`
   - Click "Grant admin consent" if you're an admin

## Google Cloud Setup

1. **Go to Google Cloud Console**
   - Navigate to: https://console.cloud.google.com
   - Create a new project or select existing

2. **Enable APIs**
   - Go to "APIs & Services" → "Enabled APIs"
   - Enable "Google+ API" (for OAuth)

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in:
     - App name: `CyberHunter Support Portal`
     - Support email: `guardian@clirsec.com`
     - Authorized domains: `clirsec.com`
     - Developer contact: `guardian@clirsec.com`

4. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: `Web application`
   - Name: `CyberHunter Portal Production`
   - Authorized redirect URIs: `https://guardian.clirsec.com/auth/callback/google`
   - Copy the **Client ID** and **Client Secret**

## Gmail App Password Setup

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: `Mail`
   - Select device: `Other (Custom name)`
   - Enter: `CyberHunter Portal`
   - Copy the 16-character password

## Next Steps

After getting all credentials:

1. SSH to server: `ssh root@5.161.176.85`
2. Edit config: `nano /opt/cyberhunter-portal/.env.production`
3. Update these values:
   - `MICROSOFT_CLIENT_ID=your-actual-id`
   - `MICROSOFT_CLIENT_SECRET=your-actual-secret`
   - `GOOGLE_CLIENT_ID=your-actual-id`
   - `GOOGLE_CLIENT_SECRET=your-actual-secret`
   - `SMTP_PASSWORD=your-16-char-app-password`
   - `IMAP_PASSWORD=same-16-char-app-password`

4. Restart services:
   ```bash
   cd /opt/cyberhunter-portal
   docker-compose --env-file .env.production restart
   ```