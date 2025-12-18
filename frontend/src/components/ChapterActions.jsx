import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function ChapterActions({ chapter, onPersonalize, onTranslate }) {
  const [isPersonalizing, setIsPersonalizing] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [showSelectedTextQuery, setShowSelectedTextQuery] = useState(false);

  const handlePersonalize = async () => {
    setIsPersonalizing(true);
    try {
      // Call personalization API
      const userId = localStorage.getItem('userId') || 'anonymous';
      const response = await axios.post(`${API_BASE_URL}/personalize`, {
        chapter,
        user_id: userId
      }, { timeout: 5000 });

      if (onPersonalize) {
        onPersonalize(response.data.personalized_content);
      }
      alert('Chapter personalized successfully! (Backend integration in progress)');
    } catch (error) {
      console.log('Personalization backend unavailable:', error.message);
      alert('✨ Personalization Feature\n\nThis feature will adapt the chapter content to your learning level and background. The AI backend will personalize:\n\n• Technical depth based on your experience\n• Examples relevant to your field\n• Pace adjusted to your knowledge\n\n(Demo mode - Backend configuration needed)');
    } finally {
      setIsPersonalizing(false);
    }
  };

  const handleTranslate = async () => {
    setIsTranslating(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/translate`, {
        chapter,
        target_language: 'ur'
      }, { timeout: 5000 });

      if (onTranslate) {
        onTranslate(response.data.translated_content);
      }

      // Optionally redirect to Urdu version
      window.location.href = `/ur/docs/${chapter}`;
    } catch (error) {
      console.log('Translation backend unavailable:', error.message);
      alert('🌐 Translation Feature\n\nThis will translate the entire chapter to Urdu, making the content accessible to Urdu speakers.\n\nFeatures:\n• Full chapter translation\n• Technical term explanations\n• Right-to-left (RTL) layout support\n\n(Demo mode - Backend configuration needed)');
    } finally {
      setIsTranslating(false);
    }
  };

  const handleTextSelection = () => {
    const selection = window.getSelection();
    const text = selection.toString();

    if (text.length > 10) {
      setSelectedText(text);
      setShowSelectedTextQuery(true);
    }
  };

  // Add event listener for text selection
  React.useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
    };
  }, []);

  const handleAskAboutSelection = async (question) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ask-selected-text`, {
        selected_text: selectedText,
        question,
        user_id: localStorage.getItem('userId') || 'anonymous'
      });

      alert(response.data.answer);
    } catch (error) {
      console.error('Error querying selected text:', error);
    }
  };

  return (
    <>
      <div className="chapter-actions">
        <button
          className="ai-button chat-button"
          onClick={() => window.dispatchEvent(new CustomEvent('openChatbot', { detail: { chapter } }))}
        >
          💬 Ask Questions from This Chapter
        </button>

        <button
          className="ai-button personalize-button"
          onClick={handlePersonalize}
          disabled={isPersonalizing}
        >
          {isPersonalizing ? '⏳ Personalizing...' : '✨ Personalize this Chapter for Me'}
        </button>

        <button
          className="ai-button translate-button"
          onClick={handleTranslate}
          disabled={isTranslating}
        >
          {isTranslating ? '⏳ Translating...' : '🌐 Translate to Urdu'}
        </button>
      </div>

      {/* Selected Text Query Popup */}
      {showSelectedTextQuery && selectedText && (
        <div
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            background: 'white',
            padding: '15px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            maxWidth: '300px',
            zIndex: 1001
          }}
        >
          <button
            onClick={() => setShowSelectedTextQuery(false)}
            style={{
              position: 'absolute',
              top: '5px',
              right: '5px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '18px'
            }}
          >
            ×
          </button>
          <h4 style={{ marginTop: 0 }}>Ask about selection</h4>
          <p style={{ fontSize: '12px', color: '#666', maxHeight: '60px', overflow: 'hidden' }}>
            "{selectedText.substring(0, 100)}..."
          </p>
          <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
            <button
              className="ai-button"
              style={{ fontSize: '12px', padding: '8px 12px' }}
              onClick={() => handleAskAboutSelection('Explain this in simple terms')}
            >
              Explain
            </button>
            <button
              className="ai-button"
              style={{ fontSize: '12px', padding: '8px 12px' }}
              onClick={() => handleAskAboutSelection('Give me an example')}
            >
              Example
            </button>
          </div>
        </div>
      )}
    </>
  );
}
