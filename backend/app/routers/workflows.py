from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.services import document_service, llm_service


router = APIRouter()


@router.options("/{workflow_id}")
async def options_workflow(workflow_id: int):
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })


@router.post("/", response_model=schemas.Workflow)
def create_workflow(workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    db_workflow = models.Workflow(**workflow.dict())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@router.get("/", response_model=List[schemas.Workflow])
def read_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workflows = db.query(models.Workflow).offset(skip).limit(limit).all()
    return workflows


@router.get("/{workflow_id}", response_model=schemas.Workflow)
def read_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.put("/{workflow_id}", response_model=schemas.Workflow)
def update_workflow(workflow_id: int, workflow: schemas.WorkflowUpdate, db: Session = Depends(get_db)):
    db_workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    update_data = workflow.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_workflow, field, value)
    
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    db_workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(db_workflow)
    db.commit()
    return {"message": "Component deleted successfully"}


@router.post("/{workflow_id}/run", response_model=schemas.LLMResponse)
def run_workflow(workflow_id: int, input_data: schemas.WorkflowExecutionCreate, db: Session = Depends(get_db)):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Extract the user query from the input_data
    user_query = input_data.input_data.get("user_query")
    if not user_query:
        raise HTTPException(status_code=400, detail="User query not found in input data")

    # Find the knowledge base and llm engine components
    knowledge_base_node = None
    llm_engine_node = None
    for node in workflow.nodes:
        if node.get("type") == "knowledge_base":
            knowledge_base_node = node
        elif node.get("type") == "llm_engine":
            llm_engine_node = node

    context_str = ""
    if knowledge_base_node:
        # Query the knowledge base
        collection_name = knowledge_base_node.get("data", {}).get("collection_name")
        if collection_name:
            try:
                search_results = document_service.query_collection(collection_name=collection_name, query_text=user_query)
                print(f"Search results: {search_results}")
                context_str = "\n".join([result.get("document", "") for result in search_results])
                print(f"Context string: {context_str}")
            except Exception as e:
                # Handle exceptions during knowledge base query
                raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {e}")

    if not llm_engine_node:
        raise HTTPException(status_code=400, detail="LLM engine node not found in workflow")

    # Get LLM configuration from the node
    llm_config = llm_engine_node.get("data", {})
    model = llm_config.get("model", "openai/gpt-3.5-turbo")
    custom_prompt = llm_config.get("custom_prompt")
    use_web_search = llm_config.get("use_web_search", False)

    # Query the LLM
    try:
        llm_response = llm_service.query_llm(
            query=user_query,
            context_str=context_str,
            custom_prompt=custom_prompt,
            use_web_search=use_web_search,
            model=model,
            api_key=None  # API key management to be implemented
        )
        return llm_response
    except Exception as e:
        # Handle exceptions during LLM query
        raise HTTPException(status_code=500, detail=f"Error querying LLM: {e}")
