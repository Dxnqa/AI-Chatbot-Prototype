import React from "react";
import ReactDOM from "react-dom/client";
import ChatPanel from "./components/ChatPanel";
import "./styles/styles.css";

const App = () => {
  return (
    <div className="app-shell">
      <ChatPanel />
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
