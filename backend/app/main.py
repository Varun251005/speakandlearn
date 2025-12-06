from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import os
import json
import random
import io
import base64

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API configuration (GPT-4 for excellent real-time conversation)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Session storage (in-memory, stateless per session)
active_sessions = {}


class ConversationMetrics:
    """Track conversation metrics during session"""
    def __init__(self):
        self.all_words = []
        self.unique_words = set()
        self.total_turns = 0
        self.grammar_errors = 0
        self.grammar_error_examples = []
        self.short_answers = 0
        self.long_answers = 0
        self.topics_discussed = set()
        self.filler_words_count = 0
        self.filler_words_used = []
        self.repeated_words = {}
        self.corrections_needed = []
        self.conversation_history = []
    
    def add_turn(self, user_text: str, ai_response: str = ""):
        """Add user's turn and AI response to conversation history"""
        self.total_turns += 1
        
        # Store in conversation history (user message, then AI response)
        self.conversation_history.append(user_text)
        if ai_response:
            self.conversation_history.append(ai_response)
        
        # Analyze user's text
        words = user_text.lower().split()
        self.all_words.extend(words)
        self.unique_words.update(words)
        
        # Track repeated words
        for word in words:
            if len(word) > 3:  # Only track meaningful words
                self.repeated_words[word] = self.repeated_words.get(word, 0) + 1
        
        # Detect filler words
        filler_words = ["um", "uh", "like", "you know", "i mean", "basically", "actually", "literally"]
        for filler in filler_words:
            if filler in user_text.lower():
                self.filler_words_count += 1
                if filler not in self.filler_words_used:
                    self.filler_words_used.append(filler)
        
        # Count answer length
        if len(words) < 5:
            self.short_answers += 1
        else:
            self.long_answers += 1
        
        # Enhanced grammar error detection with examples
        grammar_issues = {
            "i is": "Use 'I am' instead of 'I is'",
            "he are": "Use 'he is' instead of 'he are'",
            "she are": "Use 'she is' instead of 'she are'",
            "they is": "Use 'they are' instead of 'they is'",
            "was you": "Use 'were you' instead of 'was you'",
            "were he": "Use 'was he' instead of 'were he'",
            "doesn't have": "Check: 'don't have' for I/you/we/they",
            "don't has": "Use 'doesn't have' for he/she/it"
        }
        
        for error, correction in grammar_issues.items():
            if error in user_text.lower():
                self.grammar_errors += 1
                if correction not in self.corrections_needed:
                    self.corrections_needed.append(correction)
                    self.grammar_error_examples.append(f"Found: '{error}' - {correction}")
    
    def get_scores(self) -> dict:
        """Calculate final scores (0-100 scale)"""
        if self.total_turns == 0:
            return {
                "vocabulary": 50,
                "grammar": 50,
                "fluency": 50,
                "pronunciation": 75,
                "confidence": 50
            }
        
        # Vocabulary: based on unique words vs total
        vocab_diversity = len(self.unique_words) / max(len(self.all_words), 1)
        vocabulary_score = min(100, int(vocab_diversity * 200 + 50))
        
        # Grammar: based on detected errors
        grammar_score = max(30, 100 - (self.grammar_errors * 15))
        
        # Fluency: based on long vs short answers
        fluency_ratio = self.long_answers / max(self.total_turns, 1)
        fluency_score = min(100, int(fluency_ratio * 100 + 40))
        
        # Pronunciation: assume good (we use browser speech recognition)
        pronunciation_score = 80
        
        # Confidence: based on answer length and participation
        confidence_score = min(100, int((self.long_answers / max(self.total_turns, 1)) * 120 + 30))
        
        return {
            "vocabulary": vocabulary_score,
            "grammar": grammar_score,
            "fluency": fluency_score,
            "pronunciation": pronunciation_score,
            "confidence": confidence_score
        }
    
    def generate_report(self) -> dict:
        """Generate full session report"""
        scores = self.get_scores()
        
        # Summary
        summary = f"Great conversation! You spoke {self.total_turns} times with {len(self.unique_words)} unique words. "
        if scores["fluency"] > 70:
            summary += "Your fluency is improving nicely."
        else:
            summary += "Try to speak in longer sentences to build fluency."
        
        # Most repeated words (potential overuse)
        top_repeated = sorted(self.repeated_words.items(), key=lambda x: x[1], reverse=True)[:5]
        overused_words = [word for word, count in top_repeated if count > 3]
        
        # Words to learn (common words they might have missed)
        common_conversation_words = ["although", "however", "therefore", "meanwhile", "furthermore", 
                                     "basically", "specifically", "particularly", "generally", "obviously"]
        missed_words = [word for word in common_conversation_words if word not in self.unique_words]
        
        # Strengths
        strengths = []
        if scores["vocabulary"] > 70:
            strengths.append(f"Good vocabulary variety - used {len(self.unique_words)} unique words")
        if scores["confidence"] > 70:
            strengths.append("Confident speaking style with detailed answers")
        if scores["pronunciation"] > 70:
            strengths.append("Clear pronunciation and articulation")
        if self.long_answers > self.short_answers:
            strengths.append("Provides detailed, elaborate answers")
        if self.filler_words_count < 3:
            strengths.append("Minimal use of filler words - speaks naturally")
        if not strengths:
            strengths = ["Participated actively", "Willing to practice"]
        
        # Weaknesses
        weaknesses = []
        if scores["vocabulary"] < 60:
            weaknesses.append("Limited vocabulary variety - try using synonyms")
        if scores["grammar"] < 60:
            weaknesses.append("Grammar errors detected - review subject-verb agreement")
        if scores["fluency"] < 60:
            weaknesses.append("Practice speaking longer, connected sentences")
        if self.short_answers > self.long_answers:
            weaknesses.append("Answers too brief - elaborate more on your thoughts")
        if self.filler_words_count > 5:
            weaknesses.append(f"Used filler words ({', '.join(self.filler_words_used[:3])}) frequently")
        if overused_words:
            weaknesses.append(f"Overused certain words: {', '.join(overused_words[:3])}")
        if not weaknesses:
            weaknesses = ["Keep practicing daily to maintain progress"]
        
        # Suggestions
        suggestions = []
        if scores["fluency"] < 70:
            suggestions.append("Practice describing things in 3-4 sentences instead of one")
        if scores["vocabulary"] < 70:
            suggestions.append("Read English articles and note new words daily")
        if self.corrections_needed:
            suggestions.append(f"Grammar focus: {self.corrections_needed[0]}")
        if missed_words:
            suggestions.append(f"Try using transition words like: {', '.join(missed_words[:3])}")
        if self.filler_words_count > 5:
            suggestions.append("Pause instead of using filler words - it's okay to think!")
        if len(suggestions) < 3:
            suggestions.append("Have conversations daily to build confidence and fluency")
        
        # Detailed analytics
        analytics = {
            "total_words": len(self.all_words),
            "unique_words": len(self.unique_words),
            "vocabulary_diversity": round(len(self.unique_words) / max(len(self.all_words), 1) * 100, 1),
            "filler_words_count": self.filler_words_count,
            "grammar_errors_count": self.grammar_errors,
            "avg_response_length": round(len(self.all_words) / max(self.total_turns, 1), 1),
            "overused_words": overused_words[:5],
            "missed_words": missed_words[:8],
            "corrections": self.corrections_needed[:5]
        }
        
        return {
            "summary": summary,
            "scores": scores,
            "strengths": strengths[:4],
            "weaknesses": weaknesses[:4],
            "suggestions": suggestions[:3],
            "analytics": analytics
        }


async def get_conversation_response(user_text: str, session_id: str) -> str:
    """Get natural conversation response from OpenAI GPT with full context"""
    
    # Check if session should end
    end_phrases = ["end session", "finish", "stop session", "give report", "show report", "end conversation"]
    if any(phrase in user_text.lower() for phrase in end_phrases):
        return "__END_SESSION__"
    
    # Get session conversation history
    session = active_sessions.get(session_id)
    conversation_history = []
    if session:
        conversation_history = session.conversation_history[-10:]  # Last 5 exchanges
    
    # Build OpenAI chat messages format
    messages = [
        {
            "role": "system",
            "content": "You are a friendly conversation partner helping someone practice their English speaking skills. Keep responses natural, engaging, and conversational. Ask follow-up questions based on what they say. Keep responses under 2-3 sentences."
        }
    ]
    
    # Add conversation history
    if conversation_history:
        for i, msg in enumerate(conversation_history):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({
                "role": role,
                "content": msg
            })
    
    # Add current user message
    messages.append({
        "role": "user",
        "content": user_text
    })
    
    # Try OpenAI API
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 80,
                "top_p": 0.9,
                "frequency_penalty": 0.6,
                "presence_penalty": 0.6
            }
            
            r = await client.post(
                OPENAI_API_URL,
                json=payload,
                headers=headers
            )
            r.raise_for_status()
            result = r.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                response_text = result["choices"][0]["message"]["content"].strip()
                if response_text and len(response_text) > 3:
                    return response_text
    
    except Exception as e:
        print(f"OpenAI API error: {e}")
    
    # Fallback to contextual responses with history awareness
    return generate_natural_response(user_text, conversation_history)


def generate_natural_response(user_text: str, conversation_history: list = None) -> str:
    """Generate natural, context-aware responses"""
    text_lower = user_text.lower()
    history_context = " ".join(conversation_history[-4:]) if conversation_history else ""
    
    # Context-aware follow-ups
    if conversation_history and len(conversation_history) >= 2:
        last_topic = conversation_history[-2].lower()
        
        # Follow up on previous topic
        if "movie" in last_topic or "film" in last_topic:
            return random.choice([
                "What else did you like about it?",
                "Have you seen similar ones?",
                "Would you watch it again?",
                "What was your favorite scene?"
            ])
        
        if "food" in last_topic or "restaurant" in last_topic:
            return random.choice([
                "Do you go there often?",
                "What else do they serve?",
                "Have you tried making it at home?",
                "What makes it so good?"
            ])
        
        if "travel" in last_topic or "visit" in last_topic:
            return random.choice([
                "What was the highlight of your trip?",
                "How long did you stay?",
                "Would you recommend it to others?",
                "What surprised you most?"
            ])
    
    # New topic responses
    if any(word in text_lower for word in ["movie", "film", "watch", "cinema", "actor"]):
        return random.choice([
            "That sounds interesting! What kind of movies do you like?",
            "I love movies too! What was it about?",
            "Tell me more about it!",
            "Nice! Who was in it?",
            "Really? What did you think?"
        ])
    
    if any(word in text_lower for word in ["food", "eat", "cook", "restaurant", "dish"]):
        return random.choice([
            "That sounds delicious! What's your favorite?",
            "I see! Do you like cooking?",
            "Tell me more! What does it taste like?",
            "Nice! Where did you try it?",
            "Interesting! Have you made it yourself?"
        ])
    
    if any(word in text_lower for word in ["travel", "trip", "vacation", "visit", "country"]):
        return random.choice([
            "That sounds amazing! Where did you go?",
            "I'd love to hear more! What did you see?",
            "Tell me about it! How long were you there?",
            "Nice! What was your favorite part?",
            "Interesting! Would you go again?"
        ])
    
    if any(word in text_lower for word in ["work", "job", "career", "office", "company"]):
        return random.choice([
            "I see! What do you do there?",
            "Tell me more! What's it like?",
            "That's cool! Do you enjoy it?",
            "Interesting! How long have you been there?",
            "Nice! What do you like about it?"
        ])
    
    if any(word in text_lower for word in ["study", "school", "university", "learn", "student"]):
        return random.choice([
            "That's great! What are you studying?",
            "I see! What's your favorite subject?",
            "Tell me more! How's it going?",
            "Interesting! Why did you choose that?",
            "Nice! What do you want to do after?"
        ])
    
    if any(word in text_lower for word in ["hobby", "sport", "game", "play", "music"]):
        return random.choice([
            "That's cool! How often do you do that?",
            "I see! What do you like about it?",
            "Tell me more! How did you start?",
            "Interesting! Are you good at it?",
            "Nice! What else do you enjoy?"
        ])
    
    if any(word in text_lower for word in ["name", "my name is", "i'm", "i am"]):
        return random.choice([
            "Nice to meet you! What would you like to talk about?",
            "Great! What do you enjoy doing?",
            "Wonderful! Tell me about yourself.",
            "That's a nice name! What are your interests?",
            "Excellent! What brings you here today?"
        ])
    
    # Generic natural responses
    return random.choice([
        "That's interesting! Tell me more.",
        "I see! What do you think about it?",
        "Really? What happened?",
        "Tell me more about that.",
        "That's cool! What else?",
        "Interesting! Why is that?",
        "I understand. What's your opinion?",
        "That sounds nice! Can you explain more?",
        "I get it. What do you mean exactly?",
        "That's great! What else can you tell me?"
    ])


@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Voice Conversation Partner API"}


@app.post("/api/conversation")
async def conversation(
    text: str = Form(...),
    session_id: str = Form(...)
):
    """Handle conversation turn"""
    try:
        # Initialize session if new
        if session_id not in active_sessions:
            active_sessions[session_id] = ConversationMetrics()
            # Return welcome message for first turn
            if text.lower() in ["hi", "hello", "hey", "start"]:
                return {
                    "reply": "Hi! What would you like to talk about today?",
                    "is_welcome": True
                }
        
        metrics = active_sessions[session_id]
        
        # Get AI response FIRST (to access history before adding this turn)
        ai_reply = await get_conversation_response(text, session_id)
        
        # Check if session should end
        if ai_reply == "__END_SESSION__":
            # Track this final turn before generating report
            metrics.add_turn(text, "")
            report = metrics.generate_report()
            # Clean up session
            del active_sessions[session_id]
            return {
                "reply": "Thank you for practicing with me today!",
                "end_session": True,
                "report": report
            }
        
        # Track this turn with both user text and AI response
        metrics.add_turn(text, ai_reply)
        
        return {
            "reply": ai_reply,
            "end_session": False
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/start-session")
async def start_session(session_id: str = Form(...)):
    """Initialize new session"""
    active_sessions[session_id] = ConversationMetrics()
    return {
        "message": "Session started",
        "welcome": "Hi! What would you like to talk about today?"
    }


@app.post("/api/text-to-speech")
async def text_to_speech(text: str = Form(...)):
    """Convert text to speech using OpenAI TTS"""
    try:
        print(f"TTS Request for text: '{text[:50]}...'")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": "nova",
                "response_format": "mp3"
            }
            
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"TTS API Error: {response.status_code} - {error_text}")
                raise HTTPException(status_code=500, detail=f"OpenAI TTS error: {error_text}")
            
            # Convert audio to base64
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            print(f"TTS Success: Generated {len(audio_base64)} bytes")
            
            return {
                "audio": audio_base64,
                "format": "mp3"
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"TTS Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
