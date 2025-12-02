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
  );
};

export default Composer;
