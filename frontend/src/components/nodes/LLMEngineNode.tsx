import React, { useState, useCallback } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Brain, Settings } from 'lucide-react';

interface LLMEngineData {
  label: string;
  model: string;
  apiKey: string;
  customPrompt: string;
  useWebSearch: boolean;
  temperature?: number;
}

const LLMEngineNode: React.FC<NodeProps<LLMEngineData>> = ({ data, id }) => {
  const [model, setModel] = useState(data.model || '');
  const [apiKey, setApiKey] = useState(data.apiKey || '');
  const [customPrompt, setCustomPrompt] = useState(data.customPrompt || '');
  const [useWebSearch, setUseWebSearch] = useState(data.useWebSearch || false);
  const [temperature, setTemperature] = useState(data.temperature || 0.7);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleModelChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>) => {
    const newModel = event.target.value;
    setModel(newModel);
    if (data) {
      data.model = newModel;
    }
    // Blur the select element to prevent it from sticking to cursor
    event.target.blur();
    // Stop event propagation to prevent interference with React Flow
    event.stopPropagation();
  }, [data]);

  const handlePromptChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newPrompt = event.target.value;
    setCustomPrompt(newPrompt);
    if (data) {
      data.customPrompt = newPrompt;
    }
    // Stop event propagation
    event.stopPropagation();
  }, [data]);

  const handleWebSearchToggle = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.checked;
    setUseWebSearch(newValue);
    if (data) {
      data.useWebSearch = newValue;
    }
    // Stop event propagation
    event.stopPropagation();
  }, [data]);

  const handleTemperatureChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newTemp = parseFloat(event.target.value);
    setTemperature(newTemp);
    if (data) {
      data.temperature = newTemp;
    }
    // Stop event propagation
    event.stopPropagation();
  }, [data]);

  const handleApiKeyChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newApiKey = event.target.value;
    setApiKey(newApiKey);
    if (data) {
      data.apiKey = newApiKey;
    }
    // Stop event propagation
    event.stopPropagation();
  }, [data]);

  const handleAdvancedSettingsToggle = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
    setShowAdvanced(!showAdvanced);
    // Stop event propagation to prevent node dragging
    event.stopPropagation();
  }, [showAdvanced]);

  const modelOptions = [
    { value: '', label: 'Select a model...' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'gemini-pro', label: 'Gemini Pro' },
    { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
    { value: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash' },
  ];

  return (
    <div className="node-content">
      {/* Input handles */}
      <Handle
        type="target"
        position={Position.Left}
        id="query-input"
        style={{ background: '#007bff', top: '30%' }}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="context-input"
        style={{ background: '#28a745', top: '70%' }}
      />
      
      <div className="node-header">
        <Brain className="node-icon" size={16} />
        <h3 className="node-title">LLM Engine</h3>
      </div>
      
      <div className="node-field">
        <label className="node-label" htmlFor={`model-${id}`}>
          AI Model:
        </label>
        <select
          id={`model-${id}`}
          className="node-select"
          value={model}
          onChange={handleModelChange}
        >
          {modelOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="node-field">
        <label className="node-label" htmlFor={`apikey-${id}`}>
          API Key:
        </label>
        <input
          type="password"
          id={`apikey-${id}`}
          className="node-input"
          value={apiKey}
          onChange={handleApiKeyChange}
          placeholder="Enter your API key..."
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
        <label className="node-label" htmlFor={`prompt-${id}`}>
          Custom System Prompt (Optional):
        </label>
        <textarea
          id={`prompt-${id}`}
          className="node-textarea"
          value={customPrompt}
          onChange={handlePromptChange}
          placeholder="You are a helpful AI assistant..."
          rows={3}
        />
      </div>

      <div className="node-field">
        <div className="node-checkbox-wrapper">
          <input
            type="checkbox"
            id={`websearch-${id}`}
            className="node-checkbox"
            checked={useWebSearch}
            onChange={handleWebSearchToggle}
          />
          <label htmlFor={`websearch-${id}`} className="node-label" style={{ margin: 0 }}>
            Enable Web Search
          </label>
        </div>
      </div>

      <div className="node-field">
        <button
          type="button"
          onClick={handleAdvancedSettingsToggle}
          style={{
            background: 'none',
            border: 'none',
            color: '#007bff',
            cursor: 'pointer',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem'
          }}
        >
          <Settings size={12} />
          {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
        </button>
      </div>

      {showAdvanced && (
        <div className="node-field">
          <label className="node-label" htmlFor={`temperature-${id}`}>
            Temperature: {temperature}
          </label>
          <input
            type="range"
            id={`temperature-${id}`}
            min="0"
            max="2"
            step="0.1"
            value={temperature}
            onChange={handleTemperatureChange}
            style={{ width: '100%' }}
          />
          <small style={{ color: '#666', fontSize: '0.75rem' }}>
            Lower values = more focused, Higher values = more creative
          </small>
        </div>
      )}
      
      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="response-output"
        style={{ background: '#007bff' }}
      />
    </div>
  );
};

export default LLMEngineNode;
