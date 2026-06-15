# Deploying to InfinityFree: A Comprehensive Guide

## Can I upload this website to InfinityFree?

**Short Answer:** Partially. You can **only** upload the **Frontend (React)** to InfinityFree. The **Backend (Python)** and the **WhatsApp Gateway (Go/Node.js)** cannot be hosted there.

### Why?
InfinityFree only supports static files (HTML, CSS, JavaScript) and **PHP** on the server-side, along with MySQL databases.
Your project has:
- **Frontend (React/Vite)**: ✔️ Supported (Once built into static files).
- **Backend (Python/FastAPI/Flask)**: ❌ Not Supported (InfinityFree doesn't run Python apps).
- **WhatsApp Gateway (Node/Go)**: ❌ Not Supported (InfinityFree doesn't run Node.js or Go).

If you want to use InfinityFree, you must host the **frontend on InfinityFree** and host the **backend and database on another free platform** (like Render or Railway).

---

## Guide: How to Upload Your Frontend to InfinityFree

To upload the frontend, you need to compile your React code into static HTML/JS/CSS files and upload them to your InfinityFree server.

### Step 1: Configure the API URL
Since your backend cannot be hosted on InfinityFree, you need to deploy your backend to a service like Render, Railway, or Heroku first. 
Once your backend is live (e.g., `https://my-backend.onrender.com`), you need to tell your frontend where to find it.

1. Open `frontend/.env` (or `.env.local`).
2. Set the API URL to your live backend server:
   ```env
   VITE_API_URL=https://my-backend.onrender.com
   ```

### Step 2: Build the Frontend
You need to convert the React project into static files.

1. Open your terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies (if you haven't already):
   ```bash
   npm install
   ```
3. Run the build command:
   ```bash
   npm run build
   ```
This will create a new folder called **`dist`** inside the `frontend` directory. The contents of this `dist` folder are what you will upload to InfinityFree.

### Step 3: Setup InfinityFree
1. Log in to [InfinityFree](https://infinityfree.com/).
2. Create an account and set up a new hosting account (subdomain).
3. Once the account is created, go to the **Control Panel**.
4. Inside the Control Panel, look for the **Online File Manager** (or note down the FTP credentials if you prefer using FileZilla).

### Step 4: Upload the Files
1. Open the **Online File Manager** in InfinityFree.
2. Open the **`htdocs`** folder. (This is the public folder where your website files must go).
3. **Delete** any default files inside `htdocs` (like `index2.html`).
4. On your computer, open the `frontend/dist` folder you created in Step 2.
5. Upload **all the contents** of the `dist` folder directly into the `htdocs` folder on InfinityFree. (Do not upload the `dist` folder itself, only the files and folders *inside* it).

### Step 5: Setting up Routing (Important for React)
Since React handles its own routing (like going to `/login` or `/dashboard`), InfinityFree needs to know how to handle direct links to those pages.

1. In the `htdocs` folder on InfinityFree, create a new file named exactly: `.htaccess`
2. Edit the `.htaccess` file and add the following code:
   ```apache
   <IfModule mod_rewrite.c>
     RewriteEngine On
     RewriteBase /
     RewriteRule ^index\.html$ - [L]
     RewriteCond %{REQUEST_FILENAME} !-f
     RewriteCond %{REQUEST_FILENAME} !-d
     RewriteRule . /index.html [L]
   </IfModule>
   ```
3. Save the file. This ensures that if someone visits `yourwebsite.com/login`, the server doesn't throw a 404 error but instead loads the React app.

### Summary of Deployment Structure
- **Frontend**: Hosted on InfinityFree (serving static files).
- **Backend (Python)**: Hosted on Render / Railway.
- **WhatsApp Gateway**: Hosted on Render / Railway.
- **Database**: PostgreSQL (hosted on Railway or Supabase) OR MySQL (provided by InfinityFree, though your backend might need reconfiguration if it's set up for PostgreSQL).

If you want a simpler deployment where everything is hosted together, you should deploy the entire stack on **Railway** or **Render**, as they natively support Docker, Python, Node.js, and React.
