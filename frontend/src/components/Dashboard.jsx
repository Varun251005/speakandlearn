import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, RadarChart, Radar, PolarGrid, 
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, Cell 
} from 'recharts';
import './Dashboard.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [conversation, setConversation] = useState([]);
  const [isActive, setIsActive] = useState(false);
  const [sessionId] = useState(`session-${Date.now()}`);
  const [sessionEnded, setSessionEnded] = useState(false);
  const [finalReport, setFinalReport] = useState(null);
  const [listeningError, setListeningError] = useState('');
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  useEffect(() => {
    // Start with welcome message
    const welcome = "Hi! What would you like to talk about today?";
    setConversation([{ type: 'ai', text: welcome }]);
    speakText(welcome);
  }, []);

  const speakText = async (text) => {
    try {
      // Use OpenAI TTS API via backend
      const formData = new FormData();
      formData.append('text', text);

      const response = await axios.post('http://localhost:8000/api/text-to-speech', formData);
      
      if (response.data.audio) {
        // Convert base64 to audio and play
        const audioData = `data:audio/mp3;base64,${response.data.audio}`;
        const audio = new Audio(audioData);
        audio.play();
      }
    } catch (error) {
      console.error('TTS Error:', error);
      // Fallback to browser TTS
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
      }
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setListeningError('');
    
    if (!SpeechRecognition) {
      const message = 'Speech recognition not supported in your browser. Please use Chrome or Edge.';
      setListeningError(message);
      alert(message);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      console.log('Speech recognition started...');
      setIsActive(true);
    };

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      console.log('You said:', transcript);
      
      setConversation(prev => [...prev, { type: 'user', text: transcript }]);
      await processConversation(transcript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsActive(false);

      const messages = {
        'not-allowed': 'Microphone access denied. Please allow microphone permissions.',
        'network': 'Speech recognition could not reach its service. Check your internet connection or browser network access.',
        'no-speech': 'No speech was detected. Try speaking a little louder and closer to the microphone.',
        'audio-capture': 'No microphone was found or it is already in use by another app.',
        'service-not-allowed': 'Speech recognition is blocked in this browser or environment.'
      };

      const message = messages[event.error] || `Speech recognition error: ${event.error}`;
      setListeningError(message);

      if (event.error === 'not-allowed') {
        alert(message);
      }
    };

    recognition.onend = () => {
      console.log('Stopped listening');
      setIsActive(false);
    };

    recognition.start();
  };

  const processConversation = async (userText) => {
    try {
      const formData = new FormData();
      formData.append('text', userText);
      formData.append('session_id', sessionId);

      const response = await axios.post(`${API_BASE}/api/conversation`, formData);
      const data = response.data;

      // Add AI response
      setConversation(prev => [...prev, { type: 'ai', text: data.reply }]);
      
      // Speak response
      speakText(data.reply);

      // Check if session ended
      if (data.end_session && data.report) {
        setSessionEnded(true);
        setFinalReport(data.report);
      }

    } catch (error) {
      console.error('Error:', error);
      const errorMsg = "Sorry, I couldn't process that. Please try again.";
      setConversation(prev => [...prev, { type: 'ai', text: errorMsg }]);
      speakText(errorMsg);
    }
  };

  const endSession = () => {
    // User manually ends session
    processConversation("end session");
  };

  const startNewSession = () => {
    window.location.reload();
  };

  const backToHome = () => {
    window.location.reload();
  };

  if (sessionEnded && finalReport) {
    // Prepare chart data
    const radarData = [
      { skill: 'Vocabulary', value: finalReport.scores.vocabulary, fullMark: 100 },
      { skill: 'Grammar', value: finalReport.scores.grammar, fullMark: 100 },
      { skill: 'Fluency', value: finalReport.scores.fluency, fullMark: 100 },
      { skill: 'Pronunciation', value: finalReport.scores.pronunciation, fullMark: 100 },
      { skill: 'Confidence', value: finalReport.scores.confidence, fullMark: 100 },
    ];

    const barData = [
      { name: 'Vocabulary', score: finalReport.scores.vocabulary },
      { name: 'Grammar', score: finalReport.scores.grammar },
      { name: 'Fluency', score: finalReport.scores.fluency },
      { name: 'Pronunciation', score: finalReport.scores.pronunciation },
      { name: 'Confidence', score: finalReport.scores.confidence },
    ];

    const COLORS = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];

    return (
      <div className="dashboard">
        <div className="session-report">
          <div className="report-header">
            <button className="btn-back-home" onClick={backToHome} aria-label="Back to home">
              <span className="btn-icon">←</span>
              <span className="btn-back-text">Back</span>
            </button>
            <div className="report-icon">🎉</div>
            <h1>Session Complete!</h1>
            <p>Here's your comprehensive performance analysis</p>
          </div>
          
          <div className="report-section summary-section">
            <div className="section-icon">📝</div>
            <h2>Session Summary</h2>
            <p>{finalReport.summary}</p>
            {finalReport.analytics && (
              <div className="stats-grid">
                <div className="stat-box">
                  <div className="stat-value">{finalReport.analytics.total_words}</div>
                  <div className="stat-label">Total Words</div>
                </div>
                <div className="stat-box">
                  <div className="stat-value">{finalReport.analytics.unique_words}</div>
                  <div className="stat-label">Unique Words</div>
                </div>
                <div className="stat-box">
                  <div className="stat-value">{finalReport.analytics.vocabulary_diversity}%</div>
                  <div className="stat-label">Vocabulary Diversity</div>
                </div>
                <div className="stat-box">
                  <div className="stat-value">{finalReport.analytics.avg_response_length}</div>
                  <div className="stat-label">Avg Response Length</div>
                </div>
              </div>
            )}
          </div>

          {/* Performance Radar Chart */}
          <div className="report-section chart-section">
            <div className="section-icon">📊</div>
            <h2>Performance Overview</h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={350}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e0e0e0" />
                  <PolarAngleAxis dataKey="skill" tick={{ fill: '#666', fontSize: 14 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: '#999' }} />
                  <Radar name="Your Scores" dataKey="value" stroke="#667eea" fill="#667eea" fillOpacity={0.6} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bar Chart */}
          <div className="report-section chart-section">
            <div className="section-icon">📈</div>
            <h2>Detailed Score Breakdown</h2>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fill: '#666', fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: '#666' }} />
                  <Tooltip 
                    contentStyle={{ background: '#fff', border: '1px solid #ddd', borderRadius: '8px' }}
                    cursor={{ fill: 'rgba(102, 126, 234, 0.1)' }}
                  />
                  <Bar dataKey="score" radius={[10, 10, 0, 0]}>
                    {barData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Score Cards */}
          <div className="report-section scores-section">
            <div className="section-icon">🎯</div>
            <h2>Your Performance Scores</h2>
            <div className="scores-grid">
              <div className="score-card" data-score={finalReport.scores.vocabulary}>
                <div className="score-icon">📚</div>
                <div className="score-label">Vocabulary</div>
                <div className="score-value">{finalReport.scores.vocabulary}</div>
                <div className="score-bar">
                  <div className="score-fill vocabulary" style={{width: `${finalReport.scores.vocabulary}%`}}></div>
                </div>
              </div>
              <div className="score-card" data-score={finalReport.scores.grammar}>
                <div className="score-icon">✍️</div>
                <div className="score-label">Grammar</div>
                <div className="score-value">{finalReport.scores.grammar}</div>
                <div className="score-bar">
                  <div className="score-fill grammar" style={{width: `${finalReport.scores.grammar}%`}}></div>
                </div>
              </div>
              <div className="score-card" data-score={finalReport.scores.fluency}>
                <div className="score-icon">💬</div>
                <div className="score-label">Fluency</div>
                <div className="score-value">{finalReport.scores.fluency}</div>
                <div className="score-bar">
                  <div className="score-fill fluency" style={{width: `${finalReport.scores.fluency}%`}}></div>
                </div>
              </div>
              <div className="score-card" data-score={finalReport.scores.pronunciation}>
                <div className="score-icon">🗣️</div>
                <div className="score-label">Pronunciation</div>
                <div className="score-value">{finalReport.scores.pronunciation}</div>
                <div className="score-bar">
                  <div className="score-fill pronunciation" style={{width: `${finalReport.scores.pronunciation}%`}}></div>
                </div>
              </div>
              <div className="score-card" data-score={finalReport.scores.confidence}>
                <div className="score-icon">💪</div>
                <div className="score-label">Confidence</div>
                <div className="score-value">{finalReport.scores.confidence}</div>
                <div className="score-bar">
                  <div className="score-fill confidence" style={{width: `${finalReport.scores.confidence}%`}}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Corrections & Missed Words */}
          {finalReport.analytics && (
            <>
              {finalReport.analytics.corrections && finalReport.analytics.corrections.length > 0 && (
                <div className="report-section corrections-section">
                  <div className="section-icon">🔧</div>
                  <h2>Grammar Corrections Needed</h2>
                  <ul className="corrections-list">
                    {finalReport.analytics.corrections.map((correction, idx) => (
                      <li key={idx}>
                        <span className="correction-icon">✏️</span>
                        {correction}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {finalReport.analytics.missed_words && finalReport.analytics.missed_words.length > 0 && (
                <div className="report-section missed-words-section">
                  <div className="section-icon">📖</div>
                  <h2>Words to Learn</h2>
                  <p className="section-description">These common words weren't used in your conversation. Try incorporating them:</p>
                  <div className="word-chips">
                    {finalReport.analytics.missed_words.map((word, idx) => (
                      <span key={idx} className="word-chip">{word}</span>
                    ))}
                  </div>
                </div>
              )}

              {finalReport.analytics.overused_words && finalReport.analytics.overused_words.length > 0 && (
                <div className="report-section overused-section">
                  <div className="section-icon">🔄</div>
                  <h2>Overused Words</h2>
                  <p className="section-description">You repeated these words frequently. Try using synonyms:</p>
                  <div className="word-chips warning">
                    {finalReport.analytics.overused_words.map((word, idx) => (
                      <span key={idx} className="word-chip warning">{word}</span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          <div className="report-section strengths-section">
            <div className="section-icon">✅</div>
            <h2>Your Strengths</h2>
            <ul className="strengths-list">
              {finalReport.strengths.map((strength, idx) => (
                <li key={idx}>
                  <span className="checkmark">✓</span>
                  {strength}
                </li>
              ))}
            </ul>
          </div>

          <div className="report-section weaknesses-section">
            <div className="section-icon">⚠️</div>
            <h2>Areas to Improve</h2>
            <ul className="weaknesses-list">
              {finalReport.weaknesses.map((weakness, idx) => (
                <li key={idx}>
                  <span className="warning-icon">➤</span>
                  {weakness}
                </li>
              ))}
            </ul>
          </div>

          <div className="report-section suggestions-section">
            <div className="section-icon">💡</div>
            <h2>Personalized Suggestions</h2>
            <ul className="suggestions-list">
              {finalReport.suggestions.map((suggestion, idx) => (
                <li key={idx}>
                  <span className="bulb-icon">💡</span>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>

          <div className="report-actions">
            <button className="btn-new-session" onClick={startNewSession}>
              <span className="btn-icon">🔄</span>
              Start New Session
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="main-container">
        <div className="chat-wrapper">
          <div className="chat-header">
            <div className="header-content">
              <div className="header-icon">🎙️</div>
              <div className="header-text">
                <h2>AI Voice Conversation Partner</h2>
                <p className="header-subtitle">Practice English naturally</p>
              </div>
            </div>
            <button className="btn-end-session" onClick={endSession}>
              <span className="btn-icon">📊</span>
              End Session & Get Report
            </button>
          </div>

          <div className="chat-messages">
            {conversation.map((msg, idx) => (
              <div key={idx} className={`message ${msg.type}-message`}>
                <div className="message-avatar">
                  {msg.type === 'ai' ? '🤖' : '👤'}
                </div>
                <div className="message-bubble">
                  <div className="message-content">{msg.text}</div>
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div className="chat-controls">
            <div className="controls-wrapper">
              <button 
                className={isActive ? "btn-listening" : "btn-speak"} 
                onClick={startListening}
                disabled={isActive}
              >
                {isActive ? (
                  <>
                    <span className="pulse-ring"></span>
                    <span className="mic-icon active">🎤</span>
                    <span className="btn-text">Listening...</span>
                  </>
                ) : (
                  <>
                    <span className="mic-icon">🎤</span>
                    <span className="btn-text">Start Speaking</span>
                    <div className="btn-ripple"></div>
                  </>
                )}
              </button>
            </div>
            <p className="hint">
              <span className="hint-icon">💡</span>
              Say "end session" when you're done to get your detailed report
            </p>
            {listeningError && <p className="hint error-hint">{listeningError}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
