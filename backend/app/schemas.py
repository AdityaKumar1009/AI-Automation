from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ComponentBase(BaseModel):
    type: str
    name: str
    config: Optional[Dict[str, Any]] = {}
    position_x: int = 0
    position_y: int = 0


class ComponentCreate(ComponentBase):
    workflow_id: int


class ComponentUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None


class Component(ComponentBase):
    id: int
    workflow_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = ""
    nodes: Optional[List[Dict[str, Any]]] = []
    edges: Optional[List[Dict[str, Any]]] = []


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None


class Workflow(WorkflowBase):
    id: int
    created_at: datetime
    updated_at: datetime
    components: List[Component] = []

    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    filename: str
    content: bytes


class Document(BaseModel):
    id: int
    filename: str
    original_name: str
    file_size: int
    mime_type: str
    embeddings_generated: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True


class WorkflowExecutionCreate(BaseModel):
    workflow_id: int
    input_data: Dict[str, Any]


class WorkflowExecution(BaseModel):
    id: int
    workflow_id: int
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class LLMRequest(BaseModel):
    query: str
    context: Optional[str] = None
    custom_prompt: Optional[str] = None
    use_web_search: bool = False
    model: str
    api_key: Optional[str] = None


class LLMResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []
    model_used: str
