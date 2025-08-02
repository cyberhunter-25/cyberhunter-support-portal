# GitHub SSH Setup for Server

Follow these steps to set up GitHub access on your server:

## Step 1: SSH into your server

```bash
ssh root@5.161.176.85
```

## Step 2: Generate SSH key on server (if needed)

```bash
# Check if key exists
ls ~/.ssh/id_ed25519

# If not, generate one
ssh-keygen -t ed25519 -C "server@cyberhunter" -f ~/.ssh/id_ed25519 -N ""
```

## Step 3: Display the public key

```bash
cat ~/.ssh/id_ed25519.pub
```

## Step 4: Add key to GitHub

1. Copy the entire output from the command above
2. Go to: https://github.com/settings/keys
3. Click "New SSH key"
4. Title: "CyberHunter Production Server"
5. Key type: "Authentication Key"
6. Paste the key and click "Add SSH key"

## Step 5: Test GitHub connection

```bash
# On the server, test the connection
ssh -T git@github.com
```

You should see: "Hi cyberhunter-25! You've successfully authenticated..."

## Step 6: Deploy the application

```bash
# Still on the server
cd /opt/cyberhunter-portal

# Clone the repository
git clone git@github.com:cyberhunter-25/cyberhunter-support-portal.git .

# If Docker isn't installed
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create production environment file
cp .env.example .env.production

# Edit configuration (you'll need to add your values)
nano .env.production
```

## Step 7: Configure .env.production

Add these required values:

```env
# Domain Configuration
DOMAIN_NAME=support.yourdomain.com  # What's your domain?
FLASK_SECRET_KEY=your-very-long-random-secret-key

# Database
DB_PASSWORD=secure-database-password
REDIS_PASSWORD=secure-redis-password

# OAuth (from Azure/Google)
MICROSOFT_CLIENT_ID=your-azure-app-id
MICROSOFT_CLIENT_SECRET=your-azure-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

# Email Settings
SMTP_USERNAME=guardian@clirsec.com
SMTP_PASSWORD=gmail-app-password
IMAP_USERNAME=guardian@clirsec.com
IMAP_PASSWORD=gmail-app-password
```

## Step 8: Build and start services

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 9: Initialize database

```bash
# Run migrations
docker-compose exec web flask db upgrade

# Create admin user
docker-compose exec web flask create-admin
```

---

After completing these steps, your portal should be running!