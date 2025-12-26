# MentorBot RAG Application Deployment Guide

**Deploying the MentorBot Streamlit Application on Server**

This guide documents the deployment process for the MentorBot application at `https://rag.shudizhao.com`.

---

## Prerequisites

Before starting, ensure you have:

- Root/sudo access to your server
- Apache2 and Docker already installed and running
- Domain `shudizhao.com` managed by Cloudflare
- ISPConfig for web server management (if applicable)
- Git repository for the MentorBot application
- OpenAI API Key
- `requirements.txt` file with all Python dependencies

---

## Step 1: Choose Subdomain & Port

For this deployment, the following configuration is used:

- **Subdomain:** `rag.shudizhao.com`
- **Port:** 8503
- **Container Name:** `mentorbot-rag`
- **Application Directory:** `/var/www/mentorbot`
- **Git Repository:** `https://github.com/Shudi-Zhao/mentorbot.git`

---

## Step 2: Configure DNS in Cloudflare

1. **Login to Cloudflare**
   - Go to [dash.cloudflare.com](https://dash.cloudflare.com)
   - Sign in to your account

2. **Access Domain Management**
   - Select your domain `shudizhao.com`

3. **Add DNS Record**
   - Click on "DNS" in the left sidebar
   - Click "Add record"
   - Configure:
     - **Type:** A Record
     - **Name:** `rag`
     - **IPv4 address:** `YOUR_SERVER_IP_ADDRESS`
     - **Proxy status:** Proxied (orange cloud) - enables SSL, CDN, DDoS protection
     - **TTL:** Auto

4. **Save**
   - Click "Save"
   - DNS propagation typically takes 1-5 minutes with Cloudflare

5. **Configure SSL/TLS**
   - Go to **SSL/TLS** → **Overview**
   - Set encryption mode to **Full** or **Full (strict)**
   - Go to **SSL/TLS** → **Edge Certificates**
   - Enable **Always Use HTTPS**

---

## Step 3: Set Up Application Directory

Create the directory and clone the repository:

```bash
# Create directory for the MentorBot app
sudo mkdir -p /var/www/mentorbot
sudo chown $USER:www-data /var/www/mentorbot
cd /var/www/mentorbot

# Clone your repository (use SSH or HTTPS with token on server)
git clone https://github.com/Shudi-Zhao/mentorbot.git .
# OR with SSH: git clone git@github.com:Shudi-Zhao/mentorbot.git .

# Verify files are present
ls -la
# You should see: requirements.txt, app/, Dockerfile, docker-compose.yml, deploy.sh
```

---

## Step 4: Configure Environment Variables

Create `.env` file with your configuration:

```bash
cd /var/www/mentorbot

# Create .env file
cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Override default settings
# OPENAI_MODEL=gpt-3.5-turbo
# EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
# DEFAULT_CHUNK_SIZE=512
# DEFAULT_CHUNK_OVERLAP=50
# DEFAULT_TOP_K=5

# Auto-cleanup settings (for portfolio/demo deployment)
ENABLE_AUTO_CLEANUP=true
MAX_FILE_AGE_HOURS=1.0           # Delete files older than 1 hour
MAX_STORAGE_MB=100               # Maximum total storage (100MB)
MAX_FILE_SIZE_MB=10              # Maximum file size per upload (10MB)
CLEANUP_INTERVAL_MINUTES=30      # Run cleanup every 30 minutes
EOF

# Edit and add your actual OpenAI API key
nano .env
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

---

## Step 5: Deployment Files Overview

Your deployment includes the following files:

### Dockerfile

**Purpose:** Creates a containerized environment with Python 3.11, installs all dependencies, and sets up the Streamlit server to run on port 8503.

**Key Features:**
- Uses Python 3.11-slim for a lightweight image
- Installs system dependencies (build tools, curl, git)
- Creates persistent directories for data, uploads, and logs
- Configures Streamlit to run on port 8503
- Sets the browser server address to `rag.shudizhao.com`
- Includes health check for container monitoring
- Copies demo content for quick testing

### docker-compose.yml

**Purpose:** Defines the service configuration, port mapping, environment variables, and persistent volumes for the application.

**Key Features:**
- Maps port 8503 from container to host
- Sets `restart: unless-stopped` for automatic recovery after server reboot
- Mounts local `data/uploads`, `data/chroma_db`, and `logs` directories for persistence
- Configures environment variables for Streamlit and OpenAI
- Includes health checks every 30 seconds
- Creates isolated network for the application

### deploy.sh

**Purpose:** Provides commands to start, stop, restart, update, and monitor the application.

**Available Commands:**
- `./deploy.sh start` - Start the application
- `./deploy.sh stop` - Stop the application
- `./deploy.sh restart` - Restart the application
- `./deploy.sh update` - Pull latest code from Git and rebuild
- `./deploy.sh logs` - View real-time application logs
- `./deploy.sh status` - Check application status
- `./deploy.sh rebuild` - Rebuild containers from scratch

**Key Features:**
- Color-coded output for easy reading
- Automatic health checks after deployment
- Git integration for easy updates
- Comprehensive error handling
- Status monitoring and logging

---

## Step 6: Configure ISPConfig (If Using ISPConfig)

1. **Access ISPConfig**
   - Open `https://your-server-ip:8080`
   - Login with admin credentials

2. **Create New Website**
   - Navigate to **Sites → Website**
   - Click **"Add new Website"**
   - Fill in details:
     - **Domain:** `rag.shudizhao.com`
     - **Auto-Subdomain:** None
     - **SSL:** Yes
     - **Let's Encrypt SSL:** Yes (or use Cloudflare Origin Certificate)
     - **Python:** Yes

3. **Configure Apache Directives**
   - Click on **"Apache Directives"** tab
   - Paste the following configuration:

```apache
<Proxy *>
    Order allow,deny
    Allow from all
</Proxy>

ProxyPreserveHost On
ProxyPass / http://127.0.0.1:8503/
ProxyPassReverse / http://127.0.0.1:8503/

# WebSocket support for Streamlit
RewriteEngine On
RewriteCond %{HTTP:Upgrade} =websocket [NC]
RewriteRule /(.*) ws://127.0.0.1:8503/$1 [P,L]
RewriteCond %{HTTP:Upgrade} !=websocket [NC]
RewriteRule /(.*) http://127.0.0.1:8503/$1 [P,L]

# Headers for proper proxying
RequestHeader set X-Forwarded-Proto "https"
RequestHeader set X-Forwarded-Port "443"

# Security headers
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"

# CORS headers (if needed)
Header always set Access-Control-Allow-Origin "*"
Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
```

4. **Save Configuration**
   - Click **"Save"**
   - Wait 1-2 minutes for configuration to apply

---

## Step 7: Manual Apache/Nginx Configuration (Alternative)

If not using ISPConfig, configure your web server manually:

### Apache Configuration

Create `/etc/apache2/sites-available/rag.shudizhao.com.conf`:

```apache
<VirtualHost *:80>
    ServerName rag.shudizhao.com

    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>

<VirtualHost *:443>
    ServerName rag.shudizhao.com

    # SSL Configuration (if not using Cloudflare)
    # SSLEngine on
    # SSLCertificateFile /etc/ssl/certs/your-cert.crt
    # SSLCertificateKeyFile /etc/ssl/private/your-key.key

    # Proxy to Streamlit app
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8503/
    ProxyPassReverse / http://127.0.0.1:8503/

    # WebSocket support for Streamlit
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} =websocket [NC]
    RewriteRule /(.*) ws://127.0.0.1:8503/$1 [P,L]
    RewriteCond %{HTTP:Upgrade} !=websocket [NC]
    RewriteRule /(.*) http://127.0.0.1:8503/$1 [P,L]

    # Headers
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
```

Enable the site:
```bash
sudo a2ensite rag.shudizhao.com.conf
sudo a2enmod proxy proxy_http proxy_wstunnel rewrite headers ssl
sudo apache2ctl configtest
sudo systemctl reload apache2
```

### Nginx Configuration (Alternative)

Create `/etc/nginx/sites-available/rag.shudizhao.com`:

```nginx
server {
    listen 80;
    server_name rag.shudizhao.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rag.shudizhao.com;

    # SSL Configuration (if not using Cloudflare)
    # ssl_certificate /etc/ssl/certs/your-cert.crt;
    # ssl_certificate_key /etc/ssl/private/your-key.key;

    location / {
        proxy_pass http://localhost:8503;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/rag.shudizhao.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 8: Deploy the Application

Build and start the application:

```bash
cd /var/www/mentorbot

# Make deploy script executable (if not already)
chmod +x deploy.sh

# Start the application
./deploy.sh start
```

Verify deployment:

```bash
# Check container status
docker ps

# You should see the container running:
# mentorbot-rag (port 8503)

# Check logs
./deploy.sh logs
```

Test the deployment:

1. **Test locally on server:**
   ```bash
   curl http://localhost:8503
   ```

2. **Test from browser:**
   - Open browser
   - Go to: `https://rag.shudizhao.com`
   - Verify:
     - SSL certificate is valid (green padlock)
     - Application loads correctly
     - Can upload documents and ask questions
     - Demo content works

---

## Managing the Application

### Check Status
```bash
cd /var/www/mentorbot
./deploy.sh status
```

### Update Application
```bash
cd /var/www/mentorbot
./deploy.sh update
```
This will:
1. Pull latest code from Git
2. Rebuild Docker container
3. Restart the application
4. Verify it's running

### View Logs
```bash
cd /var/www/mentorbot
./deploy.sh logs
```

### Restart Application
```bash
cd /var/www/mentorbot
./deploy.sh restart
```

### Stop Application
```bash
cd /var/www/mentorbot
./deploy.sh stop
```

### Rebuild from Scratch
```bash
cd /var/www/mentorbot
./deploy.sh rebuild
```

### Monitor Resources
```bash
# Real-time container stats
docker stats mentorbot-rag

# System resources
htop
```

---

## File Structure

Your complete deployment structure:

```
/var/www/mentorbot/
├── app/                        # Application code
│   ├── main.py                 # Main Streamlit application
│   ├── config.py               # Configuration settings
│   ├── cleanup.py              # Auto-cleanup manager
│   ├── parsers/                # Document parsers
│   ├── chunking/               # Text chunking logic
│   ├── embeddings/             # Embedding service
│   ├── vectordb/               # ChromaDB integration
│   └── qa/                     # Q&A service
├── demo_content/               # Demo onboarding content
│   ├── data_scientist_onboarding.md
│   └── sample_questions.md
├── data/                       # Persistent data storage
│   ├── uploads/                # Uploaded files
│   └── chroma_db/              # Vector database
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build instructions
├── docker-compose.yml          # Service orchestration
├── deploy.sh                   # Deployment management script
├── deployment.md               # This file
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment file
├── .dockerignore               # Docker ignore patterns
└── .gitignore                  # Git ignore patterns
```

---

## Troubleshooting

### Cannot access rag.shudizhao.com

**Solution:**
```bash
# Check DNS
nslookup rag.shudizhao.com
dig rag.shudizhao.com

# Check if container is running
docker ps | grep mentorbot

# Check Apache/Nginx configuration
sudo apache2ctl configtest
# OR
sudo nginx -t

# Check logs
cd /var/www/mentorbot
./deploy.sh logs
```

### Container not starting

**Solution:**
```bash
# Check container logs
docker logs mentorbot-rag

# Check port availability
netstat -tulpn | grep 8503

# Check if .env file exists and has correct values
cat .env

# Rebuild from scratch
./deploy.sh rebuild
```

### SSL certificate issues

**With Cloudflare:**
- Ensure DNS is proxied (orange cloud)
- Set SSL/TLS mode to "Full" in Cloudflare dashboard
- Wait 5 minutes for changes to propagate

**With ISPConfig:**
```bash
# In ISPConfig, go to your site
# SSL tab → Force Update
# Wait 2-3 minutes

# Check Apache error logs
sudo tail -f /var/log/apache2/error.log
```

### Application shows 502 Bad Gateway

**Solution:**
```bash
# Check if container is running
docker ps | grep mentorbot

# If not running, start it
cd /var/www/mentorbot
./deploy.sh start

# Check if port 8503 is accessible
curl http://localhost:8503

# Check web server logs
sudo tail -f /var/log/apache2/error.log
# OR
sudo tail -f /var/log/nginx/error.log
```

### Out of memory errors

**Solution:**
```bash
# Check memory usage
free -h
docker stats

# Increase Docker memory limit in docker-compose.yml:
# Add under 'mentorbot' service:
#   deploy:
#     resources:
#       limits:
#         memory: 2G

# Restart
./deploy.sh restart
```

### ChromaDB persistence issues

**Solution:**
```bash
# Ensure data directories exist with correct permissions
sudo chown -R $USER:$USER /var/www/mentorbot/data
sudo chmod -R 755 /var/www/mentorbot/data

# Check volume mounts
docker inspect mentorbot-rag | grep Mounts -A 20

# Rebuild and restart
./deploy.sh rebuild
```

---

## Security Best Practices

1. **Environment Variables**
   - Never commit `.env` file to git
   - Keep OpenAI API key secure
   - Rotate API keys periodically

2. **File Permissions**
   ```bash
   # Set appropriate permissions
   sudo chown -R $USER:www-data /var/www/mentorbot
   sudo chmod 600 /var/www/mentorbot/.env
   sudo chmod +x /var/www/mentorbot/deploy.sh
   ```

3. **Firewall Configuration**
   ```bash
   # Only allow necessary ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable

   # Do NOT expose port 8503 externally
   # Access only through Apache/Nginx reverse proxy
   ```

4. **Regular Updates**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade

   # Update application
   cd /var/www/mentorbot
   ./deploy.sh update
   ```

5. **Monitoring**
   - Monitor logs regularly: `./deploy.sh logs`
   - Check disk space: `df -h`
   - Monitor container health: `docker ps`

---

## Auto-Cleanup Feature

MentorBot includes an auto-cleanup system to prevent abuse in demo deployments:

- **Time-based cleanup**: Deletes files older than configured hours
- **Storage limits**: Enforces maximum storage quota
- **Background scheduler**: Runs cleanup automatically
- **Manual reset**: Clear all data button in sidebar

Configure in `.env`:
```bash
ENABLE_AUTO_CLEANUP=true
MAX_FILE_AGE_HOURS=1.0
MAX_STORAGE_MB=100
MAX_FILE_SIZE_MB=10
CLEANUP_INTERVAL_MINUTES=30
```

---

## Quick Reference

**Application Details:**
- **URL:** https://rag.shudizhao.com
- **Directory:** /var/www/mentorbot
- **Port:** 8503 (internal)
- **Container:** mentorbot-rag
- **Git Repo:** https://github.com/Shudi-Zhao/mentorbot.git

**Common Commands:**
```bash
# Navigate to app directory
cd /var/www/mentorbot

# Update application
./deploy.sh update

# View logs
./deploy.sh logs

# Check status
./deploy.sh status

# Restart
./deploy.sh restart

# Stop
./deploy.sh stop

# Start
./deploy.sh start

# Rebuild from scratch
./deploy.sh rebuild
```

**Docker Commands:**
```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View logs
docker logs mentorbot-rag

# View real-time stats
docker stats mentorbot-rag

# Enter container shell
docker exec -it mentorbot-rag /bin/bash

# Remove stopped containers
docker-compose down
```

---

## Success!

Your MentorBot application is now live at **https://rag.shudizhao.com**

The deployment includes:
- SSL certificate (HTTPS) via Cloudflare
- Automatic container restart on failure
- Persistent data storage for uploads and vector database
- Easy update mechanism via Git
- Comprehensive logging
- Health monitoring
- Auto-cleanup for demo protection

To update the application in the future, simply run:
```bash
cd /var/www/mentorbot
./deploy.sh update
```

---

## Additional Resources

- **MentorBot GitHub:** https://github.com/Shudi-Zhao/mentorbot
- **Streamlit Docs:** https://docs.streamlit.io
- **Docker Docs:** https://docs.docker.com
- **Cloudflare Docs:** https://developers.cloudflare.com

---

**Deployment Date:** 2025-12-26
**Last Updated:** 2025-12-26
**Version:** 1.0
