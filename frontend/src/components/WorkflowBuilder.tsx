import React, { useCallback, useState, useRef } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  ReactFlowProvider,
  ReactFlowInstance,
  BackgroundVariant,
} from 'reactflow';

import UserQueryNode from './nodes/UserQueryNode';
import KnowledgeBaseNode from './nodes/KnowledgeBaseNode';
import LLMEngineNode from './nodes/LLMEngineNode';
import OutputNode from './nodes/OutputNode';
import ComponentPalette from './ComponentPalette';
import ExecutionPanel from './ExecutionPanel';

import 'reactflow/dist/style.css';
import './WorkflowBuilder.css';

const nodeTypes = {
  userQuery: UserQueryNode,
  knowledgeBase: KnowledgeBaseNode,
  llmEngine: LLMEngineNode,
  output: OutputNode,
};

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'userQuery',
    position: { x: 100, y: 100 },
    data: { label: 'User Query', query: '' },
  },
];

const initialEdges: Edge[] = [];

interface WorkflowBuilderProps {
  workflowId?: string;
}

const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({ workflowId }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onInit = useCallback((rfi: ReactFlowInstance) => {
    setReactFlowInstance(rfi);
  }, []);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = reactFlowInstance?.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: `${type}_${Date.now()}`,
        type,
        position: position || { x: 0, y: 0 },
        data: {
          label: getNodeLabel(type),
          ...getDefaultNodeData(type)
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const getNodeLabel = (type: string): string => {
    switch (type) {
      case 'userQuery': return 'User Query';
      case 'knowledgeBase': return 'Knowledge Base';
      case 'llmEngine': return 'LLM Engine';
      case 'output': return 'Output';
      default: return 'Unknown';
    }
  };

  const getDefaultNodeData = (type: string) => {
    switch (type) {
      case 'userQuery':
        return { query: '' };
      case 'knowledgeBase':
        return { documentIds: [], uploadedDocuments: [], embeddingApiKey: '' };
      case 'llmEngine':
        return { 
          model: '',
          customPrompt: '',
          useWebSearch: false,
          apiKey: ''
        };
      case 'output':
        return { response: '', sources: [] };
      default:
        return {};
    }
  };

  const saveWorkflow = async () => {
    if (!workflowId) return;

    try {
      const workflowData = {
        nodes: nodes,
        edges: edges
      };

      const response = await fetch(`http://localhost:8000/api/workflows/${workflowId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData),
      });

      if (response.ok) {
        console.log('Workflow saved successfully');
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
    }
  };

  const executeWorkflow = async () => {
    if (!workflowId || isExecuting) return;

    setIsExecuting(true);
    setExecutionResult(null);

    try {
      // Find user query node to get the initial input
      const userQueryNode = nodes.find(node => node.type === 'userQuery');
      const query = userQueryNode?.data?.query || '';

      const response = await fetch(`http://localhost:8000/api/llm/execute-workflow/${workflowId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: parseInt(workflowId),
          input_data: { query }
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setExecutionResult(result);
        
        // Poll for execution status
        if (result.execution_id) {
          await pollExecutionStatus(result.execution_id);
        }
      }
    } catch (error) {
      console.error('Error executing workflow:', error);
      setExecutionResult({ error: 'Failed to execute workflow' });
    } finally {
      setIsExecuting(false);
    }
  };

  const pollExecutionStatus = async (executionId: string) => {
    const maxPolls = 30; // 30 seconds timeout
    let polls = 0;

    const poll = async () => {
      if (polls >= maxPolls) return;

      try {
        const response = await fetch(`http://localhost:8000/api/llm/executions/${executionId}`);
        if (response.ok) {
          const status = await response.json();
          
          if (status.status === 'completed' || status.status === 'failed') {
            setExecutionResult(status);
            return;
          }
          
          polls++;
          setTimeout(poll, 1000); // Poll every second
        }
      } catch (error) {
        console.error('Error polling execution status:', error);
      }
    };

    await poll();
  };

  return (
    <div className="workflow-builder">
      <div className="builder-header">
        <h1>LLM Workflow Builder</h1>
        <div className="header-controls">
          <button onClick={saveWorkflow} className="save-btn">
            Save Workflow
          </button>
          <button 
            onClick={executeWorkflow} 
            className="execute-btn"
            disabled={isExecuting}
          >
            {isExecuting ? 'Executing...' : 'Execute Workflow'}
          </button>
        </div>
      </div>
      
      <div className="builder-content">
        <ComponentPalette />
        
        <div className="flow-container" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={onInit}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
          </ReactFlow>
        </div>

        {(isExecuting || executionResult) && (
          <ExecutionPanel 
            isExecuting={isExecuting}
            result={executionResult}
            onClose={() => setExecutionResult(null)}
          />
        )}
      </div>
    </div>
  );
};

const WorkflowBuilderWrapper: React.FC<WorkflowBuilderProps> = (props) => (
  <ReactFlowProvider>
    <WorkflowBuilder {...props} />
  </ReactFlowProvider>
);

export default WorkflowBuilderWrapper;
