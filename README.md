# Voice AI Agent - English Practice Partner

A modern AI-powered voice conversation partner for English practice with real-time speech recognition, intelligent conversations using OpenAI GPT, and detailed analytics.

## 🚀 Features

- **Browser Speech Recognition** - Uses native browser speech-to-text (no external dependencies)
- **AI Conversations** - Powered by OpenAI GPT-3.5-turbo for natural, engaging dialogue
- **Voice Synthesis** - High-quality text-to-speech using OpenAI TTS
- **Session Analytics** - Track vocabulary, confidence, pronunciation, and more
- **Modern UI** - Cyberpunk-themed interface with aqua accents and smooth animations
- **Real-time Feedback** - Get corrections and suggestions during conversation

## 📋 Prerequisites

- Node.js 16+ and npm
- Python 3.11+
- OpenAI API key
- Chrome or Edge browser (for best speech recognition support)

## 🛠️ Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-openai-api-key"
$env:MONGO_URI="your-mongodb-uri"  # Optional
$env:MONGO_DB_NAME="voice_ai_db"  # Optional
```

4. Start the backend server:
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## 🔥 Firebase Deployment

### Frontend (Firebase Hosting)

1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

3. Initialize Firebase (if not already done):
```bash
cd frontend
firebase init hosting
```

4. Build the React app:
```bash
npm run build
```

5. Deploy to Firebase:
```bash
firebase deploy
```

### Backend Deployment Options

**Option 1: Heroku**
```bash
cd backend
heroku create your-app-name
git push heroku main
heroku config:set OPENAI_API_KEY=your-key
```

**Option 2: Google Cloud Run**
```bash
gcloud run deploy voice-ai-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key
```

**Option 3: Railway**
1. Connect your GitHub repo to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically

## 🎯 Usage

1. Click the microphone button to start speaking
2. Have a natural conversation with the AI
3. The AI will respond with voice and text
4. Say "end session" to finish and view your analytics report

## 📊 Analytics Tracked

- **Vocabulary Richness** - Unique words used
- **Confidence Level** - Speech clarity and fluency
- **Pronunciation** - Accuracy score
- **Grammar** - Grammatical correctness
- **Fluency** - Natural flow of speech
- **Response Time** - Speed of replies

## 🔧 Configuration

Update the API base URL in `frontend/src/components/Dashboard.jsx`:
```javascript
const API_BASE = 'your-backend-url';
```

## 📝 Environment Variables

### Backend
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `MONGO_URI` - MongoDB connection string (optional)
- `MONGO_DB_NAME` - MongoDB database name (optional)

## 🎨 Theme

The app uses a cyberpunk aesthetic with:
- Background: Black (#000000)
- Primary: Aqua (#7FFFD4)
- Text: Alice Blue (#F0F8FF)
- Glowing effects and smooth animations

## 🐛 Troubleshooting

**Speech recognition not working:**
- Use Chrome or Edge browser
- Allow microphone permissions
- Ensure HTTPS (required for production)

**Backend errors:**
- Check OpenAI API key is valid
- Verify backend is running on correct port
- Check CORS configuration

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 🤝 Contributing

Pull requests welcome! Please ensure code follows existing style.

## 📧 Support

For issues or questions, please open a GitHub issue.
