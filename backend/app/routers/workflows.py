from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

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
    return {"message": "Workflow deleted successfully"}
