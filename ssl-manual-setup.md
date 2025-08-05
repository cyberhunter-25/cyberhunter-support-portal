# SSL Certificate Setup for guardian.clirsec.com

## Quick Setup Commands

SSH into your server and run these commands:

```bash
# 1. Install Nginx and Certbot
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# 2. Create Nginx configuration
nano /etc/nginx/sites-available/guardian.clirsec.com
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name guardian.clirsec.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Allow larger file uploads
    client_max_body_size 16M;
}
```

```bash
# 3. Enable the site
ln -s /etc/nginx/sites-available/guardian.clirsec.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 4. Test and reload Nginx
nginx -t
systemctl reload nginx

# 5. Get SSL certificate
certbot --nginx -d guardian.clirsec.com

# Follow the prompts:
# - Enter email: alerts@clirsec.com
# - Agree to terms: A
# - Share email: N (optional)
# - Redirect HTTP to HTTPS: 2 (recommended)
```

## Testing

After setup, visit:
- https://guardian.clirsec.com

You should see your portal with a valid SSL certificate!

## Auto-renewal

Certbot automatically sets up renewal. Test with:
```bash
certbot renew --dry-run
```

## Troubleshooting

If you get errors:
```bash
# Check if port 80 is available
lsof -i :80

# Check Nginx logs
tail -f /var/log/nginx/error.log

# Check if DNS has propagated
nslookup guardian.clirsec.com
```