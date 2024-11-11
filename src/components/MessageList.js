import React from 'react';
import Message from './Message';

const MessageList = ({ messages, isLoading, onFollowUpClick }) => {
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <Message 
          key={index} 
          message={message} 
          onFollowUpClick={onFollowUpClick}
        />
      ))}
      {isLoading && <Message isLoading={true} />}
    </div>
  );
};

export default MessageList;