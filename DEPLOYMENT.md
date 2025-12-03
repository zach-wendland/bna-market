# BNA Market Deployment Guide

This guide covers deploying BNA Market to Railway or Render. Both platforms support Python applications without Vercel's 250MB bundle size limitation.

---

## 🚂 **Option 1: Deploy to Railway (Recommended)**

Railway offers excellent developer experience with automatic deploys from GitHub and a generous free trial.

### Prerequisites
- GitHub account
- Railway account ([signup at railway.app](https://railway.app))
- API keys: RAPID_API_KEY and FRED_API_KEY

### Step-by-Step Deployment

#### 1. Push Code to GitHub
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

#### 2. Deploy via Railway Dashboard

**Option A: Web Interface (Easiest)**
1. Go to [railway.app](https://railway.app) and login
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `bna-market` repository
5. Railway will auto-detect Python and use the `Procfile`

**Option B: CLI (Fastest)**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up

# Open deployed app
railway open
```

#### 3. Set Environment Variables

In the Railway dashboard:
1. Go to your project → **Variables** tab
2. Add the following variables:
   - `RAPID_API_KEY` = `your_rapidapi_key`
   - `FRED_API_KEY` = `your_fred_api_key`
   - `SECRET_KEY` = `your_random_secret_key` (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `DATABASE_PATH` = `/app/data/BNASFR02.DB` (optional, auto-configured)

#### 4. Initial Data Population

**Important**: Your database will be empty on first deploy. Populate it by:

**Option A: Run ETL via Railway CLI**
```bash
# Connect to Railway shell
railway run bash

# Run ETL pipeline
python app.py

# Exit shell
exit
```

**Option B: Trigger via API** (if you add a scheduled job endpoint later)
```bash
curl -X POST https://your-app.railway.app/api/etl/refresh
```

#### 5. Monitor Deployment

Railway automatically:
- Installs dependencies from `requirements.txt`
- Runs the `Procfile` start command
- Provides a public URL
- Shows build logs and runtime logs

**View logs:**
```bash
railway logs
```

### Railway Pricing
- **Trial**: $5 free credit (no credit card required)
- **Hobby**: $5/month for 500 hours
- **Pro**: $20/month for 2000 hours

---

## 🎨 **Option 2: Deploy to Render**

Render offers a generous free tier with persistent storage, perfect for SQLite databases.

### Prerequisites
- GitHub account
- Render account ([signup at render.com](https://render.com))
- API keys: RAPID_API_KEY and FRED_API_KEY

### Step-by-Step Deployment

#### 1. Push Code to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

#### 2. Create New Web Service

1. Go to [render.com/dashboard](https://render.com/dashboard)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account and select `bna-market` repo
4. Render will auto-detect the `render.yaml` configuration

**Manual Configuration** (if not using render.yaml):
- **Name**: `bna-market`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 "src.bna_market.web.app:create_app()"`
- **Plan**: `Free` (or choose paid for better performance)

#### 3. Add Persistent Disk (For SQLite Database)

**Important**: Free tier instances restart periodically, which can lose your database without persistent storage.

1. In your service settings, go to **Disks** tab
2. Click **"Add Disk"**
3. Configure:
   - **Name**: `bna-database`
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: `1 GB` (free tier allows up to 1GB)

#### 4. Set Environment Variables

In the Render dashboard → **Environment** tab:
- `RAPID_API_KEY` = `your_rapidapi_key`
- `FRED_API_KEY` = `your_fred_api_key`
- `SECRET_KEY` = `your_random_secret_key`
- `FLASK_ENV` = `production`
- `DATABASE_PATH` = `/opt/render/project/src/data/BNASFR02.DB`

#### 5. Deploy

Click **"Create Web Service"** - Render will:
1. Clone your repository
2. Install dependencies
3. Start the application
4. Provide a public URL: `https://bna-market.onrender.com`

#### 6. Initial Data Population

**Option A: Manual Shell Access**
1. Go to **Shell** tab in Render dashboard
2. Run:
   ```bash
   python app.py
   ```

**Option B: Scheduled Job** (Recommended for regular updates)
1. Create a new **Cron Job** in Render
2. Command: `python app.py`
3. Schedule: `0 */6 * * *` (every 6 hours)

### Render Pricing
- **Free**: 512 MB RAM, spins down after 15 min inactivity
- **Starter**: $7/month, always-on, 512 MB RAM
- **Standard**: $25/month, 2 GB RAM

---

## 🔄 **Post-Deployment Setup**

### 1. Verify Health Check
```bash
curl https://your-app-url.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-03T12:00:00"
}
```

### 2. Populate Database

Your dashboard will show "No data available" until you run the ETL pipeline:

```bash
# Via Railway
railway run python app.py

# Via Render (Shell tab)
python app.py
```

This will:
- Fetch Zillow property listings (for-sale and rentals)
- Fetch FRED economic metrics
- Store data in SQLite database

### 3. Test Dashboard

Visit your deployment URL:
- Railway: `https://your-app.railway.app`
- Render: `https://bna-market.onrender.com`

You should see:
- Property KPIs (rental/sale counts and averages)
- FRED economic indicators
- Plotly interactive charts
- Property tables with search/filter

---

## 🔧 **Troubleshooting**

### Build Fails: "Module not found"
**Cause**: Missing dependency in `requirements.txt`
**Fix**: Verify all imports have corresponding packages listed

### Runtime Error: "No such table: BNA_RENTALS"
**Cause**: Database not populated
**Fix**: Run `python app.py` to populate tables

### App Shows "Application Error"
**Check logs:**
```bash
# Railway
railway logs

# Render
# View logs in dashboard → Logs tab
```

### Database Resets on Render
**Cause**: Free tier instances restart periodically
**Fix**: Add persistent disk (see Render deployment step 3)

### Slow Initial Load
**Cause**: Free tier "cold starts" (app spins down after inactivity)
**Fix**: Upgrade to paid plan or implement keep-alive ping

---

## 📊 **Monitoring & Maintenance**

### Update Data Pipeline

**Automated** (Recommended):
Set up a cron job to run `python app.py` periodically:
- **Railway**: Use GitHub Actions with Railway API
- **Render**: Create Cron Job service (see step 6 in Render guide)

**Manual**:
```bash
railway run python app.py  # Railway
# OR use Render Shell tab
```

### View Application Logs
```bash
# Railway
railway logs --tail

# Render
# Dashboard → Logs tab → Stream logs
```

### Update Environment Variables

Both platforms allow updating env vars without redeployment:
- Railway: Project → Variables tab
- Render: Service → Environment tab

---

## 🚀 **Performance Optimization**

### 1. Increase Workers (Paid Plans)

Edit `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 "src.bna_market.web.app:create_app()"
```

Formula: `workers = (2 × CPU cores) + 1`

### 2. Enable Caching

Add Redis for query caching:
```bash
# Railway: Add Redis plugin
railway add redis

# Render: Add Redis service
# Dashboard → New + → Redis
```

### 3. Database Indexes

Already included in `scripts/add_indexes.py`:
```bash
python scripts/add_indexes.py
```

---

## 🔐 **Security Checklist**

- ✅ Environment variables (not hardcoded secrets)
- ✅ `SECRET_KEY` set to random value
- ✅ HTTPS enabled by default (Railway/Render)
- ✅ `.env` in `.gitignore`
- ⚠️ Consider adding authentication for production use

---

## 📞 **Support**

### Railway
- Docs: [docs.railway.app](https://docs.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)

### Render
- Docs: [render.com/docs](https://render.com/docs)
- Community: [community.render.com](https://community.render.com)

---

## 🎉 **Success!**

Your BNA Market dashboard is now live! Share your deployment URL and start analyzing Nashville real estate data.

**Next Steps:**
1. Schedule regular ETL updates
2. Add custom domain (optional)
3. Implement user authentication (optional)
4. Set up monitoring/alerts (optional)
