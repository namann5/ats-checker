# 🚀 Deployment Guide – ATS Analyzer

## Quick Deploy to Render.com (Recommended – Free Tier)

### Step 1: Connect Your GitHub Repo
1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Connect your GitHub account and select `namann5/ats-checker`

### Step 2: Configure Deployment
- **Name:** `ats-checker` (or your preferred name)
- **Environment:** `Docker`
- **Build Command:** `pip install -r requirements.txt` (auto-detected)
- **Start Command:** 
  ```
  gunicorn -w 4 -b 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker app.main:app
  ```
- **Instance Type:** `Free` (or upgrade to paid)
- **Auto Deploy:** Enable (auto-deploy on GitHub push)

### Step 3: Add Environment Variables
In Render dashboard, go to **Environment** and add:
```
APPLICATION_ID=your_back4app_app_id
MASTER_KEY=your_back4app_master_key
OPENAI_API_KEY=your_openai_key (optional)
PYTHONUNBUFFERED=true
```

### Step 4: Deploy
Click **"Create Web Service"** and Render will:
- ✅ Pull your code from GitHub
- ✅ Build the Docker image
- ✅ Deploy and run your app
- ✅ Provide a live URL (e.g., `https://ats-checker.onrender.com`)

Your app will be live in 2-3 minutes!

---

## Alternative: Deploy to Other Platforms

### Heroku
```bash
heroku create ats-checker
heroku config:set APPLICATION_ID=your_id MASTER_KEY=your_key OPENAI_API_KEY=your_key
git push heroku main
```

### Railway.app
1. Connect GitHub repo
2. Set environment variables
3. Auto-deploys on push (similar to Render)

### PythonAnywhere
1. Upload code via web interface
2. Configure WSGI script to point to `app.main:app`
3. Add environment variables in web app settings

### DigitalOcean / AWS / Google Cloud
- Use Docker image: `gunicorn` start command
- Set environment variables via platform UI
- Scale horizontally as needed

---

## Local Testing Before Deploy

```powershell
# Install gunicorn locally
pip install gunicorn

# Test with Gunicorn (like production)
gunicorn -w 4 -b 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker app.main:app

# Open http://127.0.0.1:8000
```

---

## Monitoring & Logs

### Render.com Logs
- Dashboard → Logs tab → View real-time logs

### Health Check
- Render automatically checks `/` endpoint every 30 seconds
- If it fails 3 times, service restarts

---

## Environment Variables (Keep Confidential!)

**Never commit `back4app.env` to Git!**

Add these to your platform's secrets:
- `APPLICATION_ID` – Back4App App ID
- `MASTER_KEY` – Back4App Master Key
- `OPENAI_API_KEY` – OpenAI API key (optional)

---

## Troubleshooting

**"Start command not found"**
- Make sure `gunicorn` is in `requirements.txt` ✅ (Already done)

**"502 Bad Gateway"**
- Check logs for Python errors
- Verify environment variables are set
- Ensure app starts without errors locally

**"Module not found"**
- Verify `requirements.txt` has all dependencies
- Run `pip install -r requirements.txt` locally to test

---

## Costs

**Render.com Free Tier:**
- ✅ 1 free web service (spins down after 15 min of inactivity)
- ✅ 100 GB/month bandwidth
- ✅ Auto-deploys from GitHub

**Paid ($7/month minimum):**
- Always-on instances
- Dedicated resources
- Better performance

---

## Next Steps

1. **Deploy now:** Go to https://render.com and connect your repo
2. **Monitor:** Check logs after deployment
3. **Test:** Visit your live URL and test the analyzer
4. **Scale:** Upgrade instance type if needed

**Your app will be production-ready in minutes!** 🚀
