# Quick Deployment Guide

## ✅ Already Done:
- ✅ Code cleaned up and committed
- ✅ Frontend deployed: https://speakandlearn1.web.app
- ✅ Backend ready for deployment

## 🚀 Deploy Backend Now (5 minutes):

### Step 1: Create GitHub Repository

1. Open: https://github.com/new
2. Repository name: `voiceagent`
3. Make it **Public**
4. **DO NOT** check "Add README"
5. Click **"Create repository"**

### Step 2: Push Code to GitHub

After creating the repo, GitHub will show commands. Copy your username and run:

```powershell
cd d:\voiceagent
git remote add origin https://github.com/YOUR_USERNAME/voiceagent.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render.com (FREE)

1. Open: https://render.com/
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest)
4. Click **"New +"** → **"Web Service"**
5. Click **"Connect account"** to link GitHub
6. Find and select **"voiceagent"** repository
7. Configure:

   **Name:** `voiceagent-api`
   
   **Region:** Oregon (US West) or closest
   
   **Branch:** `main`
   
   **Root Directory:** `backend`
   
   **Runtime:** `Python 3`
   
   **Build Command:** `pip install -r requirements.txt`
   
   **Start Command:** `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`

8. Click **"Advanced"** → **"Add Environment Variable"**:
   - Key: `OPENAI_API_KEY`
   - Value: `your_openai_api_key_here`

9. Select **"Free"** plan
10. Click **"Create Web Service"**

Wait 5-10 minutes for deployment. You'll get a URL like:
`https://voiceagent-api-xxxx.onrender.com`

### Step 4: Update Frontend

```powershell
cd d:\voiceagent\frontend
notepad .env.production
```

Change to your Render URL:
```
REACT_APP_API_URL=https://voiceagent-api-xxxx.onrender.com
```

Save and rebuild:
```powershell
npm run build
firebase deploy --only hosting
```

## 🎉 Done!

Your app is now fully deployed:
- **Frontend:** https://speakandlearn1.web.app
- **Backend:** https://voiceagent-api-xxxx.onrender.com

**Note:** Render free tier sleeps after 15 min inactivity. First request takes ~30s to wake up.
