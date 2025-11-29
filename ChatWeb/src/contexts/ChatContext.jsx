import React, { createContext, useState, useContext } from "react";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [threadId, setThreadId] = useState(null);

  const addMessage = (message) => {
    setMessages((prev) => [...prev, message]);
  };

  const clearChat = () => {
    setMessages([]);
    setThreadId(null);
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        setMessages,
        threadId,
        setThreadId,
        addMessage,
        clearChat,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);
