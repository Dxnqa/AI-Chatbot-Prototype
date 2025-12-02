import React from "react";

const Composer = ({ message, setMessage, onSubmit, isThinking }) => {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  return (
    <form className="composer" onSubmit={onSubmit}>
      <div className="composer__input-wrapper">
        <textarea
          className="composer__input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question, outline an idea, or paste context…"
          rows={2}
        />
        <button
          className="composer__submit"
          type="submit"
          disabled={!message.trim() || isThinking}
        >
          {isThinking ? "Sending" : "Send"}
        </button>
      </div>
      <span className="composer__hint">
        Enter to send • Shift + Enter for newline
      </span>
    </form>
  );
};

export default Composer;
