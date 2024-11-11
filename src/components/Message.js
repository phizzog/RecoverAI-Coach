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
  
  // Handle both string and object responses
  const messageContent = type === 'ai' ? 
    (typeof response === 'object' ? response.response : response) : 
    text;

  // Extract follow-up questions and ensure it's an array
  const followUpQuestions = type === 'ai' && 
    typeof response === 'object' && 
    Array.isArray(response.follow_up_questions) ? 
    response.follow_up_questions : [];

  // Remove markdown formatting from follow-up questions if present
  const cleanFollowUpQuestions = followUpQuestions.map(question => 
    question
      .replace(/\*\*/g, '') // Remove all asterisks
      .replace(/^(First|Second|Third)\s*user\s*question:\s*/i, '') // Remove "First/Second/Third user question:" prefix
      .trim()
  );

  return (
    <div className={`message ${type}`}>
      <div className="message-icon">
        {type === 'user' ? <FaUser /> : <FaRobot />}
      </div>
      <div className="message-content">
        <ReactMarkdown>{messageContent || ''}</ReactMarkdown>
        {cleanFollowUpQuestions.length > 0 && onFollowUpClick && (
          <div className="follow-up-questions">
            <div className="follow-up-title">Related Questions:</div>
            {cleanFollowUpQuestions.map((question, index) => (
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