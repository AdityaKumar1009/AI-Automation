from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    nodes = Column(JSON)  # Store React Flow nodes
    edges = Column(JSON)  # Store React Flow edges
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    components = relationship("Component", back_populates="workflow")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class Component(Base):
    __tablename__ = "components"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    type = Column(String)  # user_query, knowledge_base, llm_engine, output
    name = Column(String)
    config = Column(JSON)  # Component-specific configuration
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    workflow = relationship("Workflow", back_populates="components")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    original_name = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String)
    extracted_text = Column(Text)
    embeddings_generated = Column(Boolean, default=False)
    chroma_collection_name = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String)  # pending, running, completed, failed
    execution_log = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    chat_history = relationship("ChatHistory", back_populates="execution")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_execution_id = Column(Integer, ForeignKey("workflow_executions.id"))
    role = Column(String)  # user, assistant
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    execution = relationship("WorkflowExecution", back_populates="chat_history")
