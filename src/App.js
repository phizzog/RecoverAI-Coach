import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import WhoopData from './components/WhoopData';
import { sendMessage, fetchWhoopData } from './services/api';
import './styles/index.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [whoopData, setWhoopData] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [currentWeekStart, setCurrentWeekStart] = useState(() => {
    // Calculate initial start date (6 days ago)
    const today = new Date();
    const sixDaysAgo = new Date(today);
    sixDaysAgo.setDate(today.getDate() - 6);
    return sixDaysAgo.toISOString().split('T')[0];
  });

  useEffect(() => {
    fetchWhoopData(currentWeekStart)
      .then(data => setWhoopData(data))
      .catch(error => console.error('Error fetching Whoop data:', error));
  }, [currentWeekStart]);

  const handleWeekChange = (newDate) => {
    setCurrentWeekStart(newDate);
  };

  const handleSendMessage = async (messageData) => {
    try {
      const userMessage = {
        type: 'user',
        text: messageData.query
      };
      setMessages(prev => [...prev, userMessage]);

      const updatedHistory = [...conversationHistory, userMessage];
      setConversationHistory(updatedHistory);

      const response = await sendMessage(messageData.query, messageData.whoopData, updatedHistory);
      
      const aiMessage = {
        type: 'ai',
        response: response.response
      };
      setMessages(prev => [...prev, aiMessage]);
      setConversationHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'error',
        response: 'Sorry, there was an error processing your message.'
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="header">
          <h1>AI Chat Assistant</h1>
        </div>
        <ChatInterface 
          messages={messages}
          onSendMessage={handleSendMessage}
          whoopData={whoopData}
        />
      </div>
      <div className="whoop-data">
        <WhoopData 
          data={whoopData} 
          onWeekChange={handleWeekChange}
          currentWeekStart={currentWeekStart}
        />
      </div>
    </div>
  );
}

export default App;