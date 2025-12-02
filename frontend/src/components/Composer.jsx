import React, { useState, useRef, useEffect } from "react";

const actionOptions = [
  { id: "retrieve", label: "Retrieve", command: "/retrieve: " },
  { id: "search", label: "Search", command: "/search: " },
  { id: "ingest", label: "Ingest", command: "/ingest: " },
];

const Composer = ({ message, setMessage, onSubmit, isThinking }) => {
  const [showActions, setShowActions] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea as content changes
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [message]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  const handleActionSelect = (command) => {
    setMessage(command);
    setShowActions(false);
  };

  return (
    <form className="composer" onSubmit={onSubmit}>
      <div className="composer__input-wrapper">
        <button
          type="button"
          className="composer__actions-toggle"
          onClick={() => setShowActions((prev) => !prev)}
          aria-expanded={showActions}
          aria-label="Actions menu"
        >
          +
        </button>
        {showActions && (
          <div className="composer__actions-dropdown" role="menu">
            {actionOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                className="composer__action-item"
                role="menuitem"
                onClick={() => handleActionSelect(option.command)}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
        <textarea
          ref={textareaRef}
          className="composer__input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question"
          rows={1}
          maxLength={1500}
        />
        <button
          className="composer__submit"
          type="submit"
          disabled={!message.trim() || isThinking}
          aria-label="Send message"
        >
          ↑
        </button>
      </div>
      <span className="composer__hint">
        Enter to send • Shift + Enter for newline
      </span>
    </form>
  );
};

export default Composer;
