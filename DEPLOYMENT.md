# Saber Deployment Guide

Deploying the Saber BldgAuditTool:
- **Backend** (`API's/` + `BldgAuditToolSimple_v1/`) → `saber-backend.colorado.edu`
- **Frontend** (`client/`) → Vercel

---

## Directory Structure on Server

```
/opt/saber/
├── API's/                      ← FastAPI app (main.py)
├── BldgAuditToolSimple_v1/     ← Python analysis engine (imported by main.py)
├── requirements.txt
├── uploads/                    ← persistent user uploads (created manually)
└── venv/                       ← Python virtual environment
```

---

# Part A — Backend on saber-backend.colorado.edu

## Prerequisites — UCB VPN

You must be on UCB VPN before you can SSH into the server.

1. Download Cisco Secure Client for Mac:
   ```
   https://cuservices.colorado.edu/vpn/download/secureclient-macos.pkg
   ```
2. Open the `.pkg` and install it
3. Open **Cisco Secure Client**
4. Enter server address: `vpn.colorado.edu`
5. Login with your **IdentiKey username and password**
6. Approve the **Duo MFA** push on your phone

VPN help: http://oit.colorado.edu/vpn  
OIT support: 303-735-4357 or oithelp@colorado.edu

---

## Step A1 — SSH into the server

```bash
ssh rapa4019@saber-backend.colorado.edu
```

- First time: type `yes` when asked about the host fingerprint
- Enter your IdentiKey password (cursor won't move — that's normal)

You should land at `[rapa4019@saber-backend ~]$`

---

## Step A2 — Get sudo access

The server runs **Red Hat Enterprise Linux 9.7**. You need sudo to install packages.

1. Go to https://mygroups.colorado.edu
2. Login with your IdentiKey
3. Under **Groups I manage**, click **CS-SG-VI CEAE SABER_SUDOERS**
4. Click the **Members** tab
5. Click **+ Add members** and add your IdentiKey
6. Log out of the server and back in:
   ```bash
   exit
   ssh rapa4019@saber-backend.colorado.edu
   ```
7. Test sudo works:
   ```bash
   sudo whoami
   # should print: root
   ```

> **Note:** Group changes in mygroups.colorado.edu can take 15–30 minutes to sync to the server. If sudo still fails after re-logging in, wait and try again. If it still fails after 30 minutes, email Adam Zheng to grant sudo manually.

---

## Step A3 — Install system packages

> **Important:** This server uses `dnf` (Red Hat), not `apt` (Ubuntu/Debian).

```bash
sudo dnf update -y
```

RHEL 9 does not include Python 3.12 by default. Enable EPEL + CRB repos first, then install:

```bash
sudo dnf install -y epel-release
sudo dnf config-manager --set-enabled crb
sudo dnf install -y python3.12 python3-pip nginx git rsync curl
```

> Note: `python3.12-venv` does not exist as a separate package on RHEL 9 — venv is bundled inside `python3.12`. Just use `python3.12 -m venv`.

Verify:
```bash
python3.12 --version    # Python 3.12.x
nginx -v                # nginx version
```

If Python 3.12 is still unavailable, use Python 3.11 (ships with RHEL 9 AppStream):
```bash
sudo dnf install -y python3.11 python3-pip nginx git rsync curl
python3.11 --version
```

Then substitute `python3.11` for `python3.12` in all commands below.

---

## Step A4 — Upload code from your Mac

**Open a new terminal tab on your Mac** (keep the SSH session open in another tab).

Run this rsync from your Mac — it uploads both the API and the analysis engine together:

```bash
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '.next' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'client' \
  --exclude 'Projects/*/Results' \
  /Users/raj/CUB/Saber/ \
  rapa4019@saber-backend.colorado.edu:/opt/saber/
```

**Switch back to your SSH tab** and verify:
```bash
ls /opt/saber/
```

You must see both:
```
API's    BldgAuditToolSimple_v1    requirements.txt    start.sh ...
```

Verify the critical files:
```bash
ls "/opt/saber/API's/"
ls /opt/saber/BldgAuditToolSimple_v1/BldgAuditToolPackage/
```

---

## Step A5 — Create Python virtual environment

```bash
cd /opt/saber
```
```bash
python3.12 -m venv venv    # venv module is built-in; no separate package needed
```
```bash
source venv/bin/activate
```

Your prompt now shows `(venv)`. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This takes **3–8 minutes**. If you see build errors for `scipy` or `numpy`:
```bash
sudo dnf install -y python3-devel gcc gcc-gfortran openblas-devel
pip install -r requirements.txt   # retry
```

Verify everything installed:
```bash
python3 -c "import fastapi, uvicorn, pandas, matplotlib, scipy, sklearn; print('all OK')"
```

---

## Step A6 — Test the app manually

```bash
cd "/opt/saber/API's"
uvicorn main:app --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

In a **second SSH tab**, test:
```bash
curl http://127.0.0.1:8000/list-projects
```

Expected: JSON like `{"projects":["LakewoodTestCase", ...]}`. Press `Ctrl+C` to stop.

---

## Step A7 — Create uploads directory and service user

```bash
sudo mkdir -p /opt/saber/uploads
sudo useradd --system --no-create-home --shell /bin/false saberapp
# Ownership model: rapa4019 owns the tree (so future `rsync` deploys can write it),
# group saberapp + group-write + setgid so the service (User=saberapp) can still create
# its output files. See "Update backend after a code change" — keep this model on every
# deploy; do NOT chown the tree to saberapp:saberapp or `rsync` will fail with EACCES.
sudo chown -R rapa4019:saberapp /opt/saber
sudo chmod -R g+w /opt/saber
sudo find /opt/saber -type d -exec chmod g+s {} \;
```

---

## Step A8 — Create the systemd service

```bash
sudo nano /etc/systemd/system/saber-backend.service
```

Paste **exactly**:

```ini
[Unit]
Description=Saber BldgAuditTool FastAPI Backend
After=network.target

[Service]
Type=simple
User=saberapp
Group=saberapp
WorkingDirectory=/opt/saber/API's
ExecStart=/opt/saber/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=UPLOADS_DIR=/opt/saber/uploads
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable saber-backend
sudo systemctl start saber-backend
```

Check it's running:
```bash
sudo systemctl status saber-backend
# Must show: Active: active (running)
```

If it shows `failed`, check the logs:
```bash
sudo journalctl -u saber-backend -n 50 --no-pager
```

Test it's responding:
```bash
curl http://127.0.0.1:8000/list-projects
```

---

## Step A9 — Configure nginx as reverse proxy

```bash
sudo nano /etc/nginx/conf.d/saber.conf
```

> **Note:** Red Hat nginx uses `conf.d/`, not `sites-available/sites-enabled/`.

Paste:

```nginx
server {
    listen 80;
    server_name saber-backend.colorado.edu;

    # Allow pkl and CSV uploads up to 50MB
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Analysis runs take 30-90 seconds — prevent nginx timeout
        proxy_read_timeout    300s;
        proxy_connect_timeout  10s;
        proxy_send_timeout    300s;
    }
}
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

Test config and start nginx:
```bash
sudo nginx -t
# Must say: syntax is ok / test is successful
```

> **SELinux note (RHEL 9):** Files copied from your home directory retain the wrong SELinux context and nginx will refuse to read them with "Permission denied". Fix both the conf file and the service file after moving them:
> ```bash
> sudo restorecon /etc/nginx/conf.d/saber.conf
> sudo restorecon /etc/systemd/system/saber-backend.service
> ```
> Also, SELinux blocks nginx from proxying to localhost by default. Enable it once:
> ```bash
> sudo setsebool -P httpd_can_network_connect 1
> ```

```bash
sudo systemctl enable --now nginx
```

Open the firewall for HTTP/HTTPS:
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

Test from your Mac terminal (not SSH):
```bash
curl http://saber-backend.colorado.edu/list-projects
```

---

## Step A10 — Enable HTTPS (required for Vercel → backend calls)

Browsers block HTTP calls from HTTPS pages. Since Vercel is HTTPS, the backend must also be HTTPS.

```bash
sudo dnf install -y certbot python3-certbot-nginx
sudo certbot --nginx -d saber-backend.colorado.edu
```

Certbot will ask:
1. Your email — enter it
2. Agree to terms — type `Y`
3. Redirect HTTP → HTTPS — choose `2`

Verify:
```bash
curl https://saber-backend.colorado.edu/list-projects
```

Check auto-renewal works:
```bash
sudo certbot renew --dry-run
```

---

# Part B — Frontend on Vercel

## Step B1 — Push code to GitHub

Check if a remote already exists:
```bash
git remote -v
```

If not, create a GitHub repo and push:
```bash
git remote add origin https://github.com/<your-username>/saber.git
git branch -M main
git push -u origin main
```

> `.env.local` is in `.gitignore` and will NOT be pushed — the API keys stay local and are added to Vercel separately.

---

## Step B2 — Import project on Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Click **Import Git Repository** → select your GitHub repo
3. **Change the Root Directory** to `client`
   - Click **Edit** next to Root Directory → type `client` → **Continue**
4. Framework Preset should auto-detect as **Next.js** — leave it

---

## Step B3 — Set environment variables on Vercel

Before clicking Deploy, add these under **Environment Variables**:

| Name | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://saber-backend.colorado.edu` |
| `ANTHROPIC_API_KEY` | *(copy from your local `client/.env.local`)* |

- `NEXT_PUBLIC_API_URL` — used by the browser to call the FastAPI backend
- `ANTHROPIC_API_KEY` — used server-side by the `/api/chat` route (Vercel keeps it secret)

---

## Step B4 — Deploy

Click **Deploy**. Vercel will build and deploy in ~2 minutes. You'll get a URL like `saber-xxxx.vercel.app`.

---

## Step B5 — Test end-to-end

1. Open your Vercel URL in the browser
2. Step 1: Upload a `.pkl` file from `BldgAuditToolSimple_v1/Projects/LakewoodTestCase/`
3. Check DevTools → Network: request should go to `https://saber-backend.colorado.edu/upload-pkl` and return 200
4. Try the chatbot — it should stream a response
5. Step 11 (Analysis): click Run Analysis — calls the UCB server, takes ~30 seconds

---

# Ongoing Maintenance

## Update backend after a code change

> **Ownership model.** `/opt/saber` is owned by **`rapa4019`** (so your `rsync` can write
> it) with group **`saberapp`** and group-write + setgid on directories (so the service,
> which runs as `saberapp`, can still create its output files — `Projects/.../Results/`,
> etc.). Do **not** `chown` the tree to `saberapp:saberapp` — that locks `rapa4019` out of
> the next `rsync`. The post-rsync command below re-applies this model and is idempotent.

**1. From your Mac** — sync the backend (excludes deps, build output, git history, and the
frontend, which deploys separately via Vercel):
```bash
rsync -avz --progress \
  --exclude 'node_modules' --exclude '.next' --exclude 'venv' \
  --exclude '__pycache__' --exclude '.git' --exclude 'client' \
  /Users/raj/CUB/Saber/ \
  rapa4019@saber-backend.colorado.edu:/opt/saber/
```
`rsync` has no `--delete`, so it only adds/updates files — nothing server-side is removed.

**2. On the server** — re-apply ownership/perms, restart, and confirm it came back up
(`-t` lets `sudo` prompt for its password):
```bash
ssh -t rapa4019@saber-backend.colorado.edu '
  sudo chown -R rapa4019:saberapp /opt/saber &&
  sudo chmod -R g+w /opt/saber &&
  sudo find /opt/saber -type d -exec chmod g+s {} \; &&
  sudo systemctl restart saber-backend &&
  sudo systemctl status saber-backend --no-pager
'
```
Look for `Active: active (running)`. Then watch a request go through with
`sudo journalctl -u saber-backend -f` while you exercise the app.

> **First time only / if `rsync` reports `Permission denied`.** The tree is currently owned
> by `rapa4019`. If it ever reverts to `saberapp` (or another user), take ownership before
> the first sync: `ssh -t rapa4019@saber-backend.colorado.edu 'sudo chown -R rapa4019:saberapp /opt/saber'`.

> **Note on `saberapp` group membership.** The group-write model only works if the service
> user `saberapp` is a member of the `saberapp` group. Verify with `id saberapp` (the
> `groups=` list must contain `saberapp`). If not: `sudo usermod -aG saberapp saberapp`.

## Update frontend after a code change

```bash
git add .
git commit -m "your message"
git push origin main
# Vercel auto-deploys on every push to main
```

## Useful server commands

```bash
# View live backend logs
sudo journalctl -u saber-backend -f

# Restart backend
sudo systemctl restart saber-backend

# Check backend status
sudo systemctl status saber-backend

# Check disk usage of uploads
du -sh /opt/saber/uploads/

# Check what's using port 8000
sudo ss -tlnp | grep 8000

# Renew SSL certificate (runs automatically, but can be done manually)
sudo certbot renew
```

---

# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| SSH hangs with no output | Not on UCB VPN | Connect to `vpn.colorado.edu` first |
| `not in the sudoers file` | Group sync delay | Wait 15–30 min after adding to SABER_SUDOERS, then re-login |
| `502 Bad Gateway` | uvicorn not running | `sudo systemctl restart saber-backend` |
| `CORS` error in browser | Wrong API URL | Check `NEXT_PUBLIC_API_URL` on Vercel |
| `413 Request Entity Too Large` | nginx size limit | Verify `client_max_body_size 50M` in nginx config |
| Analysis request times out | nginx timeout too short | Verify `proxy_read_timeout 300s` in nginx config |
| `ModuleNotFoundError: BldgAuditToolPackage` | Analysis engine missing | Re-run rsync, check `ls /opt/saber/BldgAuditToolSimple_v1/` |
| Certbot fails | DNS not resolving | Wait for DNS to propagate, then retry |
| Mixed content error in browser | Backend still on HTTP | Complete Step A10 (HTTPS/certbot) |
