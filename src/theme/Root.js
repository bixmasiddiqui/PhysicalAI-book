import React from 'react';
// import ChatbotWidget from '../components/ChatbotWidget';

// Wrap the entire app with the chatbot widget
export default function Root({children}) {
  return (
    <>
      {children}
      {/* <ChatbotWidget /> */}
    </>
  );
}
