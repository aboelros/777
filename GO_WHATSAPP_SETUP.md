# Go WhatsApp Web Multi-Device Setup Guide

This guide explains how to deploy and configure the `aldinokemal/go-whatsapp-web-multidevice` gateway for use with AI Sales Commander.

## 1. Deploy on Railway

1.  **Create a new Service** in your Railway project.
2.  Select **Docker Image**.
3.  Enter the image name: `aldinokemal/go-whatsapp-web-multidevice:latest`
4.  **Variables**: Add the following environment variables:
    *   `PORT`: `3000` (The container listens on 3000 by default)
    *   `AppPort`: `3000` (Optional, but good to be explicit)
    *   `BasicAuthPassword`: `your-secure-password` (Optional, for security)

5.  **Deploy** the service.
6.  **Public Domain**: Go to Settings -> Networking and generate a domain (e.g., `go-whatsapp-production.up.railway.app`).

## 2. Connect in AI Sales Commander

1.  Go to **Integrations** page.
2.  Click **Connect** on the WhatsApp card.
3.  Select **Go WhatsApp (Multi-Device)** from the dropdown.
4.  **Base URL**: Enter your Railway domain (e.g., `https://go-whatsapp-production.up.railway.app`).
5.  **Basic Auth Password**: Enter the password you set in `BasicAuthPassword` (if any).
6.  **Session Name**: You can leave this as `default` or enter a name.
7.  Click **Connect**.

## 3. Scan QR Code

1.  After connecting, a QR code should appear.
2.  Open WhatsApp on your phone -> Linked Devices -> Link a Device.
3.  Scan the QR code.

## 4. Webhook Configuration (Optional but Recommended)

To receive incoming messages, you need to configure the webhook in the Go WhatsApp container.

1.  **In Railway**, add/update variables:
    *   `WebhookURL`: `https://your-backend-url.com/api/v1/webhooks/whatsapp/go_whatsapp` (You need to verify the correct webhook endpoint in your backend)
    
    *Note: The current backend implementation might need a specific webhook endpoint for Go WhatsApp if the payload structure is different from WPPConnect. The adapter attempts to normalize it.*

## Troubleshooting

*   **Logs**: Check the logs in Railway for the Go WhatsApp service.
*   **401 Unauthorized**: Make sure the Basic Auth Password matches.
*   **Connection Refused**: Ensure the `PORT` variable is set correctly to `3000`.
