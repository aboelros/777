# Messenger API Setup Guide

This guide details how to set up the **Messenger** product in your Meta App and configure the necessary environment variables.

## 1. Environment Variables needed

Add these to your backend `.env` file (or Railway variables):

```env
# Required for Messenger
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_APP_SECRET=your_app_secret
WHATSAPP_VERIFY_TOKEN=01012011
```

*   `FACEBOOK_PAGE_ACCESS_TOKEN`: Generated in step 2.3 below.
*   `FACEBOOK_PAGE_ID`: The ID of the Facebook Page you are connecting.
*   `FACEBOOK_APP_SECRET`: Found in App Settings -> Basic.
*   `WHATSAPP_VERIFY_TOKEN`: Your chosen verification string (`01012011`).

## 2. Setup Guide

### Step 1: Add Messenger Product
1.  Go to your App Dashboard on [developers.facebook.com](https://developers.facebook.com/).
2.  Scroll down to the "Add a product" section.
3.  Find **Messenger** and click **Set Up**.

### Step 2: Configure Access Tokens
1.  In the Messenger settings sidebar, go to **Instagram settings** or **Settings** (depending on if you want IG or FB Messenger).
2.  Scroll to the **Access Tokens** section.
3.  Click **Add or Remove Pages**.
4.  Select the Facebook Page you want to connect.
5.  Once the page appears in the list, click **Generate Token**.
6.  **Copy this token**. This is your `FACEBOOK_PAGE_ACCESS_TOKEN`. Save it immediately.

### Step 3: Configure Webhooks
1.  Scroll down to the **Webhooks** section on the same page.
2.  Click **Add Callback URL**.
3.  **Callback URL**: `https://ai-sales-bot-api-production-a5d1.up.railway.app/api/v1/webhooks/inbound`
4.  **Verify Token**: `01012011`
5.  Click **Verify and Save**.
    *   *If this fails, ensure your backend is running and has the `WHATSAPP_VERIFY_TOKEN` set to `01012011`.*

### Step 4: Subscribe to Page Events
1.  After verifying, you will see your Page listed in the Webhooks section.
2.  Click **Add Subscriptions**.
3.  Select the following fields:
    *   `messages` (Required for receiving texts)
    *   `messaging_postbacks` (Required for button clicks)
    *   `messaging_optins` (Optional)
    *   `message_deliveries` (Optional)
    *   `message_reads` (Optional)
4.  Click **Save**.

### Step 5: App Review (For Production)
*   For testing, you (the admin) can message the page and it will work.
*   For public use, you must submit your app for **App Review**.
*   Go to **App Review** -> **Permissions and Features**.
*   Request advanced access for `pages_messaging`.

## 3. Testing
1.  Open Messenger and send a message to your connected Facebook Page.
2.  Check your backend logs or the application "Messages" page.
3.  You should see the message appear!
