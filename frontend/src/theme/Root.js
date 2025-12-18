import React from 'react';
import ChatbotWidget from '../components/ChatbotWidget';

// Wrap the entire app with the chatbot widget
// This makes the chatbot available on every page
export default function Root({children}) {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}
