# Firebase Deployment Guide - speakandlearn-57614

## Quick Deploy to Firebase

### 1. Build the Frontend
```bash
cd d:\voiceagent\frontend
npm run build
```

### 2. Deploy to Firebase
```bash
firebase deploy
```

Your app will be live at: `https://speakandlearn-57614.web.app`

---

## Backend Deployment (Choose One)

### Option A: Railway.app (Recommended - Free & Easy)

1. **Sign up at railway.app**
2. **New Project → Deploy from GitHub**
3. **Add Environment Variables:**
   - `OPENAI_API_KEY` = your_openai_api_key_here
   - `MONGO_URI` = your_mongodb_uri_here (optional)
   - `MONGO_DB_NAME` = voice_ai_db (optional)
4. **Set Root Directory:** `backend`
5. Deploy automatically!

### Option B: Heroku

```bash
cd d:\voiceagent\backend
heroku login
heroku create speakandlearn-api
git init
git add .
git commit -m "Initial commit"
git push heroku main
heroku config:set OPENAI_API_KEY=sk-proj-...
heroku config:set MONGO_URI=mongodb+srv://...
heroku config:set MONGO_DB_NAME=voice_ai_db
```

### Option C: Render.com

1. Connect GitHub repo
2. New Web Service
3. Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `cd app && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

---

## Update Frontend with Backend URL

Once backend is deployed, update `.env.production`:

```bash
REACT_APP_API_URL=https://your-backend-url.railway.app
```

Then rebuild and redeploy:
```bash
npm run build
firebase deploy
```

---

## Test Your Deployment

1. Visit: https://speakandlearn-57614.web.app
2. Click microphone button
3. Allow microphone permissions
4. Start speaking!

---

## Troubleshooting

**Issue:** "Speech recognition not working"
- **Fix:** Firebase Hosting uses HTTPS automatically, which is required for browser speech recognition

**Issue:** "Cannot connect to backend"
- **Fix:** Update `REACT_APP_API_URL` in `.env.production` with your actual backend URL
- Rebuild: `npm run build`
- Redeploy: `firebase deploy`

**Issue:** "CORS error"
- **Fix:** Backend `main.py` already has CORS set to allow all origins (`allow_origins=["*"]`)

---

## Project URLs

- **Frontend:** https://speakandlearn-57614.web.app
- **Firebase Console:** https://console.firebase.google.com/u/0/project/speakandlearn-57614
- **Backend:** (Deploy and add URL here)
