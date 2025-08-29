from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.Component)
def create_component(component: schemas.ComponentCreate, db: Session = Depends(get_db)):
    db_component = models.Component(**component.dict())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


@router.get("/workflow/{workflow_id}", response_model=List[schemas.Component])
def read_workflow_components(workflow_id: int, db: Session = Depends(get_db)):
    components = db.query(models.Component).filter(
        models.Component.workflow_id == workflow_id
    ).all()
    return components


@router.get("/{component_id}", response_model=schemas.Component)
def read_component(component_id: int, db: Session = Depends(get_db)):
    component = db.query(models.Component).filter(models.Component.id == component_id).first()
    if component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    return component


@router.put("/{component_id}", response_model=schemas.Component)
def update_component(component_id: int, component: schemas.ComponentUpdate, db: Session = Depends(get_db)):
    db_component = db.query(models.Component).filter(models.Component.id == component_id).first()
    if db_component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    
    update_data = component.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_component, field, value)
    
    db.commit()
    db.refresh(db_component)
    return db_component


@router.delete("/{component_id}")
def delete_component(component_id: int, db: Session = Depends(get_db)):
    db_component = db.query(models.Component).filter(models.Component.id == component_id).first()
    if db_component is None:
        raise HTTPException(status_code=404, detail="Component not found")
    
    db.delete(db_component)
    db.commit()
    return {"message": "Component deleted successfully"}
