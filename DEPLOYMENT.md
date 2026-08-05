# Saber Deployment Guide — Azure

Deploying the Saber BldgAuditTool to the lab's Azure subscription:
- **Backend** (`API's/` + `BldgAuditToolSimple_v1/`) → Azure Web App `saber-api` (Docker container)
- **Frontend** (`client/`) → Azure Web App `saber-web` (Node 22)

Both apps share one **B3 Linux App Service plan** (~$53/mo) plus an Azure Container
Registry (Basic, ~$5/mo). The panel-sizer app can be added to the same plan later at
no extra cost.

App Service provides HTTPS automatically at `*.azurewebsites.net` — no nginx,
certbot, systemd, or VPN needed.

---

## Prerequisites

### Subscription access

The subscription is `azucob0ceaelbslw`, created by CU Research Computing
(rc-help@colorado.edu). Access is managed via Grouper groups:

- `azucob0ceaelbslw-OIT-SubscriptionContributor` — required to create/deploy resources
- `azucob0ceaelbslw-OIT-SubscriptionReader` — view only
- `azucob0ceaelbslw-OIT-SubscriptionBilling`

Nick Clements (nicholas.clements@colorado.edu) manages membership at
https://mygroups.colorado.edu. If `az group create` fails with an authorization
error, you are not in the Contributor group yet — ask Nick to add your IdentiKey.

Billing party: Kathleen.stutzman@colorado.edu.

### Azure CLI

```bash
brew install azure-cli          # if not installed
az login                        # sign in with your CU Office 365 account
az account show                 # must show name: azucob0ceaelbslw
```

If you have multiple subscriptions:
```bash
az account set --subscription azucob0ceaelbslw
```

---

# Part A — One-time infrastructure setup

```bash
az group create -n saber-rg -l westus3
az appservice plan create -n saber-plan -g saber-rg --sku B3 --is-linux
az acr create -n saberacr -g saber-rg --sku Basic --admin-enabled true
```

> ACR names are globally unique. If `saberacr` is taken, pick another (e.g.
> `saberacrcub`) and substitute it in every command below.

---

# Part B — Backend (`saber-api`)

## Step B1 — Build the container image

This uploads the repo and builds it **in the cloud** using the `Dockerfile` at
the repo root (which already handles the apostrophe in the `API's` folder name).
Run the whole command — `-r` is the registry, `-t` the image tag, and the final
argument is the path to build:

```bash
az acr build -r saberacr -t saber-api:latest /Users/raj/CUB/Saber
```

> If you named your registry something other than `saberacr`, check with
> `az acr list -g saber-rg -o table` and substitute the name.

Takes ~5 minutes the first time (installs scipy/numpy/matplotlib).

## Step B2 — Create the Web App

```bash
az webapp create -n saber-api -g saber-rg -p saber-plan --container-image-name saberacr.azurecr.io/saber-api:latest
```

Then give the app credentials to pull from the registry — `az webapp create` does
**not** set these up, and without them the app serves 503 because the image pull
is rejected. Run these three lines separately:

```bash
ACR_USER=$(az acr credential show -n saberacr --query username -o tsv)
ACR_PASS=$(az acr credential show -n saberacr --query "passwords[0].value" -o tsv)
az webapp config container set -n saber-api -g saber-rg --container-image-name saberacr.azurecr.io/saber-api:latest --container-registry-url https://saberacr.azurecr.io --container-registry-user "$ACR_USER" --container-registry-password "$ACR_PASS"
```

Verify credentials took — the output must list `DOCKER_REGISTRY_SERVER_URL` and
`DOCKER_REGISTRY_SERVER_USERNAME`:

```bash
az webapp config container show -n saber-api -g saber-rg
```

## Step B3 — Configure it

Run this as **one line** — pasting backslash-continued commands into zsh can
silently drop the values, leaving settings stored as `null`:

```bash
az webapp config appsettings set -n saber-api -g saber-rg --settings WEBSITES_PORT=8080 WEBSITES_ENABLE_APP_SERVICE_STORAGE=true UPLOADS_DIR=/home/uploads PYTHONUNBUFFERED=1
```

Verify every setting shows its value (not `null`):

```bash
az webapp config appsettings list -n saber-api -g saber-rg -o table
```

Then restart so the container picks them up:

```bash
az webapp restart -n saber-api -g saber-rg
```

- `WEBSITES_PORT=8080` — the port uvicorn listens on inside the container (see Dockerfile)
- `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` — mounts persistent storage at `/home`.
  A container's own filesystem is **wiped on every restart**; anything that must
  survive (user uploads) has to live under `/home`.
- `UPLOADS_DIR=/home/uploads` — same role as `/opt/saber/uploads` on the old server

> **Request timeout:** App Service allows up to 230 s per request. Analysis runs
> take 30–90 s, so no extra configuration is needed (the old nginx
> `proxy_read_timeout` tuning has no Azure equivalent to worry about).

## Step B4 — Test

```bash
curl https://saber-api.azurewebsites.net/list-projects
```

Expected: JSON like `{"projects":["LakewoodTestCase", ...]}`. The first request
after a deploy is slow (container cold start) — give it ~1 minute.

---

# Part C — Frontend (`saber-web`)

## Step C1 — Create the Web App

Run each command as one line (replace `sk-ant-...` with the real value from `client/.env.local`, keeping the quotes so zsh doesn't treat `<`/`>` as redirection):

```bash
az webapp create -n saber-web -g saber-rg -p saber-plan --runtime "NODE|22-lts"
az webapp config appsettings set -n saber-web -g saber-rg --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true NEXT_PUBLIC_API_URL=https://saber-api.azurewebsites.net "ANTHROPIC_API_KEY=sk-ant-..."
az webapp config set -n saber-web -g saber-rg --startup-file "npm start"
```

- `SCM_DO_BUILD_DURING_DEPLOYMENT=true` — Azure's Oryx builder runs `npm install`
  and `npm run build` on the server after each deploy, so you push source, not
  `node_modules`
- `NEXT_PUBLIC_API_URL` — **baked into the JS bundle at build time**, which is why
  the remote build must have it set as an app setting *before* the first deploy.
  If you ever change it, redeploy so the bundle is rebuilt.
- `ANTHROPIC_API_KEY` — used server-side by the `/api/chat` route; never exposed
  to the browser. `.env.local` stays local (it's in `.gitignore`).

## Step C2 — Deploy

From the repo root:

```bash
cd /Users/raj/CUB/Saber/client
zip -r /tmp/saber-web.zip . -x "node_modules/*" -x ".next/*" -x ".env.local"
az webapp deploy -n saber-web -g saber-rg --src-path /tmp/saber-web.zip --type zip
```

The remote build takes ~3–5 minutes. Watch it with:

```bash
az webapp log deployment show -n saber-web -g saber-rg
```

## Step C3 — Test end-to-end

1. Open `https://saber-web.azurewebsites.net`
2. Step 1: upload a `.pkl` file from `BldgAuditToolSimple_v1/Projects/LakewoodTestCase/`
3. DevTools → Network: the request should go to
   `https://saber-api.azurewebsites.net/upload-pkl` and return 200
4. Try the chatbot — it should stream a response
5. Analysis step: click Run Analysis — takes ~30 seconds

---

# Ongoing maintenance

## Update backend after a code change

```bash
az acr build -r saberacr -t saber-api:latest /Users/raj/CUB/Saber
az webapp restart -n saber-api -g saber-rg
```

The restart pulls the new `:latest` image.

## Update frontend after a code change

```bash
cd /Users/raj/CUB/Saber/client
zip -r /tmp/saber-web.zip . -x "node_modules/*" -x ".next/*" -x ".env.local"
az webapp deploy -n saber-web -g saber-rg --src-path /tmp/saber-web.zip --type zip
```

> **Optional upgrade:** wire a GitHub Action in the lab's GitHub org repo so
> pushes to `main` auto-deploy both apps (replaces what Vercel used to do).
> `az webapp deployment github-actions add` scaffolds this.

## Useful commands

```bash
# Live backend logs (equivalent of journalctl -f)
az webapp log tail -n saber-api -g saber-rg

# Live frontend logs
az webapp log tail -n saber-web -g saber-rg

# Restart an app
az webapp restart -n saber-api -g saber-rg

# Check app status
az webapp show -n saber-api -g saber-rg --query state

# Check uploads disk usage (opens a shell inside the container)
az webapp ssh -n saber-api -g saber-rg
du -sh /home/uploads/

# Current month's spend
az consumption usage list --query "[].{svc:instanceName,cost:pretaxCost}" -o table
```

## Custom domain (optional, later)

For `saber.colorado.edu` instead of `*.azurewebsites.net`:

1. Ask OIT to create a CNAME from `saber.colorado.edu` → `saber-web.azurewebsites.net`
2. ```bash
   az webapp config hostname add -n saber-web -g saber-rg --hostname saber.colorado.edu
   az webapp config ssl create -n saber-web -g saber-rg --hostname saber.colorado.edu
   ```
   App Service issues and renews a free managed certificate automatically.
3. Rebuild/redeploy the frontend? Not needed for the frontend domain itself, but
   if the **backend** gets a custom domain, update `NEXT_PUBLIC_API_URL` and
   redeploy the frontend so the new URL is baked into the bundle.

---

# Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `az group create` → `AuthorizationFailed` | Not in Contributor Grouper group | Ask Nick to add you at mygroups.colorado.edu, wait ~30 min, `az logout && az login` |
| Backend shows default "waiting for content" page | Container failed to start | `az webapp log tail -n saber-api -g saber-rg` and look for the uvicorn error |
| 503 + `container show` lists no `DOCKER_REGISTRY_SERVER_*` | App has no registry pull credentials | Run the `az webapp config container set` credential step in Part B, then restart |
| Terminal stuck at `cmdsubst dquote>` | Pasted command broke mid-line (unclosed `$(` or quote) | Ctrl+C, re-paste; run `$(...)` substitutions as separate variable assignments |
| Backend 503 / "container didn't respond" | Wrong port | Verify `WEBSITES_PORT=8080` app setting |
| App settings show `"value": null` | Backslash-continued command pasted badly | Re-run `appsettings set` as a single line, verify with `appsettings list -o table`, then restart the app |
| Uploads disappear after restart | Persistent storage off | Verify `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` and `UPLOADS_DIR=/home/uploads` |
| `CORS` error in browser | Wrong API URL baked in | Check `NEXT_PUBLIC_API_URL` app setting on `saber-web`, then redeploy frontend |
| Frontend deploy succeeds but site broken | Oryx build failed | `az webapp log deployment show -n saber-web -g saber-rg` |
| Chatbot returns 500 | Missing API key | Verify `ANTHROPIC_API_KEY` app setting on `saber-web` |
| Analysis request times out | Run exceeds 230 s App Service limit | Investigate the run; 230 s is a hard platform limit |
| First request very slow | Cold start after deploy/restart | Normal — B3 has Always On available: `az webapp config set -n saber-api -g saber-rg --always-on true` |
