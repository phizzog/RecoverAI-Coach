import React from 'react';
import { FaUser, FaRobot } from 'react-icons/fa';
import ReactMarkdown from 'react-markdown';

function Message({ message, isLoading, onFollowUpClick }) {
  if (isLoading) {
    return (
      <div className="message ai">
        <div className="message-icon">
          <FaRobot />
        </div>
        <div className="message-content">
          Thinking...
        </div>
      </div>
    );
  }

  const { type, response, text } = message;
  const messageContent = type === 'ai' ? 
    (typeof response === 'object' ? response.response : response) : 
    text;

  const followUpQuestions = type === 'ai' && 
    typeof response === 'object' && 
    response.follow_up_questions;

  return (
    <div className={`message ${type}`}>
      <div className="message-icon">
        {type === 'user' ? <FaUser /> : <FaRobot />}
      </div>
      <div className="message-content">
        <ReactMarkdown>{messageContent || ''}</ReactMarkdown>
        {followUpQuestions && followUpQuestions.length > 0 && (
          <div className="follow-up-questions">
            <div className="follow-up-title">Related Questions:</div>
            {followUpQuestions.map((question, index) => (
              <button
                key={index}
                className="follow-up-button"
                onClick={() => onFollowUpClick(question)}
              >
                {question}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Message; 