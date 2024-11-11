import React, { useEffect, useRef, useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const welcomeMessages = [
  "Welcome back. Ready to dive into your health data? Let's unlock some insights to fuel your progress. What questions can I help you answer?",
  "Curious about your recent sleep patterns or how to improve recovery? Let's explore your data and find actionable steps to reach your goals.",
  "Hi there. Need some insights on your nutrition or sleep routines? I'm here to help you make the most out of your daily habits.",
  "Let's take a look at your progress. I can help with personalized tips on sleep, diet, and recovery. What's on your mind today?",
  "Welcome. Your health data is packed with insights. I'm here to make it clear and practical. Ask me anything about sleep, nutrition, or recovery.",
  "Ready to improve your health habits? Your data holds the answers, and I can guide you through it. How can I help today?",
  "Good to see you. Let's take a closer look at your nutrition, sleep, and overall wellness. What would you like to focus on?",
  "Health and wellness are all about balance. Your data reveals the path forward, and I'm here to guide you. Let's get started with any questions you have.",
  "Here to help you make sense of your health data. From sleep quality to nutrition balance, let's find ways to optimize your journey.",
  "Let's dive into your latest health stats. I'm here to help make sense of your data and provide insights to improve your sleep, diet, and recovery.",
  "Welcome back. Your health data shows both progress and opportunity. Let's work together to keep moving toward your goals. What's your focus today?",
  "Looking to improve your wellness routines? Your data has valuable insights, and I'm here to help you understand them better. What would you like to know?",
  "Hello. I'm here to help you leverage your data for better health outcomes. Let's start with any questions about sleep, nutrition, or recovery.",
  "Let's turn your health data into actionable advice. Whether it's sleep quality, diet, or recovery, I can guide you to better habits. What's on your mind?",
  "Making sense of health data can be tricky, but I'm here to help. Let's dig into your wellness stats together. Any questions on your sleep or nutrition?",
];

const suggestedPrompts = [
  "How can I improve my sleep quality based on my recent data?",
  "What foods should I focus on to increase my daily energy levels?",
  "Is my protein intake balanced for my goals?",
  "How can I reduce the number of times I wake up during the night?",
  "What can I do to fall asleep faster?",
  "Are there any patterns in my diet that might be affecting my sleep?",
  "How does my current sleep pattern compare to recommended standards?",
  "Should I adjust my hydration routine for better recovery?",
  "How much deep sleep am I getting, and is it enough?",
  "What are the best snacks for improving focus without disrupting my sleep?",
  "How can I use my diet to speed up recovery after workouts?",
  "Why am I feeling low energy despite sleeping 7-8 hours?",
  "What are some ways to improve REM sleep based on my data?",
  "How can I use nutrition to improve my focus and concentration?",
  "What's the best timing for my meals to optimize energy and recovery?",
  "How is my sleep impacting my muscle recovery?",
  "Is there a link between my recent stress levels and my sleep quality?",
  "What changes should I consider in my diet to boost my immune system?",
  "Why am I getting drowsy in the afternoon, even when I sleep well at night?",
  "How can I improve my bedtime routine to help me sleep better?",
  "Are there specific foods that might help reduce muscle soreness?",
  "How does my sleep quality compare on weekdays vs. weekends?",
  "What should I change in my routine if I want to improve my athletic recovery?",
  "What's my average REM sleep, and how can I increase it?",
  "Can you suggest some nutrient-rich foods to add to my breakfast?",
  "How much of my sleep is spent in deep sleep vs. light sleep?",
  "Is my caffeine intake affecting my sleep? If so, how?",
  "How can I adjust my dinner timing to sleep better at night?",
  "Are there certain foods I should avoid before bed?",
  "What insights can you give me on balancing carbs, fats, and protein in my meals?",
];

function ChatInterface({ messages, onSendMessage, whoopData }) {
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [selectedPrompts] = useState(() => {
    const shuffled = [...suggestedPrompts].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, 3);
  });
  const [welcomeMessage] = useState(() => {
    return welcomeMessages[Math.floor(Math.random() * welcomeMessages.length)];
  });
  const [followUpPrompts, setFollowUpPrompts] = useState([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, isLoading, followUpPrompts]);

  const handleSendMessage = async (messageData) => {
    setIsLoading(true);
    setFollowUpPrompts([]); // Clear existing follow-up prompts
    
    try {
      await onSendMessage(messageData);
      
      // After getting the response, get follow-up questions from the response
      if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        if (lastMessage.type === 'ai' && lastMessage.response?.follow_up_questions) {
          setFollowUpPrompts(lastMessage.response.follow_up_questions);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptClick = (prompt) => {
    handleSendMessage({
      query: prompt,
      whoopData: whoopData
    });
  };

  return (
    <div className="chat-interface">
      <div className="message-list-container">
        {messages.length === 0 && (
          <div className="welcome-container">
            <div className="welcome-message">{welcomeMessage}</div>
            <div className="suggested-prompts">
              {selectedPrompts.map((prompt, index) => (
                <button
                  key={index}
                  className="prompt-button"
                  onClick={() => handlePromptClick(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}
        <MessageList messages={messages} isLoading={isLoading} />
        {!isLoading && followUpPrompts.length > 0 && (
          <div className="suggested-prompts follow-up-prompts">
            <div className="follow-up-title">Related Questions:</div>
            {followUpPrompts.map((prompt, index) => (
              <button
                key={index}
                className="prompt-button"
                onClick={() => handlePromptClick(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <MessageInput onSendMessage={handleSendMessage} whoopData={whoopData} />
    </div>
  );
}

export default ChatInterface;