# WPPConnect Server Setup Guide

This guide explains how to deploy and configure WPPConnect Server for use with your AI Sales Agent. WPPConnect is a lightweight, multi-session WhatsApp gateway.

## 1. Deploy WPPConnect on Railway

1.  **Log in to Railway** and click **"New Project"**.
2.  Select **"Deploy from Docker Image"**.
3.  Enter the image name: `wppconnect/server-cli:latest` and press Enter.
4.  Click on the newly created service to open its settings.
5.  Go to the **"Variables"** tab and add the following:
    *   `PORT`: `8080` (Default port)
    *   `SECRET_KEY`: `my-secret-key-123` (Optional, for authentication)
    *   `WEBHOOK_URL`: (Leave empty, we will configure it via API if needed)

6.  **Generate a Domain:**
    *   Go to the **"Settings"** tab.
    *   Under "Networking", click **"Generate Domain"**.
    *   Copy this domain (e.g., `wppconnect-production.up.railway.app`).

## 2. Connect to AI Sales Agent

1.  Open your **AI Sales Agent Dashboard**.
2.  Go to the **Integrations** page.
3.  Click **Connect** on the WhatsApp integration card.
4.  Select **WPPConnect Server** from the dropdown.
5.  Fill in the details:
    *   **WPPConnect Base URL:** Your Railway URL (e.g., `https://wppconnect-production.up.railway.app`).
    *   **Secret Key:** The `SECRET_KEY` you set in step 1 (if any).
    *   **Session Name:** Choose a name for this connection (e.g., `shop1`).
6.  Click **Connect**.

## 3. Scan QR Code

1.  After connecting, a **QR Code** will appear on the screen.
2.  Open **WhatsApp** on your phone.
3.  Go to **Settings > Linked Devices > Link a Device**.
4.  Scan the QR code.

## 4. Done!

Your WhatsApp number is now connected.
