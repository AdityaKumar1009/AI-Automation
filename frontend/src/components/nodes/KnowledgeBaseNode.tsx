import React, { useState, useCallback, useRef } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Database, Upload, FileText, X } from 'lucide-react';

interface KnowledgeBaseData {
  label: string;
  documentIds: number[];
  embeddingApiKey: string;
  uploadedDocuments: Array<{
    id: number;
    name: string;
    size: number;
    status: 'uploading' | 'processing' | 'ready' | 'error';
  }>;
}

const KnowledgeBaseNode: React.FC<NodeProps<KnowledgeBaseData>> = ({ data, id }) => {
  const [documents, setDocuments] = useState(data.uploadedDocuments || []);
  const [isUploading, setIsUploading] = useState(false);
  const [embeddingApiKey, setEmbeddingApiKey] = useState(data.embeddingApiKey || '');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    // Stop event propagation to prevent interference with React Flow
    event.stopPropagation();
    setIsUploading(true);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Add document to local state with uploading status
      const tempDoc = {
        id: Date.now() + i,
        name: file.name,
        size: file.size,
        status: 'uploading' as const
      };
      
      setDocuments(prev => [...prev, tempDoc]);

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('embedding_api_key', embeddingApiKey);

        const response = await fetch('http://localhost:8000/api/documents/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const uploadedDoc = await response.json();
          
          // Update document status
          setDocuments(prev => prev.map(doc => 
            doc.id === tempDoc.id 
              ? { ...doc, id: uploadedDoc.id, status: 'ready' }
              : doc
          ));
          
          // Update node data
          if (data) {
            data.documentIds = [...(data.documentIds || []), uploadedDoc.id];
            data.uploadedDocuments = documents.map(doc => 
              doc.id === tempDoc.id 
                ? { ...doc, id: uploadedDoc.id, status: 'ready' }
                : doc
            );
          }
        } else {
          // Update document status to error
          setDocuments(prev => prev.map(doc => 
            doc.id === tempDoc.id 
              ? { ...doc, status: 'error' }
              : doc
          ));
        }
      } catch (error) {
        console.error('Upload error:', error);
        setDocuments(prev => prev.map(doc => 
          doc.id === tempDoc.id 
            ? { ...doc, status: 'error' }
            : doc
        ));
      }
    }

    setIsUploading(false);
    
    // Clear the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [data, documents, embeddingApiKey]);

  const handleEmbeddingApiKeyChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newApiKey = event.target.value;
    setEmbeddingApiKey(newApiKey);
    if (data) {
      data.embeddingApiKey = newApiKey;
    }
    // Stop event propagation
    event.stopPropagation();
  }, [data]);

  const removeDocument = useCallback((docId: number) => {
    setDocuments(prev => prev.filter(doc => doc.id !== docId));
    
    if (data) {
      data.documentIds = data.documentIds?.filter(id => id !== docId) || [];
      data.uploadedDocuments = data.uploadedDocuments?.filter(doc => doc.id !== docId) || [];
    }
  }, [data]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'uploading': return '#ffc107';
      case 'processing': return '#17a2b8';
      case 'ready': return '#28a745';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="node-content">
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="query-input"
        style={{ background: '#007bff' }}
      />
      
      <div className="node-header">
        <Database className="node-icon" size={16} />
        <h3 className="node-title">Knowledge Base</h3>
      </div>
      
      <div className="node-field">
        <label className="node-label" htmlFor={`embedding-apikey-${id}`}>
          Gemini API Key (for embeddings):
        </label>
        <input
          type="password"
          id={`embedding-apikey-${id}`}
          className="node-input"
          value={embeddingApiKey}
          onChange={handleEmbeddingApiKeyChange}
          placeholder="Enter your Gemini API key..."
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '0.875rem'
          }}
        />
      </div>
      
      <div className="node-field">
        <label className="node-label">
          Upload Documents:
        </label>
        <div 
          className="upload-area"
          style={{
            border: '2px dashed #ddd',
            borderRadius: '4px',
            padding: '1rem',
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: isUploading ? '#f8f9fa' : 'transparent'
          }}
          onClick={(e) => {
            e.stopPropagation();
            fileInputRef.current?.click();
          }}
        >
          <Upload size={20} style={{ marginBottom: '0.5rem', color: '#666' }} />
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#666' }}>
            {isUploading ? 'Uploading...' : 'Click to upload documents'}
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.md,.docx"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
        </div>
      </div>

      {documents.length > 0 && (
        <div className="node-field">
          <label className="node-label">Uploaded Documents:</label>
          <div className="document-list" style={{ maxHeight: '150px', overflowY: 'auto' }}>
            {documents.map((doc) => (
              <div 
                key={doc.id} 
                className="document-item"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.5rem',
                  margin: '0.25rem 0',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '4px',
                  fontSize: '0.75rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  <FileText size={12} style={{ marginRight: '0.25rem' }} />
                  <div>
                    <div style={{ fontWeight: 500 }}>{doc.name}</div>
                    <div style={{ color: '#666' }}>
                      {formatFileSize(doc.size)} • 
                      <span style={{ color: getStatusColor(doc.status), marginLeft: '4px' }}>
                        {doc.status}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeDocument(doc.id);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#666',
                    padding: '2px'
                  }}
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="context-output"
        style={{ background: '#007bff' }}
      />
    </div>
  );
};

export default KnowledgeBaseNode;
