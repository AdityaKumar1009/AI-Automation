from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.services.llm_service import LLMService
from app.services.workflow_service import WorkflowService

router = APIRouter()


@router.options("/execute-workflow/{workflow_id}")
async def options_execute_workflow(workflow_id: int):
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })


@router.post("/chat", response_model=schemas.LLMResponse)
async def chat_with_llm(
    request: schemas.LLMRequest,
    db: Session = Depends(get_db)
):
    llm_service = LLMService()
    response = await llm_service.generate_response(
        query=request.query,
        model=request.model,
        context=request.context,
        custom_prompt=request.custom_prompt,
        use_web_search=request.use_web_search,
        api_key=request.api_key
    )
    return response


@router.post("/execute-workflow/{workflow_id}")
async def execute_workflow(
    workflow_id: int,
    execution_request: schemas.WorkflowExecutionCreate,
    db: Session = Depends(get_db)
):
    # Verify workflow exists
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create execution record
    db_execution = models.WorkflowExecution(
        workflow_id=workflow_id,
        input_data=execution_request.input_data,
        status="pending"
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    
    # Execute workflow
    workflow_service = WorkflowService()
    result = await workflow_service.execute_workflow(db_execution.id, db)
    
    return {
        "execution_id": db_execution.id,
        "status": result.get("status", "completed"),
        "output": result.get("output", {}),
        "message": "Workflow execution started"
    }


@router.get("/executions/{execution_id}")
def get_execution_status(execution_id: int, db: Session = Depends(get_db)):
    execution = db.query(models.WorkflowExecution).filter(
        models.WorkflowExecution.id == execution_id
    ).first()
    
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution


@router.get("/executions/{execution_id}/chat")
def get_execution_chat(execution_id: int, db: Session = Depends(get_db)):
    chat_history = db.query(models.ChatHistory).filter(
        models.ChatHistory.workflow_execution_id == execution_id
    ).order_by(models.ChatHistory.timestamp).all()
    
    return chat_history
