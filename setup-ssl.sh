#\!/bin/bash
# Safe SSL Setup Script for CyberHunter Portal
# This script sets up Let's Encrypt SSL certificates without breaking the existing setup

set -e  # Exit on error

echo "=== SSL Setup for guardian.clirsec.com ==="

# Step 1: Create a temporary nginx config for Let's Encrypt verification
echo "Creating temporary nginx configuration..."
cat > /tmp/nginx-temp.conf << 'NGINX_EOF'
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name guardian.clirsec.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            proxy_pass http://host.docker.internal:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
NGINX_EOF

# Step 2: Create directories for certbot
echo "Creating certbot directories..."
mkdir -p /var/www/certbot
mkdir -p /etc/letsencrypt

# Step 3: Stop the current nginx container
echo "Stopping nginx container..."
cd /opt/cyberhunter-portal
docker-compose stop nginx || true

# Step 4: Run a temporary nginx container for Let's Encrypt
echo "Starting temporary nginx for Let's Encrypt..."
docker run -d --name nginx-temp \
    --add-host=host.docker.internal:host-gateway \
    -p 80:80 \
    -v /tmp/nginx-temp.conf:/etc/nginx/nginx.conf:ro \
    -v /var/www/certbot:/var/www/certbot \
    nginx:alpine

# Wait for nginx to start
sleep 5

# Step 5: Run certbot
echo "Generating SSL certificates..."
certbot certonly --webroot \
    --webroot-path /var/www/certbot \
    --email support@clirsec.com \
    --agree-tos \
    --no-eff-email \
    -d guardian.clirsec.com \
    --non-interactive

# Step 6: Stop temporary nginx
echo "Stopping temporary nginx..."
docker stop nginx-temp
docker rm nginx-temp

# Step 7: Create SSL directory and copy certificates
echo "Setting up certificates for Docker..."
mkdir -p /opt/cyberhunter-portal/ssl
cp /etc/letsencrypt/live/guardian.clirsec.com/fullchain.pem /opt/cyberhunter-portal/ssl/cert.pem
cp /etc/letsencrypt/live/guardian.clirsec.com/privkey.pem /opt/cyberhunter-portal/ssl/key.pem
chmod 644 /opt/cyberhunter-portal/ssl/cert.pem
chmod 600 /opt/cyberhunter-portal/ssl/key.pem

echo "=== SSL Setup Complete ==="
echo "SSL certificates are located at:"
echo "  /opt/cyberhunter-portal/ssl/cert.pem"
echo "  /opt/cyberhunter-portal/ssl/key.pem"
