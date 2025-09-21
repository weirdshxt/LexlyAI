import React, { useState, useRef, useEffect } from "react";
import { ApiService } from "../services/apiService";
import { SessionData, ChatMessage } from "../types";
import { format } from "date-fns";
import "../style.css";

interface ChatInterfaceProps {
  sessionData: SessionData;
  onSessionUpdate: (session: SessionData) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  sessionData,
  onSessionUpdate,
}) => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(
    sessionData?.conversationHistory || []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!sessionData?.sessionId) {
      setError("Session ID is not available. Please reload the page.");
      return;
    }
    setMessages(sessionData.conversationHistory || []);
    setError(null);
  }, [sessionData]);

  const handleSendMessage = async () => {
    if (!message.trim() || loading) return;
    if (!sessionData?.sessionId) {
      setError("Session ID is not available. Please reload the page.");
      return;
    }
    const userMessage: ChatMessage = {
      role: "user",
      content: message.trim(),
      timestamp: new Date().toISOString(),
    };
    const newMessages = [...(messages || []), userMessage];
    setMessages(newMessages);
    setMessage("");
    setLoading(true);
    setError(null);
    try {
      const response = await ApiService.chatWithDocument(
        sessionData.sessionId,
        userMessage.content
      );
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.response,
        timestamp: response.timestamp,
      };
      const updatedMessages = [...(newMessages || []), assistantMessage];
      setMessages(updatedMessages);
      const updatedSession = {
        ...sessionData,
        conversationHistory: updatedMessages,
      };
      onSessionUpdate(updatedSession);
    } catch (err: any) {
      setError(err.message || "Failed to send message");
      setMessages(messages);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setError(null);
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return format(new Date(timestamp), "HH:mm");
    } catch {
      return "";
    }
  };

  return (
    <div className="chat-root">
      <div className="chat-header">
        <div className="chat-avatar">🤖</div>
        <div>
          <div className="chat-title">Legal Assistant AI</div>
          <div className="chat-desc">Your intelligent legal document analysis companion</div>
        </div>
      </div>
      <div className="chat-info">Ask questions about the document. The AI remembers our conversation and can reference specific clauses.</div>
      <div className="chat-messages">
        {error && <div className="chat-alert error">{error}</div>}
        {messages.length === 0 ? (
          <div className="chat-empty">Start a conversation by asking a question about the document...</div>
        ) : (
          <ul className="chat-message-list">
            {messages.map((msg, index) => (
              <li key={index} className={`chat-message-item ${msg.role}`}>
                <div className="chat-message-avatar">{msg.role === "user" ? "🧑" : "🤖"}</div>
                <div className="chat-message-content">
                  <div className="chat-message-text">{msg.content}</div>
                  <div className="chat-message-time">{formatTimestamp(msg.timestamp)}</div>
                </div>
              </li>
            ))}
            {loading && (
              <li className="chat-message-item assistant">
                <div className="chat-message-avatar">🤖</div>
                <div className="chat-message-content">
                  <div className="chat-message-text">AI is thinking...</div>
                </div>
              </li>
            )}
            <div ref={messagesEndRef} />
          </ul>
        )}
      </div>
      <div className="chat-input-section">
        <textarea
          className="chat-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask any question about your legal document..."
          disabled={loading}
          rows={2}
        />
        <button className="chat-send-btn" onClick={handleSendMessage} disabled={loading || !message.trim()}>
          Send
        </button>
        <button className="chat-clear-btn" onClick={clearConversation} title="Clear conversation" disabled={loading}>
          Clear
        </button>
      </div>
      <div className="chat-hint">Press Enter to send, Shift + Enter for new line</div>
      {messages.length === 0 && (
        <div className="chat-suggestions">
          <div className="chat-suggestions-title">Suggested Questions:</div>
          <div className="chat-suggestions-list">
            {["What is this document about?","What are the main terms and conditions?","What are my obligations?","What happens if I terminate early?","What are the payment terms?","Are there any penalties?"].map((suggestion, index) => (
              <button key={index} className="chat-suggestion-btn" onClick={() => setMessage(suggestion)}>{suggestion}</button>
            ))}
          </div>
        </div>
      )}
      <div className="chat-context-info">
        <strong>Context:</strong> This chat is connected to "{sessionData.documentName}". The AI can reference specific clauses and maintains conversation memory.
      </div>
    </div>
  );
};

export default ChatInterface;
