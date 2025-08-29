import React, { useState, useCallback } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { MessageSquare } from 'lucide-react';

interface UserQueryData {
  label: string;
  query: string;
}

const UserQueryNode: React.FC<NodeProps<UserQueryData>> = ({ data, id }) => {
  const [query, setQuery] = useState(data.query || '');
  
  const handleQueryChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newQuery = event.target.value;
    setQuery(newQuery);
    
    // Update the node data
    if (data) {
      data.query = newQuery;
    }
  }, [data]);

  return (
    <div className="node-content">
      <div className="node-header">
        <MessageSquare className="node-icon" size={16} />
        <h3 className="node-title">User Query</h3>
      </div>
      
      <div className="node-field">
        <label className="node-label" htmlFor={`query-${id}`}>
          Enter your question or prompt:
        </label>
        <textarea
          id={`query-${id}`}
          className="node-textarea"
          value={query}
          onChange={handleQueryChange}
          placeholder="What would you like to know?"
          rows={3}
        />
      </div>
      
      <div className="node-field">
        <small style={{ color: '#666', fontSize: '0.75rem' }}>
          This will be the starting point of your workflow
        </small>
      </div>
      
      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="query-output"
        style={{ background: '#007bff' }}
      />
    </div>
  );
};

export default UserQueryNode;
