import React from 'react';
import { MessageSquare, Database, Brain, Monitor } from 'lucide-react';

const ComponentPalette: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const components = [
    {
      type: 'userQuery',
      label: 'User Query',
      icon: MessageSquare,
      description: 'Accept user input and queries',
      color: '#007bff'
    },
    {
      type: 'knowledgeBase',
      label: 'Knowledge Base',
      icon: Database,
      description: 'Upload and process documents',
      color: '#28a745'
    },
    {
      type: 'llmEngine',
      label: 'LLM Engine',
      icon: Brain,
      description: 'AI model processing',
      color: '#6f42c1'
    },
    {
      type: 'output',
      label: 'Output',
      icon: Monitor,
      description: 'Display results and chat interface',
      color: '#fd7e14'
    }
  ];

  return (
    <div 
      className="component-palette"
      style={{
        width: '250px',
        background: 'white',
        borderRight: '1px solid #e0e0e0',
        padding: '1rem',
        overflowY: 'auto'
      }}
    >
      <h3 style={{ margin: '0 0 1rem 0', color: '#333', fontSize: '1rem' }}>
        Components
      </h3>
      
      <div className="palette-components">
        {components.map((component) => {
          const IconComponent = component.icon;
          
          return (
            <div
              key={component.type}
              className="palette-item"
              draggable
              onDragStart={(event) => onDragStart(event, component.type)}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '0.75rem',
                margin: '0.5rem 0',
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '6px',
                cursor: 'grab',
                transition: 'all 0.2s ease',
                userSelect: 'none'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#e9ecef';
                e.currentTarget.style.borderColor = component.color;
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.borderColor = '#dee2e6';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <IconComponent 
                size={20} 
                style={{ 
                  marginRight: '0.75rem', 
                  color: component.color,
                  flexShrink: 0
                }} 
              />
              <div>
                <div 
                  style={{ 
                    fontWeight: 600, 
                    fontSize: '0.875rem', 
                    color: '#333',
                    marginBottom: '0.25rem'
                  }}
                >
                  {component.label}
                </div>
                <div 
                  style={{ 
                    fontSize: '0.75rem', 
                    color: '#666',
                    lineHeight: '1.3'
                  }}
                >
                  {component.description}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div 
        style={{
          marginTop: '2rem',
          padding: '1rem',
          backgroundColor: '#e7f3ff',
          borderRadius: '6px',
          border: '1px solid #b3d9ff'
        }}
      >
        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: '#0066cc' }}>
          How to use:
        </h4>
        <ul style={{ margin: 0, paddingLeft: '1rem', fontSize: '0.75rem', color: '#333' }}>
          <li>Drag components onto the canvas</li>
          <li>Connect components by drawing lines between them</li>
          <li>Configure each component's settings</li>
          <li>Click "Execute Workflow" to run</li>
        </ul>
      </div>
    </div>
  );
};

export default ComponentPalette;
