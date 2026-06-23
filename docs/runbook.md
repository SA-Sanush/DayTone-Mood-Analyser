# DayTone — Deployment & Operations Runbook

## Table of Contents
1. [Local Development](#1-local-development)
2. [Deploy to Render (free tier)](#2-deploy-to-render-free-tier)
3. [Deploy to Railway (alternative)](#3-deploy-to-railway-alternative)
4. [Deploy via Docker](#4-deploy-via-docker)
5. [Environment Variables Reference](#5-environment-variables-reference)
6. [Database Migrations](#6-database-migrations)
7. [Model Retraining](#7-model-retraining)
8. [Monitoring & Logs](#8-monitoring--logs)
9. [Incident Response](#9-incident-response)
10. [Backup & Recovery](#10-backup--recovery)

---

## 1. Local Development

```bash
# Clone and set up
git clone <repo-url>
cd DayTone
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Configure secrets
cp .env.example .env
# Edit .env — set SECRET_KEY, generate ENCRYPTION_KEY (see .env.example comment)

# Initialise database
flask db upgrade

# Download NLTK data (first run only)
python -c "import nltk; nltk.download('vader_lexicon')"

# Train the ML model (first run only)
python -m app.ml.train

# Start dev server
python run.py
# → http://127.0.0.1:5000
```

---

## 2. Deploy to Render (free tier)

**One-click method (recommended):**

1. Push repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Connect your GitHub repo — Render auto-detects `render.yaml`.
4. Set the one secret that can't be auto-generated:
   - `ENCRYPTION_KEY` → run `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` locally and paste the result.
5. Click **Deploy** — Render runs `flask db upgrade` then starts gunicorn.

**Manual method:**

1. Create a **Web Service** pointing to this repo.
2. Build command: `pip install -r requirements.txt && flask db upgrade`
3. Start command: `gunicorn "app:create_app()" --workers 2 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT --preload`
4. Add all env vars from [Environment Variables Reference](#5-environment-variables-reference).

> **Free tier limits**: 512 MB RAM, spins down after 15 min of inactivity (cold start ~30s).

---

## 3. Deploy to Railway (alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Create new project
railway new

# Add Postgres and Redis plugins from the Railway dashboard, then:
railway variables set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
railway variables set ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
railway variables set FLASK_ENV=production
railway variables set ADMIN_REGISTRATION_CODE=$(python -c "import secrets; print(secrets.token_hex(16))")
railway variables set SESSION_COOKIE_SECURE=true

# Deploy
railway up
```

---

## 4. Deploy via Docker

```bash
# Build
docker build -t daytone .

# Run standalone (SQLite, no Redis)
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret \
  -e ENCRYPTION_KEY=your-fernet-key \
  -v $(pwd)/instance:/app/instance \
  daytone

# Run with docker-compose (app + Redis)
cp .env.example .env   # fill in your values
docker-compose up -d

# View logs
docker-compose logs -f app
```

---

## 5. Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ Prod | Flask session signing key. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | ✅ Prod | Fernet key for note encryption. Generate: see `.env.example` |
| `DATABASE_URL` | ✅ Prod | PostgreSQL URL. SQLite used if unset (dev only). |
| `RATELIMIT_STORAGE_URI` | ✅ Prod | Redis URL for rate limiting, e.g. `redis://localhost:6379/0` |
| `REDIS_URL` | Optional | Alias for Redis URL (used by Render/Railway auto-injection) |
| `FLASK_ENV` | ✅ Prod | Set to `production` |
| `SESSION_COOKIE_SECURE` | ✅ Prod | Set to `true` (requires HTTPS) |
| `ADMIN_REGISTRATION_CODE` | ✅ Prod | ≥16 char token to unlock admin registration |
| `ADMIN_ALERT_EMAIL` | Recommended | Email for High-risk alerts and contact form |
| `MAIL_SERVER` | Optional | SMTP server (default: `smtp.gmail.com`) |
| `MAIL_PORT` | Optional | SMTP port (default: 587) |
| `MAIL_USERNAME` | Optional | SMTP login |
| `MAIL_PASSWORD` | Optional | SMTP password (use App Password for Gmail) |
| `SENTRY_DSN` | Optional | Sentry DSN for error tracking (free tier at sentry.io) |
| `COUNTRY` | Optional | Country code for localised crisis resources (default: GLOBAL) |

---

## 6. Database Migrations

```bash
# After changing models.py, generate a migration:
flask db migrate -m "describe your change"

# Review the generated file in migrations/versions/
# Then apply:
flask db upgrade

# Roll back one step:
flask db downgrade

# Check current migration state:
flask db current
```

> Render runs `flask db upgrade` automatically in the build command on every deploy.

---

## 7. Model Retraining

```bash
# Retrain with current training data
python -m app.ml.train

# Check model metrics
cat app/ml/model_metrics.json

# Run bias audit
python scripts/bias_audit.py

# Run drift monitor (compare to baseline)
python scripts/monitor_drift.py

# Reload model cache without restarting (dev)
flask reload-model
```

---

## 8. Monitoring & Logs

### Sentry (error tracking)
1. Create a free account at [sentry.io](https://sentry.io).
2. Create a Python/Flask project.
3. Copy the DSN and set `SENTRY_DSN=<your-dsn>` in env vars.
4. Errors are captured automatically — no extra code needed.

### Structured logs
- **Development**: plain text to stdout.
- **Production**: JSON lines to stdout + rotating file at `logs/daytone.log` (7-day retention).
- **Free log aggregator**: Connect [Better Stack](https://betterstack.com) or [Logtail](https://betterstack.com/logtail) to the log file.

### Health check
```bash
curl https://your-app.onrender.com/health
# → {"status": "ok"}
```

---

## 9. Incident Response

### App is down / 500 errors
1. Check Sentry for the error trace.
2. Check Render/Railway logs for the last 50 lines.
3. Roll back to the previous deploy in the Render dashboard if needed.
4. If DB migration caused it: `flask db downgrade` then redeploy.

### Rate limit being hit (429 errors)
- Redis connection lost → limiter falls back to in-memory (safe for single instance).
- Check Redis service status in the hosting dashboard.

### High-risk prediction spike
- Check the Admin → ML Diagnostics page for prediction distribution.
- Run `python scripts/monitor_drift.py` to check for model drift.
- If drift detected, retrain: `python -m app.ml.train`.

### Data breach / leaked secret
1. Immediately rotate `SECRET_KEY` (invalidates all sessions) and `ENCRYPTION_KEY` (requires re-encrypting notes).
2. Run `gitleaks detect --no-git` locally to audit for committed secrets.
3. Revoke and regenerate API keys in the Sentry/hosting dashboard.
4. Notify users if personal data was exposed.

---

## 10. Backup & Recovery

### SQLite (development)
```bash
# Manual backup
cp instance/daytone.db instance/daytone-backup-$(date +%Y%m%d).db
```

### PostgreSQL (production — Render/Railway)
- **Render**: Automated daily backups included in free tier. Restore from Render dashboard.
- **Supabase/Neon**: Point-in-time recovery available.
- **Manual backup**:
  ```bash
  pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
  # Restore:
  psql $DATABASE_URL < backup-YYYYMMDD.sql
  ```

### ML Model
- `app/ml/model.pkl` is excluded from git (see `.gitignore`).
- Store a copy in cloud storage (e.g. free Backblaze B2) after each retrain.
- Retrain from source data at any time: `python -m app.ml.train`.
