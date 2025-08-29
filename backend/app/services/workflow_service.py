from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from app import models
from app.services.llm_service import LLMService
from app.services.document_service import DocumentService


class WorkflowService:
    def __init__(self):
        self.llm_service = LLMService()
        self.document_service = DocumentService()

    async def execute_workflow(self, execution_id: int, db: Session) -> Dict[str, Any]:
        """Execute a workflow based on its component connections"""
        
        # Get execution record
        execution = db.query(models.WorkflowExecution).filter(
            models.WorkflowExecution.id == execution_id
        ).first()
        
        if not execution:
            return {"status": "error", "message": "Execution not found"}
        
        try:
            # Update status to running
            execution.status = "running"
            db.commit()
            
            # Get workflow and its components
            workflow = db.query(models.Workflow).filter(
                models.Workflow.id == execution.workflow_id
            ).first()
            
            if not workflow:
                execution.status = "failed"
                execution.execution_log = "Workflow not found"
                db.commit()
                return {"status": "error", "message": "Workflow not found"}
            
            # Execute workflow based on nodes and edges
            result = await self._process_workflow_nodes(
                workflow.nodes, 
                workflow.edges, 
                execution.input_data,
                execution_id,
                db
            )
            
            # Update execution record
            execution.status = "completed" if result.get("success") else "failed"
            execution.output_data = result.get("output", {})
            execution.execution_log = result.get("log", "")
            execution.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                "status": execution.status,
                "output": execution.output_data,
                "log": execution.execution_log
            }
            
        except Exception as e:
            execution.status = "failed"
            execution.execution_log = f"Execution error: {str(e)}"
            execution.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                "status": "error",
                "message": str(e)
            }

    async def _process_workflow_nodes(
        self, 
        nodes: List[Dict], 
        edges: List[Dict], 
        input_data: Dict[str, Any],
        execution_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Process workflow nodes based on their connections"""
        
        try:
            # Build adjacency list from edges
            graph = {}
            for edge in edges:
                source = edge.get("source")
                target = edge.get("target")
                if source not in graph:
                    graph[source] = []
                graph[source].append(target)
            
            # Find starting nodes (nodes with no incoming edges)
            all_targets = set()
            for targets in graph.values():
                all_targets.update(targets)
            
            start_nodes = []
            for node in nodes:
                node_id = node.get("id")
                if node_id not in all_targets:
                    start_nodes.append(node)
            
            # Process nodes in order
            node_outputs = {}
            processed = set()
            
            # Start with user query nodes
            for node in start_nodes:
                if node.get("type") == "userQuery":
                    await self._process_node(node, input_data, node_outputs, execution_id, db)
                    processed.add(node.get("id"))
            
            # Process remaining nodes based on dependencies
            while len(processed) < len(nodes):
                progress_made = False
                
                for node in nodes:
                    node_id = node.get("id")
                    if node_id in processed:
                        continue
                    
                    # Check if all dependencies are processed
                    dependencies_ready = True
                    for edge in edges:
                        if edge.get("target") == node_id and edge.get("source") not in processed:
                            dependencies_ready = False
                            break
                    
                    if dependencies_ready:
                        # Get input from connected nodes
                        node_input = self._get_node_input(node_id, edges, node_outputs, input_data)
                        await self._process_node(node, node_input, node_outputs, execution_id, db)
                        processed.add(node_id)
                        progress_made = True
                
                if not progress_made:
                    break
            
            # Find output nodes
            output_data = {}
            for node in nodes:
                if node.get("type") == "output":
                    node_id = node.get("id")
                    if node_id in node_outputs:
                        output_data[node_id] = node_outputs[node_id]
            
            return {
                "success": True,
                "output": output_data,
                "log": f"Processed {len(processed)} nodes successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": {},
                "log": f"Workflow processing error: {str(e)}"
            }

    def _get_node_input(
        self, 
        node_id: str, 
        edges: List[Dict], 
        node_outputs: Dict[str, Any], 
        initial_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get input data for a node from its connected predecessors"""
        
        node_input = {"initial_input": initial_input}
        
        for edge in edges:
            if edge.get("target") == node_id:
                source_id = edge.get("source")
                if source_id in node_outputs:
                    node_input[source_id] = node_outputs[source_id]
        
        return node_input

    async def _process_node(
        self, 
        node: Dict[str, Any], 
        input_data: Dict[str, Any], 
        node_outputs: Dict[str, Any],
        execution_id: int,
        db: Session
    ):
        """Process an individual node based on its type"""
        
        node_id = node.get("id")
        node_type = node.get("type")
        node_data = node.get("data", {})
        
        try:
            if node_type == "userQuery":
                # Extract query from input
                query = input_data.get("query", node_data.get("query", ""))
                node_outputs[node_id] = {"query": query, "type": "user_query"}
                
                # Save to chat history
                chat_message = models.ChatHistory(
                    workflow_execution_id=execution_id,
                    role="user",
                    content=query
                )
                db.add(chat_message)
                db.commit()
            
            elif node_type == "knowledgeBase":
                # Process knowledge base query
                query = ""
                for key, value in input_data.items():
                    if isinstance(value, dict) and value.get("type") == "user_query":
                        query = value.get("query", "")
                        break
                
                if query:
                    # Get document IDs and embedding API key from node configuration
                    document_ids = node_data.get("documentIds", [])
                    embedding_api_key = node_data.get("embeddingApiKey")
                    
                    if document_ids:
                        similar_content = await self.document_service.search_similar_content(
                            query, document_ids, db, embedding_api_key
                        )
                        context = "\n".join(similar_content)
                        node_outputs[node_id] = {"context": context, "type": "knowledge_base", "embedding_api_key": embedding_api_key}
                    else:
                        node_outputs[node_id] = {"context": "", "type": "knowledge_base", "embedding_api_key": embedding_api_key}
                else:
                    node_outputs[node_id] = {"context": "", "type": "knowledge_base", "embedding_api_key": node_data.get("embeddingApiKey")}
            
            elif node_type == "llmEngine":
                # Process LLM request
                query = ""
                context = ""
                
                # Extract data from connected nodes
                for key, value in input_data.items():
                    if isinstance(value, dict):
                        if value.get("type") == "user_query":
                            query = value.get("query", "")
                        elif value.get("type") == "knowledge_base":
                            context = value.get("context", "")
                
                if not query:
                    query = node_data.get("query", "What can you help me with?")
                
                # Get LLM configuration from node
                model = node_data.get("model")
                if not model:
                    raise ValueError("Model is required for LLM Engine node")
                    
                custom_prompt = node_data.get("customPrompt")
                use_web_search = node_data.get("useWebSearch", False)
                api_key = node_data.get("apiKey")
                
                # Generate response
                llm_response = await self.llm_service.generate_response(
                    query=query,
                    model=model,
                    context=context,
                    custom_prompt=custom_prompt,
                    use_web_search=use_web_search,
                    api_key=api_key
                )
                
                node_outputs[node_id] = {
                    "response": llm_response.response,
                    "sources": llm_response.sources,
                    "type": "llm_response"
                }
            
            elif node_type == "output":
                # Collect all responses for output
                response = ""
                sources = []
                
                for key, value in input_data.items():
                    if isinstance(value, dict) and value.get("type") == "llm_response":
                        response = value.get("response", "")
                        sources = value.get("sources", [])
                        break
                
                node_outputs[node_id] = {
                    "response": response,
                    "sources": sources,
                    "type": "output"
                }
                
                # Save to chat history
                chat_message = models.ChatHistory(
                    workflow_execution_id=execution_id,
                    role="assistant",
                    content=response
                )
                db.add(chat_message)
                db.commit()
        
        except Exception as e:
            node_outputs[node_id] = {
                "error": str(e),
                "type": "error"
            }
