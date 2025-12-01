import React from "react";
import ReactDOM from "react-dom/client";
import "./styles/styles.css";

const { useMemo, useState } = React;

const initialConversation = [
  {
    id: "intro-1",
    role: "assistant",
    content:
      "Hi! I’m ready whenever you are. Send a prompt or pick one of the quick starters below.",
    timestamp: "just now",
  },
  {
    id: "intro-2",
    role: "user",
    content:
      "Give me an outline for a launch email announcing our AI assistant.",
    timestamp: "just now",
  },
  {
    id: "intro-3",
    role: "assistant",
    content:
      "Absolutely. I’ll keep the tone friendly and confident, highlight the assistant’s value, and end with a crisp CTA.",
    timestamp: "just now",
  },
];

const quickPrompts = [
  {
    id: "prompt-1",
    title: "Summarize research",
    detail: "Turn messy notes into a clear brief",
  },
  {
    id: "prompt-2",
    title: "Brainstorm angles",
    detail: "Rapid-fire ideas for campaigns",
  },
  {
    id: "prompt-3",
    title: "Rewrite copy",
    detail: "Polish tone, keep intent",
  },
];

const Chat = () => {
  const seededMessages = useMemo(() => initialConversation, []);
  const [messages, setMessages] = useState(seededMessages);
  const [message, setMessage] = useState("");
  const [isThinking, setIsThinking] = useState(false);

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

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || isThinking) return;

    pushMessage("user", trimmed);
    setMessage("");
    setIsThinking(true);

    // Placeholder for backend call – simulate response latency for UI feedback.
    setTimeout(() => {
      pushMessage(
        "assistant",
        "On it. I’ll draft a thoughtful response once the backend is connected."
      );
      setIsThinking(false);
    }, 800);
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
                  {entry.role === "user" ? "You" : "AI"}
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
              onClick={() => handlePromptSelect(prompt.title)}
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
