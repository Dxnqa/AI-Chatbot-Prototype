import React from "react";

const Message = ({ role, content, timestamp }) => {
  return (
    <article className={`message message--${role}`}>
      <div className="message__bubble">
        <span className="message__role">
          {role === "user" ? "You" : "Prototype"}
        </span>
        <p>{content}</p>
      </div>
      <time>{timestamp}</time>
    </article>
  );
};

export default Message;
