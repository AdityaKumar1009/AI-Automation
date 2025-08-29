import React, { useState, useEffect } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Monitor, ExternalLink, Copy, MessageCircle } from 'lucide-react';

interface OutputData {
  label: string;
  response: string;
  sources: string[];
  chatHistory?: Array<{
    role: string;
    content: string;
    timestamp: string;
  }>;
}

const OutputNode: React.FC<NodeProps<OutputData>> = ({ data, id }) => {
  const [response, setResponse] = useState(data.response || '');
  const [sources, setSources] = useState(data.sources || []);
  const [showChat, setShowChat] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [chatHistory, setChatHistory] = useState(data.chatHistory || []);

  useEffect(() => {
    setResponse(data.response || '');
    setSources(data.sources || []);
  }, [data.response, data.sources]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      // You could add a toast notification here
      console.log('Copied to clipboard');
    });
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    // Add user message to chat history
    const userMessage = {
      role: 'user',
      content: newMessage,
      timestamp: new Date().toISOString()
    };

    setChatHistory(prev => [...prev, userMessage]);
    setNewMessage('');

    // Here you would typically send the follow-up question through the workflow
    // For now, we'll just simulate a response
    setTimeout(() => {
      const assistantMessage = {
        role: 'assistant',
        content: 'This is a follow-up response. In a real implementation, this would re-run the workflow with the new question.',
        timestamp: new Date().toISOString()
      };
      setChatHistory(prev => [...prev, assistantMessage]);
    }, 1000);
  };

  return (
    <div className="node-content">
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="response-input"
        style={{ background: '#007bff' }}
      />
      
      <div className="node-header">
        <Monitor className="node-icon" size={16} />
        <h3 className="node-title">Output</h3>
      </div>
      
      {response && (
        <div className="node-field">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label className="node-label">Response:</label>
            <button
              onClick={() => copyToClipboard(response)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#007bff',
                padding: '2px'
              }}
              title="Copy response"
            >
              <Copy size={12} />
            </button>
          </div>
          <div 
            className="response-content"
            style={{
              padding: '0.75rem',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              border: '1px solid #e9ecef',
              maxHeight: '200px',
              overflowY: 'auto',
              fontSize: '0.875rem',
              lineHeight: '1.4',
              whiteSpace: 'pre-wrap'
            }}
          >
            {response}
          </div>
        </div>
      )}

      {sources.length > 0 && (
        <div className="node-field">
          <label className="node-label">Sources:</label>
          <div className="sources-list">
            {sources.slice(0, 3).map((source, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '0.25rem' }}>
                <ExternalLink size={10} style={{ marginRight: '0.25rem', color: '#666' }} />
                <a
                  href={source}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: '0.75rem',
                    color: '#007bff',
                    textDecoration: 'none',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    maxWidth: '150px'
                  }}
                >
                  {source}
                </a>
              </div>
            ))}
            {sources.length > 3 && (
              <small style={{ color: '#666' }}>
                +{sources.length - 3} more sources
              </small>
            )}
          </div>
        </div>
      )}

      <div className="node-field">
        <button
          onClick={() => setShowChat(!showChat)}
          style={{
            background: showChat ? '#007bff' : 'transparent',
            color: showChat ? 'white' : '#007bff',
            border: '1px solid #007bff',
            borderRadius: '4px',
            padding: '0.5rem',
            cursor: 'pointer',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            width: '100%',
            justifyContent: 'center'
          }}
        >
          <MessageCircle size={12} />
          {showChat ? 'Hide Chat' : 'Show Chat Interface'}
        </button>
      </div>

      {showChat && (
        <div className="node-field">
          <div 
            className="chat-container"
            style={{
              border: '1px solid #ddd',
              borderRadius: '4px',
              height: '200px',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div 
              className="chat-messages"
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '0.5rem',
                backgroundColor: '#fafafa'
              }}
            >
              {chatHistory.map((message, index) => (
                <div 
                  key={index}
                  style={{
                    marginBottom: '0.5rem',
                    padding: '0.5rem',
                    borderRadius: '4px',
                    backgroundColor: message.role === 'user' ? '#e3f2fd' : '#f5f5f5',
                    fontSize: '0.75rem'
                  }}
                >
                  <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </div>
                  <div>{message.content}</div>
                </div>
              ))}
            </div>
            
            <div 
              className="chat-input"
              style={{
                display: 'flex',
                padding: '0.5rem',
                borderTop: '1px solid #ddd'
              }}
            >
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Ask a follow-up question..."
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                style={{
                  flex: 1,
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  padding: '0.25rem 0.5rem',
                  fontSize: '0.75rem',
                  marginRight: '0.5rem'
                }}
              />
              <button
                onClick={handleSendMessage}
                disabled={!newMessage.trim()}
                style={{
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '0.25rem 0.5rem',
                  fontSize: '0.75rem',
                  cursor: 'pointer'
                }}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OutputNode;
