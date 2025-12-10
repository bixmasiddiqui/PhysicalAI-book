import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function ChatbotWidget({ chapter }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentChapter, setCurrentChapter] = useState(chapter);
  const messagesEndRef = useRef(null);

  // Listen for chapter button clicks
  useEffect(() => {
    const handleOpenChatbot = (e) => {
      setCurrentChapter(e.detail?.chapter);
      setIsOpen(true);
    };

    window.addEventListener('openChatbot', handleOpenChatbot);
    return () => window.removeEventListener('openChatbot', handleOpenChatbot);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    // Try to connect to backend, fallback to mock response
    try {
      const response = await axios.post(`${API_BASE_URL}/ask`, {
        message: userMessage,
        chapter: chapter || null,
        user_id: localStorage.getItem('userId') || 'anonymous'
      }, { timeout: 5000 });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources
      }]);
    } catch (error) {
      console.log('Backend unavailable, using mock response:', error.message);
      // Mock response when backend is unavailable
      setTimeout(() => {
        const mockResponse = getMockResponse(userMessage);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: mockResponse,
          sources: [{ title: 'Mock Response', type: 'demo' }]
        }]);
        setIsLoading(false);
      }, 1000);
      return;
    }
    setIsLoading(false);
  };

  const getMockResponse = (question) => {
    const q = question.toLowerCase();
    if (q.includes('physical ai') || q.includes('what is')) {
      return 'Physical AI represents the convergence of artificial intelligence and robotics, enabling machines to perceive, reason about, and interact with the physical world. It combines perception systems, reasoning & planning, actuation & control, and learning systems.\n\n(Note: This is a demo response. The AI backend will provide detailed answers once configured.)';
    } else if (q.includes('humanoid') || q.includes('robot')) {
      return 'Humanoid robots are designed to operate in environments built for humans. They are particularly useful in healthcare, manufacturing, service industries, disaster response, and space exploration.\n\n(Note: This is a demo response. The AI backend will provide detailed answers once configured.)';
    } else if (q.includes('career') || q.includes('job')) {
      return 'Career opportunities in Physical AI include: AI Robotics Engineer, Motion Planning Specialist, Computer Vision Engineer, Human-Robot Interaction Designer, and AI Safety Researcher.\n\n(Note: This is a demo response. The AI backend will provide detailed answers once configured.)';
    } else {
      return `I understand you're asking about "${question}". This is a demo mode - the AI chatbot will provide comprehensive answers about Physical AI and Humanoid Robotics once the backend is fully configured.\n\nFor now, try asking about:\n- What is Physical AI?\n- Humanoid robots applications\n- Career opportunities in robotics`;
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Toggle Button */}
      <div className="chatbot-widget">
        <button
          className="chatbot-toggle"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle Chatbot"
        >
          {isOpen ? '✕' : '💬'}
        </button>
      </div>

      {/* Chat Modal */}
      {isOpen && (
        <div className="chatbot-modal">
          {/* Header */}
          <div className="chatbot-header">
            <h3>🤖 AI Teaching Assistant</h3>
            {currentChapter && <p style={{ fontSize: '12px', margin: '5px 0 0 0' }}>
              Asking about: {currentChapter}
            </p>}
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.length === 0 && (
              <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                <p>👋 Hi! I'm your AI assistant for this textbook.</p>
                <p>Ask me anything about Physical AI and Robotics!</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx}>
                <div className={`message ${msg.role}`}>
                  <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                </div>

                {msg.sources && msg.sources.length > 0 && (
                  <div style={{ fontSize: '11px', color: '#666', marginTop: '5px', padding: '0 15px' }}>
                    📚 Sources: {msg.sources.map(s => s.title).join(', ')}
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div>Thinking...</div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chatbot-input-area">
            <textarea
              className="chatbot-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              rows="2"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              style={{
                marginTop: '10px',
                padding: '10px 20px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: input.trim() ? 'pointer' : 'not-allowed',
                opacity: input.trim() ? 1 : 0.5
              }}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
