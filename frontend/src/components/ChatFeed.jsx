import React from "react";
import Message from "./Message";

const ChatFeed = ({ messages, isThinking }) => {
  return (
    <main className="chat-feed">
      {messages.map((entry) => (
        <Message
          key={entry.id}
          role={entry.role}
          content={entry.content}
          timestamp={entry.timestamp}
        />
      ))}
      {isThinking && (
        <article className="message message--assistant message--ghost">
          <div className="message__bubble">
            <span className="message__role">AI</span>
            <p>Thinking…</p>
          </div>
        </article>
      )}
    </main>
  );
};

export default ChatFeed;
