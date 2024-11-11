import React, { useState } from 'react';
import { IoSend } from 'react-icons/io5';

function MessageInput({ onSendMessage, whoopData }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage({
        query: message,
        whoopData: whoopData
      });
      setMessage('');
    }
  };

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <div className="input-container">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="message-input-field"
        />
        <button type="submit" className="send-button" disabled={!message.trim()}>
          <IoSend />
        </button>
      </div>
    </form>
  );
}

export default MessageInput;