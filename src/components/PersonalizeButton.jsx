import React, { useState } from 'react';
import axios from 'axios';

const PersonalizeButton = ({ chapterId }) => {
  const [loading, setLoading] = useState(false);
  const [personalized, setPersonalized] = useState(false);
  const [content, setContent] = useState(null);
  const [error, setError] = useState(null);

  const handlePersonalize = async () => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');

    if (!token) {
      alert('Please sign in to personalize content');
      // Redirect to login
      window.location.href = '/auth/login';
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/personalize`,
        { chapter_id: chapterId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setContent(response.data.content);
      setPersonalized(true);

      // Show success message
      if (response.data.cached) {
        console.log(`Personalized content loaded from cache (${response.data.metadata.processing_time_ms}ms)`);
      } else {
        console.log(`Content personalized (${response.data.metadata.processing_time_ms}ms)`);
      }

    } catch (err) {
      console.error('Personalization error:', err);

      if (err.response?.status === 401) {
        setError('Please sign in to personalize content');
        localStorage.removeItem('access_token');
      } else if (err.response?.status === 404) {
        setError('Chapter not found');
      } else {
        setError(err.response?.data?.detail || 'Failed to personalize content');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = () => {
    setPersonalized(!personalized);
  };

  return (
    <div style={{ margin: '20px 0', padding: '15px', background: '#f0f0f0', borderRadius: '8px' }}>
      <button
        onClick={handlePersonalize}
        disabled={loading}
        style={{
          padding: '10px 20px',
          background: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: '16px'
        }}
      >
        {loading ? 'Personalizing...' : 'Personalize This Chapter'}
      </button>

      {personalized && (
        <button
          onClick={handleToggle}
          style={{
            padding: '10px 20px',
            background: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            marginLeft: '10px',
            fontSize: '16px'
          }}
        >
          {personalized ? 'Show Original' : 'Show Personalized'}
        </button>
      )}

      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          {error}
        </div>
      )}

      {personalized && content && (
        <div style={{ marginTop: '20px', padding: '15px', background: 'white', borderRadius: '5px' }}>
          <h3>Personalized Content:</h3>
          <div dangerouslySetInnerHTML={{ __html: content }} />
        </div>
      )}
    </div>
  );
};

export default PersonalizeButton;
