import React, { useState } from "react";

const quickPrompts = [
  {
    id: "prompt-1",
    title: "Knowledge management - Q&A",
    detail: "Answer a question with context-based searching",
    command: "/retrieve: ",
  },
  {
    id: "prompt-2",
    title: "Ticket ingestion",
    detail: "State an issue to automatically create a ticket.",
    command: "/ingest: ",
  },
  {
    id: "prompt-3",
    title: "Web search",
    detail: "Activate web search to find answers on the internet",
    command: "/search: ",
  },
];

const QuickPrompts = ({ onPromptSelect }) => {
  const [showPrompts, setShowPrompts] = useState(false);

  return (
    <div className="quick-prompts" aria-label="Suggested prompts">
      <button
        type="button"
        className="quick-prompts__toggle"
        onClick={() => setShowPrompts((prev) => !prev)}
        aria-expanded={showPrompts}
      >
        Prompts
        <span className="quick-prompts__chevron" aria-hidden="true">
          ▾
        </span>
      </button>
      {showPrompts && (
        <div className="quick-prompts__menu" role="menu">
          {quickPrompts.map((prompt) => (
            <button
              key={prompt.id}
              className="quick-prompts__item"
              type="button"
              role="menuitem"
              onClick={() => {
                onPromptSelect(prompt.command);
                setShowPrompts(false);
              }}
              title={prompt.detail}
            >
              <strong>{prompt.title}</strong>
              <span>{prompt.detail}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default QuickPrompts;
