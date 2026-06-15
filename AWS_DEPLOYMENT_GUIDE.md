# Deploying to AWS: A Comprehensive Guide

## Can I upload this entire website to AWS?

**Short Answer:** Yes, absolutely! 

Unlike InfinityFree, AWS (Amazon Web Services) is a full-fledged cloud provider. It can host your **Frontend (React)**, **Backend (Python)**, **WhatsApp Gateway (Go/Node)**, and **Database (PostgreSQL)** all in one place.

Since you already have a `docker-compose.yml` file in your project, deploying to AWS is relatively straightforward.

---

## AWS Free Tier
AWS offers a **Free Tier** for the first 12 months for new accounts. This includes:
- **750 hours/month of Amazon EC2** (`t2.micro` or `t3.micro` instance). This is enough to run one small server 24/7 for free.
- **30 GB of EBS Storage** (Hard drive space for your server).
- **Amazon RDS** (Optional free tier for a managed database).

*Note: A `t2.micro` instance has 1GB of RAM. If your application (Frontend + Backend + Database + WhatsApp Gateway) uses a lot of memory, it might be a bit tight, but it usually works for small-to-medium loads.*

---

## Recommended Approach: AWS EC2 with Docker Compose
The easiest way to deploy your entire stack on AWS is to create an **EC2 Instance** (a virtual server), install Docker, and run your `docker-compose.yml` file.

### Step 1: Create an AWS Account and Launch an EC2 Instance
1. Go to [aws.amazon.com](https://aws.amazon.com/) and create a free account.
2. Go to the **EC2 Dashboard** and click **Launch Instance**.
3. **Name**: Give your server a name (e.g., `MyApp-Server`).
4. **OS Image (AMI)**: Select **Ubuntu** (Ubuntu Server 24.04 LTS or 22.04 LTS). Make sure it says "Free tier eligible".
5. **Instance Type**: Select `t2.micro` or `t3.micro` (Free tier eligible).
6. **Key Pair**: Click "Create new key pair", name it (e.g., `my-aws-key`), and download the `.pem` file. **Keep this file safe; you need it to connect to your server!**
7. **Network Settings**: 
   - Check **Allow SSH traffic** from anywhere.
   - Check **Allow HTTP traffic from the internet**.
   - Check **Allow HTTPS traffic from the internet**.
8. **Storage**: You can increase it up to 30 GB for free.
9. Click **Launch Instance**.

### Step 2: Connect to Your Server
Once the instance is running, you need to connect to it using SSH.
1. Open your terminal.
2. Change the permissions of your downloaded key file (Mac/Linux only):
   ```bash
   chmod 400 my-aws-key.pem
   ```
3. Connect to the server using its Public IP address (found in the EC2 dashboard):
   ```bash
   ssh -i "my-aws-key.pem" ubuntu@YOUR_EC2_PUBLIC_IP
   ```

### Step 3: Install Docker and Docker Compose
Run these commands on your AWS server to install Docker:
```bash
# Update packages
sudo apt update -y

# Install Docker
sudo apt install docker.io -y

# Install Docker Compose
sudo apt install docker-compose-v2 -y

# Start Docker and enable it to run on startup
sudo systemctl start docker
sudo systemctl enable docker

# Give your user permission to run docker without "sudo"
sudo usermod -aG docker ubuntu
```
*(You may need to log out by typing `exit` and reconnect via SSH for the permission change to take effect).*

### Step 4: Upload Your Project to AWS
You need to get your code onto the server. You can either use Git or copy it directly.

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

**Option B: Copying files via SCP (Run this on your local computer)**
```bash
scp -i "my-aws-key.pem" -r "c:\Users\ARKAN STOER\Desktop\777" ubuntu@YOUR_EC2_PUBLIC_IP:/home/ubuntu/777
```

### Step 5: Configure Environment Variables
On your AWS server, navigate to your project folder and create your `.env` file:
```bash
cd your-project-folder
nano .env
```
Paste all your production environment variables (from your `COMPLETE_CONFIG.env` or `railway.env.example` files). Press `Ctrl+X`, then `Y`, then `Enter` to save.

**Important Frontend Change:** 
Make sure your frontend's `VITE_API_URL` in the `.env` file points to your EC2 Public IP address (e.g., `http://YOUR_EC2_PUBLIC_IP:8000`).

### Step 6: Start the Application
Run Docker Compose to build and start everything:
```bash
docker compose up -d --build
```

### Step 7: Access Your Website
- If your frontend runs on port `80`, you can access it by typing your EC2 Public IP in your browser: `http://YOUR_EC2_PUBLIC_IP`
- *Note: If your frontend runs on a specific port like `3000` or `5173`, you will need to open that port in the AWS EC2 Security Group settings (Inbound Rules).*

---

## Summary
- **Cost**: Free for 12 months (if you stay within the Free Tier limits).
- **Capability**: Can run your entire stack (Frontend, Backend, Database, Gateway).
- **Difficulty**: Moderate (Requires using the terminal and Linux commands).
- **Maintenance**: You manage the server (updates, security, etc.).

If you want an easier platform that manages the server for you (Platform as a Service), **Render** or **Railway** (which you already have guides for in your project) are the best alternatives, though their free tiers have stricter limits than AWS EC2.
