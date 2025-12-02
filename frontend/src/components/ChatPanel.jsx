import React, { useState } from "react";
import ChatHeader from "./ChatHeader";
import ChatFeed from "./ChatFeed";
import Composer from "./Composer";

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [conversationId, setConversationId] = useState(null);

  const pushMessage = (role, content) => {
    setMessages((prev) => [
      ...prev,
      {
        id: `${role}-${Date.now()}`,
        role,
        content,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isThinking) return;

    pushMessage("user", trimmed);
    setMessage("");
    setIsThinking(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmed,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      pushMessage("assistant", data.response);
    } catch (error) {
      console.error("Chat API error:", error);
      pushMessage(
        "assistant",
        "Sorry, something went wrong. Please try again."
      );
    } finally {
      setIsThinking(false);
    }
  };

  const handlePromptSelect = (prompt) => {
    setMessage(prompt);
  };

  const handleNewChat = () => {
    setMessages([]);
    setMessage("");
    setConversationId(null);
  };

  return (
    <div className="chat-panel">
      <ChatHeader
        onPromptSelect={handlePromptSelect}
        onNewChat={handleNewChat}
      />
      <ChatFeed messages={messages} isThinking={isThinking} />
      <Composer
        message={message}
        setMessage={setMessage}
        onSubmit={handleSubmit}
        isThinking={isThinking}
      />
    </div>
  );
};

export default ChatPanel;
