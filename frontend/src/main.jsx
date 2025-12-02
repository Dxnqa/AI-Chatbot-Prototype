import React from "react";
import ReactDOM from "react-dom/client";
import "./styles/styles.css";

const { useState } = React;

const quickPrompts = [
  {
    id: "prompt-1",
    title: "Knowledge management - Q&A",
    detail: "Answer a question with context-based searching",
    command: "/retrieve: "
  },
  {
    id: "prompt-2",
    title: "Ticket ingestion",
    detail: "State an issue to automatically create a ticket.",
    command: "/ingest: "
  },
  {
    id: "prompt-3",
    title: "Web search",
    detail: "Activate web search to find answers on the internet",
    command:"/search: "
  },
];

const Chat = () => {
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

      // Update conversation ID for tracking
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

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handlePromptSelect = (prompt) => {
    setMessage(prompt);
  };

  return (
    <div className="app-shell">
      <div className="chat-panel">
        <header className="chat-panel__header">
          <div className="chat-panel__identity">
            <div className="chat-panel__avatar">P</div>
            <div>
              <p className="identity__title">Prototype</p>
              <p className="identity__meta">Knowledge base specialist</p>
            </div>
          </div>
          <button className="ghost-button" type="button">
            New chat
          </button>
        </header>

        <main className="chat-feed">
          {messages.map((entry) => (
            <article
              key={entry.id}
              className={`message message--${entry.role}`}
            >
              <div className="message__bubble">
                <span className="message__role">
                  {entry.role === "user" ? "You" : "Prototype"}
                </span>
                <p>{entry.content}</p>
              </div>
              <time>{entry.timestamp}</time>
            </article>
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

        <section className="quick-prompts" aria-label="Suggested prompts">
          {quickPrompts.map((prompt) => (
            <button
              key={prompt.id}
              className="quick-prompts__item"
              type="button"
              onClick={() => handlePromptSelect(prompt.command)}
            >
              <strong>{prompt.title}</strong>
              <span>{prompt.detail}</span>
            </button>
          ))}
        </section>

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            className="composer__input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question, outline an idea, or paste context…"
            rows={2}
          />
          <div className="composer__footer">
            <span className="composer__hint">
              Enter to send • Shift + Enter for newline
            </span>
            <button
              className="primary-button"
              type="submit"
              disabled={!message.trim() || isThinking}
            >
              {isThinking ? "Sending" : "Send"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<Chat />);
