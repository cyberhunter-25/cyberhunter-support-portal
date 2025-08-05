# Email Alias Setup for guardian@clirsec.com

## How Email Aliases Work with the Portal

An alias will work perfectly because:

1. **Receiving emails**: All emails sent to guardian@clirsec.com will arrive in the main mailbox
2. **Sending emails**: The portal can send emails with "From: guardian@clirsec.com" 
3. **IMAP monitoring**: The portal will monitor the main mailbox and filter for guardian@ emails

## Setup Instructions

### Option 1: Gmail/Google Workspace Alias

If your main email is on Google Workspace:

1. **Create the alias**:
   - Go to Google Admin Console
   - Users → Select user → User information → Email aliases
   - Add alias: guardian@clirsec.com

2. **Configure the portal**:
   ```env
   # Use the MAIN account credentials, not the alias
   SMTP_USERNAME=mainaccount@clirsec.com  # Your actual mailbox
   SMTP_PASSWORD=your-app-password         # App password for main account
   
   IMAP_USERNAME=mainaccount@clirsec.com  # Same main account
   IMAP_PASSWORD=your-app-password         # Same app password
   
   # But set the sender as the alias
   MAIL_DEFAULT_SENDER=guardian@clirsec.com
   ```

### Option 2: Other Email Providers

For other providers (Office 365, cPanel, etc.):

1. **Create alias in your mail system**
2. **Use main account for authentication**
3. **Set guardian@ as the sender address**

## Important Configuration

In your `.env.production`, you'll have:

```env
# Authentication uses your MAIN email account
SMTP_USERNAME=your-main-email@clirsec.com
SMTP_PASSWORD=your-main-account-app-password

IMAP_USERNAME=your-main-email@clirsec.com  
IMAP_PASSWORD=your-main-account-app-password

# But emails appear to come from guardian@
MAIL_DEFAULT_SENDER=guardian@clirsec.com
MAIL_SUPPORT_EMAIL=guardian@clirsec.com
```

## Portal Code Adjustment

The portal will need a small adjustment to filter emails properly. When monitoring IMAP, it should look for emails sent to "guardian@clirsec.com" specifically.

## Benefits

✅ Single mailbox to manage
✅ Single app password
✅ Cost effective
✅ Emails still appear professional from guardian@
✅ Can add more aliases later (support@, alerts@, etc.)

## Testing

After setup, test by:
1. Sending an email TO guardian@clirsec.com
2. Checking if portal receives it
3. Creating a ticket and verifying email is FROM guardian@clirsec.com