import React, { useState } from 'react';
import axios from 'axios';

const TranslateButton = ({ chapterId, originalContent }) => {
  const [loading, setLoading] = useState(false);
  const [translated, setTranslated] = useState(false);
  const [urduContent, setUrduContent] = useState(null);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState(null);

  const handleTranslate = async () => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');

    if (!token) {
      alert('Please sign in to translate content');
      window.location.href = '/auth/login';
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/translate`,
        {
          chapter_id: chapterId,
          target_language: 'urdu',
          source_content: originalContent || undefined
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setUrduContent(response.data.translated_content);
      setMetadata(response.data.metadata);
      setTranslated(true);

      // Show success message
      if (response.data.cached) {
        console.log(`Translation loaded from cache (${response.data.metadata.processing_time_ms}ms)`);
      } else {
        console.log(`Chapter translated to Urdu (${response.data.metadata.processing_time_ms}ms, ${response.data.metadata.tokens_used} tokens)`);
      }

    } catch (err) {
      console.error('Translation error:', err);

      if (err.response?.status === 401) {
        setError('Please sign in to translate content');
        localStorage.removeItem('access_token');
      } else if (err.response?.status === 404) {
        setError('Chapter not found');
      } else if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please try again later.');
      } else {
        setError(err.response?.data?.detail || 'Failed to translate content');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleShowOriginal = () => {
    setTranslated(false);
  };

  const handleShowUrdu = () => {
    setTranslated(true);
  };

  return (
    <div style={{
      margin: '20px 0',
      padding: '15px',
      background: '#f8f9fa',
      borderRadius: '8px',
      border: '1px solid #dee2e6'
    }}>
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <button
          onClick={handleTranslate}
          disabled={loading}
          style={{
            padding: '10px 20px',
            background: loading ? '#6c757d' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: '500',
            transition: 'background 0.2s'
          }}
        >
          {loading ? 'Translating to Urdu...' : 'Translate to Urdu'}
        </button>

        {urduContent && (
          <button
            onClick={translated ? handleShowOriginal : handleShowUrdu}
            style={{
              padding: '10px 20px',
              background: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500'
            }}
          >
            {translated ? 'Show English' : 'Show Urdu'}
          </button>
        )}

        {metadata && (
          <span style={{
            fontSize: '14px',
            color: '#6c757d',
            marginLeft: 'auto'
          }}>
            {metadata.cached ? '✓ Cached' : `✓ ${metadata.tokens_used} tokens`}
            {' • '}
            {metadata.processing_time_ms}ms
          </span>
        )}
      </div>

      {error && (
        <div style={{
          color: '#dc3545',
          marginTop: '10px',
          padding: '10px',
          background: '#f8d7da',
          borderRadius: '5px',
          fontSize: '14px'
        }}>
          {error}
        </div>
      )}

      {metadata?.fallback_used && (
        <div style={{
          color: '#856404',
          marginTop: '10px',
          padding: '10px',
          background: '#fff3cd',
          borderRadius: '5px',
          fontSize: '14px'
        }}>
          Translation temporarily unavailable. Showing original content.
          <br />
          <small>Reason: {metadata.fallback_reason}</small>
        </div>
      )}

      {translated && urduContent && (
        <div
          style={{
            marginTop: '20px',
            padding: '20px',
            background: 'white',
            borderRadius: '5px',
            border: '1px solid #dee2e6',
            direction: 'rtl',
            textAlign: 'right',
            fontFamily: '"Noto Nastaliq Urdu", "Traditional Arabic", serif',
            fontSize: '18px',
            lineHeight: '2'
          }}
        >
          <div
            dangerouslySetInnerHTML={{ __html: urduContent }}
            style={{
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word'
            }}
          />
        </div>
      )}

      <div style={{
        marginTop: '10px',
        fontSize: '12px',
        color: '#6c757d',
        textAlign: 'center'
      }}>
        Translation powered by {metadata?.llm_provider || 'LLM'} | Technical terms preserved in English
      </div>
    </div>
  );
};

export default TranslateButton;
