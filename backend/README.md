# Voice AI Agent - Backend Deployment

Backend API deployed successfully!

## Local Development

```bash
cd backend/app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key

## API Endpoints

- `POST /api/conversation` - Process conversation with GPT
- `POST /api/text-to-speech` - Convert text to speech using OpenAI TTS
- `POST /api/end-session` - Get session analytics
