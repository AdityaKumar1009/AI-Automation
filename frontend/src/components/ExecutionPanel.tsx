import React from 'react';
import { X, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface ExecutionPanelProps {
  isExecuting: boolean;
  result: any;
  onClose: () => void;
}

const ExecutionPanel: React.FC<ExecutionPanelProps> = ({ isExecuting, result, onClose }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} style={{ color: '#28a745' }} />;
      case 'failed':
        return <XCircle size={16} style={{ color: '#dc3545' }} />;
      case 'running':
        return <Clock size={16} style={{ color: '#007bff' }} />;
      default:
        return <AlertCircle size={16} style={{ color: '#ffc107' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#28a745';
      case 'failed': return '#dc3545';
      case 'running': return '#007bff';
      default: return '#ffc107';
    }
  };

  return (
    <div
      className="execution-panel"
      style={{
        position: 'fixed',
        top: '80px',
        right: '20px',
        width: '400px',
        maxHeight: 'calc(100vh - 100px)',
        backgroundColor: 'white',
        border: '1px solid #ddd',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '1rem',
          borderBottom: '1px solid #eee'
        }}
      >
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>
          Workflow Execution
        </h3>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: '#666',
            padding: '4px'
          }}
        >
          <X size={16} />
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
        {isExecuting && (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div
              className="spinner"
              style={{
                width: '40px',
                height: '40px',
                border: '3px solid #f3f3f3',
                borderTop: '3px solid #007bff',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 1rem'
              }}
            />
            <p style={{ margin: 0, color: '#666' }}>
              Executing workflow...
            </p>
          </div>
        )}

        {result && (
          <div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '1rem',
                padding: '0.75rem',
                backgroundColor: '#f8f9fa',
                borderRadius: '4px',
                border: `1px solid ${getStatusColor(result.status)}20`
              }}
            >
              {getStatusIcon(result.status)}
              <span style={{ fontWeight: 500, textTransform: 'capitalize' }}>
                {result.status}
              </span>
            </div>

            {result.execution_id && (
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ fontSize: '0.875rem', color: '#666' }}>
                  Execution ID:
                </strong>
                <div style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#333' }}>
                  {result.execution_id}
                </div>
              </div>
            )}

            {result.output_data && Object.keys(result.output_data).length > 0 && (
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ fontSize: '0.875rem', color: '#666', display: 'block', marginBottom: '0.5rem' }}>
                  Output:
                </strong>
                <div
                  style={{
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    padding: '0.75rem',
                    fontSize: '0.875rem',
                    maxHeight: '200px',
                    overflowY: 'auto'
                  }}
                >
                  {Object.entries(result.output_data).map(([key, value]: [string, any]) => (
                    <div key={key} style={{ marginBottom: '0.5rem' }}>
                      <strong>{key}:</strong>
                      {typeof value === 'object' ? (
                        <pre style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>
                          {JSON.stringify(value, null, 2)}
                        </pre>
                      ) : (
                        <div style={{ marginTop: '0.25rem' }}>
                          {String(value)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.execution_log && (
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ fontSize: '0.875rem', color: '#666', display: 'block', marginBottom: '0.5rem' }}>
                  Execution Log:
                </strong>
                <div
                  style={{
                    backgroundColor: '#f8f9fa',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    padding: '0.75rem',
                    fontSize: '0.75rem',
                    fontFamily: 'monospace',
                    maxHeight: '150px',
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {result.execution_log}
                </div>
              </div>
            )}

            {result.error && (
              <div
                style={{
                  backgroundColor: '#f8d7da',
                  border: '1px solid #f5c6cb',
                  borderRadius: '4px',
                  padding: '0.75rem',
                  color: '#721c24',
                  fontSize: '0.875rem'
                }}
              >
                <strong>Error:</strong> {result.error}
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ExecutionPanel;
