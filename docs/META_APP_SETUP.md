# Meta App Setup Guide

This guide explains how to create and configure a Meta App to work with the AI Sales Commander.

## 1. Create a Meta App

1.  Go to [developers.facebook.com](https://developers.facebook.com/).
2.  Click **My Apps** -> **Create App**.
3.  Select **Other** (or "Business" if available and appropriate for your use case).
4.  Select **Business** as the app type.
5.  Enter your **App Name** and **Contact Email**.
6.  Select your **Business Account** (optional but recommended).
7.  Click **Create App**.

## 2. Add Products

You need to add the following 5 products to your app:

### 1️⃣ Facebook Login for Business
*   Click **Set Up** on the "Facebook Login for Business" card.
*   **Settings**:
    *   **Valid OAuth Redirect URIs**: Add your callback URL.
        *   For local development: `http://localhost:3000/integrations/meta/callback` (or wherever your frontend handles the return).
        *   For production: `https://your-domain.com/integrations/meta/callback`.

### 2️⃣ Webhooks
*   Click **Set Up** on the "Webhooks" card.
*   **Subscribe to objects**:
    *   Select **Page** -> Subscribe to `messages`, `messaging_postbacks`, `feed`.
    *   Select **Instagram** -> Subscribe to `comments`, `mentions`, `story_insights`.
    *   Select **WhatsApp Business Account** -> Subscribe to `messages`.
*   **Callback URL**: `https://your-domain.com/api/v1/webhooks/inbound` (Note: Facebook requires HTTPS. For localhost, use a tunnel like Ngrok).
*   **Verify Token**: Enter a secure string (e.g., `my_secure_verify_token`). You will need to set this in your backend environment variables (`META_VERIFY_TOKEN`).

### 3️⃣ Messenger
*   Click **Set Up** on the "Messenger" card.
*   **Access Tokens**: Generate a Page Access Token for the Facebook Page you want to manage.
*   **Webhooks**: Ensure your Webhook subscription is linked to this Page.

### 4️⃣ Instagram Graph API
*   Click **Set Up** on the "Instagram Graph API" card.
*   **Tools**: Use the "API Setup with Facebook Login" or "User Token Generator" if needed manually, but the "Facebook Login" product handles the permissions.

### 5️⃣ WhatsApp
*   Click **Set Up** on the "WhatsApp" card.
*   **API Setup**:
    *   Get your **Temporary Access Token** (for testing).
    *   Get your **Phone Number ID**.
    *   Get your **WhatsApp Business Account ID**.
*   **Configuration**:
    *   Set the **Callback URL** and **Verify Token** (same as Webhooks product).

## 3. App Settings

1.  Go to **App Settings** -> **Basic**.
2.  Copy your **App ID** and **App Secret**.
3.  Add these to your project's environment variables or Integration settings.

## 4. Environment Variables

Ensure your backend has these variables set (or configured in the Integration UI):

```env
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_VERIFY_TOKEN=your_verify_token
```
