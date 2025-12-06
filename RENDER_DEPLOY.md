# Deploy Backend to Render.com (Free Tier)

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `voiceagent`
3. Description: "Voice AI Agent for English Practice"
4. Choose Public or Private
5. **DO NOT** initialize with README (we have local files)
6. Click "Create repository"

## Step 2: Push Code to GitHub

Copy the commands from GitHub (replace YOUR_USERNAME):

```powershell
cd d:\voiceagent
git remote add origin https://github.com/YOUR_USERNAME/voiceagent.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Render.com

1. Go to https://render.com/
2. Sign up / Log in (use GitHub to connect)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository `voiceagent`
5. Configure the service:

   **Basic Settings:**
   - Name: `voiceagent-api`
   - Region: Choose closest to you
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`

   **Environment Variables:**
   Click "Add Environment Variable":
   - Key: `OPENAI_API_KEY`
   - Value: `your_openai_api_key_here`

6. Click "Create Web Service"
7. Wait 5-10 minutes for deployment
8. Copy your Render URL: `https://voiceagent-api-xxxx.onrender.com`

## Step 4: Update Frontend

```powershell
cd d:\voiceagent\frontend
notepad .env.production
```

Replace with your Render URL:
```
REACT_APP_API_URL=https://voiceagent-api-xxxx.onrender.com
```

## Step 5: Rebuild and Redeploy Frontend

```powershell
cd d:\voiceagent\frontend
npm run build
firebase deploy --only hosting
```

## Done! 🎉

Your complete application is now live:
- Frontend: https://speakandlearn1.web.app
- Backend: https://voiceagent-api-xxxx.onrender.com

## Notes

- Render free tier: Apps sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month free (enough for testing)
- No credit card required!
