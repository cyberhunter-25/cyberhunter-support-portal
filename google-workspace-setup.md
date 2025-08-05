# Google Workspace Setup for guardian@clirsec.com

## Step 1: Create the Email Alias

1. **Go to Google Admin Console**
   - https://admin.google.com
   - Sign in with your Google Workspace admin account

2. **Add the Alias**
   - Navigate to: **Directory** → **Users**
   - Click on the user who will receive guardian@ emails
   - Click **User information** → **Email aliases**
   - Click **ADD ALIAS**
   - Enter: `guardian` (without @clirsec.com)
   - Click **SAVE**

3. **Wait for Propagation**
   - Alias is usually active within minutes
   - Can take up to 24 hours in rare cases

## Step 2: Generate App Password

1. **Go to the Main Account** (not admin console)
   - Sign in to the account that has the guardian@ alias
   - Go to: https://myaccount.google.com/security

2. **Enable 2-Step Verification** (if not already enabled)
   - Click "2-Step Verification"
   - Follow the setup process

3. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: **Mail**
   - Select device: **Other (Custom name)**
   - Enter name: `CyberHunter Portal`
   - Click **Generate**
   - **COPY THE 16-CHARACTER PASSWORD** (spaces don't matter)

## Step 3: Update Portal Configuration

Your `.env.production` should look like this:

```env
# Email Configuration (using main account for auth)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=yourmainaccount@clirsec.com  # The actual mailbox (NOT guardian@)
SMTP_PASSWORD=xxxx xxxx xxxx xxxx          # The 16-char app password
SMTP_USE_TLS=True

IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=yourmainaccount@clirsec.com  # Same main account
IMAP_PASSWORD=xxxx xxxx xxxx xxxx          # Same app password

# Email will appear to come from guardian@
MAIL_DEFAULT_SENDER=guardian@clirsec.com
MAIL_SUPPORT_EMAIL=guardian@clirsec.com
```

## Step 4: Test the Setup

1. **Send a test email TO guardian@clirsec.com**
   - Should arrive in your main mailbox

2. **In Gmail settings for your main account**:
   - Go to Settings → **Accounts and Import**
   - Under "Send mail as", click **Add another email address**
   - Add: guardian@clirsec.com
   - Uncheck "Treat as an alias" 
   - This allows sending FROM guardian@ via SMTP

## Important Notes

- ✅ All guardian@ emails arrive in your main inbox
- ✅ You can filter them with Gmail labels/filters
- ✅ Portal sends emails FROM guardian@clirsec.com
- ✅ Replies go back to your main inbox
- ✅ Only one Google Workspace license needed

## Gmail Filter (Optional but Recommended)

Create a filter to organize guardian@ emails:
1. In Gmail, click the gear → **See all settings** → **Filters and Blocked Addresses**
2. Click **Create a new filter**
3. In "To" field: `guardian@clirsec.com`
4. Click **Create filter**
5. Choose: Apply label "Guardian Portal" (create new label)
6. Optional: Skip the inbox if you want them separate

## Troubleshooting

If emails aren't sending:
- Verify 2-Step Verification is enabled
- Regenerate app password
- Check "Less secure app access" is NOT blocking (shouldn't be with app passwords)
- Ensure you're using the main account username, not the alias

Ready to configure? Let me know:
1. What's your main Google Workspace email?
2. Did you create the guardian@ alias?
3. Do you have the app password?