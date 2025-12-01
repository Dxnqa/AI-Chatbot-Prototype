import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';

const { useState } = React;

const Chat = () => {
    const [message, setMessage] = useState('');
    
    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim()) {
            console.log('Message submitted:', message);
            // TODO: Add API call here to send message to backend
            setMessage('');
        }
    };
    
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };
    
    return (
        <div className="chat-container">
            <div className="chat-header">
                <h1>AI Chatbot</h1>
            </div>
            
            <div className="chat-messages">
                {/* Messages will be displayed here */}
            </div>
            
            <form className="chat-input-form" onSubmit={handleSubmit}>
                <textarea
                    className="chat-textarea"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                    rows={3}
                />
                <button 
                    type="submit" 
                    className="chat-submit-button"
                    disabled={!message.trim()}
                >
                    Send
                </button>
            </form>
        </div>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Chat />);