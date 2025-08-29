from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Form
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import shutil
from pathlib import Path

from app.database import get_db
from app import models, schemas
from app.services.document_service import DocumentService

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.options("/upload")
async def options_upload():
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })


@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    embedding_api_key: str = Form(""),
    db: Session = Depends(get_db)
):
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document record
    db_document = models.Document(
        filename=unique_filename,
        original_name=file.filename,
        file_path=str(file_path),
        file_size=file_path.stat().st_size,
        mime_type=file.content_type or "application/octet-stream"
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Process document asynchronously (extract text and generate embeddings)
    document_service = DocumentService()
    await document_service.process_document(db_document.id, db, embedding_api_key if embedding_api_key else None)
    
    return db_document


@router.get("/", response_model=List[schemas.Document])
def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=schemas.Document)
def read_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    file_path = Path(db_document.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    db.delete(db_document)
    db.commit()
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/generate-embeddings")
async def generate_embeddings(document_id: int, db: Session = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document_service = DocumentService()
    await document_service.generate_embeddings(document_id, db)
    
    return {"message": "Embeddings generated successfully"}
