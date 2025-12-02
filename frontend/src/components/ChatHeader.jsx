import React from "react";
import QuickPrompts from "./QuickPrompts";

const ChatHeader = ({ onPromptSelect, onNewChat }) => {
  return (
    <header className="chat-panel__header">
      <div className="chat-panel__identity">
        <div className="chat-panel__avatar">P</div>
        <div className="identity__body">
          <div className="identity__title-row">
            <p className="identity__title">Prototype</p>
          </div>
          <div className="identity__meta-row">
            <p className="identity__meta">Knowledge base specialist</p>
            <QuickPrompts onPromptSelect={onPromptSelect} />
          </div>
        </div>
      </div>
      <button className="ghost-button" type="button" onClick={onNewChat}>
        New chat
      </button>
    </header>
  );
};

export default ChatHeader;
