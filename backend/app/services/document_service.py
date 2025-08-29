import fitz  # PyMuPDF
import httpx
import json
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from decouple import config
import chromadb
from chromadb.config import Settings
import numpy as np
from pathlib import Path

from app import models


class DocumentService:
    def __init__(self):
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )

    async def process_document(self, document_id: int, db: Session, embedding_api_key: Optional[str] = None):
        """Extract text from document and generate embeddings"""
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            return
        
        # Extract text
        extracted_text = await self.extract_text_from_file(document.file_path, document.mime_type)
        
        # Update document with extracted text
        document.extracted_text = extracted_text
        db.commit()
        
        # Generate embeddings if API key is provided
        if embedding_api_key:
            await self.generate_embeddings(document_id, db, embedding_api_key)

    async def extract_text_from_file(self, file_path: str, mime_type: str) -> str:
        """Extract text from various file formats using PyMuPDF"""
        try:
            if mime_type == "application/pdf":
                return self._extract_text_from_pdf_pymupdf(file_path)
            elif mime_type.startswith("text/"):
                return self._extract_text_from_text_file(file_path)
            else:
                # For other formats, try to read as text
                try:
                    return self._extract_text_from_text_file(file_path)
                except:
                    return "Could not extract text from this file format"
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def _extract_text_from_pdf_pymupdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF (fitz)"""
        text = ""
        try:
            # Open the PDF file
            pdf_document = fitz.open(file_path)
            
            # Extract text from each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text() + "\n"
            
            pdf_document.close()
        except Exception as e:
            text = f"Error extracting text from PDF: {str(e)}"
        return text

    def _extract_text_from_text_file(self, file_path: str) -> str:
        """Extract text from text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

    async def generate_embeddings(self, document_id: int, db: Session, embedding_api_key: str):
        """Generate embeddings for document text using Gemini API and store in ChromaDB"""
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document or not document.extracted_text:
            return

        try:
            # Split text into chunks
            chunks = self._split_text_into_chunks(document.extracted_text)
            
            # Generate collection name
            collection_name = f"doc_{document_id}"
            
            # Create or get ChromaDB collection
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"document_id": document_id, "filename": document.original_name}
            )
            
            # Generate embeddings for each chunk using Gemini
            embeddings = []
            chunk_ids = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                # Generate embedding using Gemini API
                embedding = await self._generate_gemini_embedding(chunk, embedding_api_key)
                if embedding:
                    embeddings.append(embedding)
                    chunk_ids.append(f"{document_id}_chunk_{i}")
                    metadatas.append({
                        "document_id": document_id,
                        "chunk_index": i,
                        "text_length": len(chunk)
                    })
            
            # Store in ChromaDB
            if embeddings:
                collection.add(
                    embeddings=embeddings,
                    documents=chunks[:len(embeddings)],
                    metadatas=metadatas,
                    ids=chunk_ids
                )
            
            # Update document record
            document.embeddings_generated = True
            document.chroma_collection_name = collection_name
            db.commit()
            
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Mark as failed but don't crash
            document.embeddings_generated = False
            db.commit()

    async def _generate_gemini_embedding(self, text: str, api_key: str) -> Optional[List[float]]:
        """Generate embedding using Gemini API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent",
                    headers={
                        "Content-Type": "application/json",
                        "X-goog-api-key": api_key
                    },
                    json={
                        "content": {
                            "parts": [
                                {
                                    "text": text
                                }
                            ]
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "embedding" in result and "values" in result["embedding"]:
                        return result["embedding"]["values"]
                else:
                    print(f"Gemini embedding API error: {response.status_code} - {response.text}")
                    return None
        
        except Exception as e:
            print(f"Error calling Gemini embedding API: {str(e)}")
            return None

    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            if end >= len(text):
                break
        return chunks

    async def search_similar_content(self, query: str, document_ids: List[int], db: Session, embedding_api_key: Optional[str] = None, top_k: int = 5) -> List[str]:
        """Search for similar content in specified documents using vector similarity"""
        try:
            # Get documents that have embeddings generated
            documents = db.query(models.Document).filter(
                models.Document.id.in_(document_ids),
                models.Document.embeddings_generated == True,
                models.Document.chroma_collection_name.isnot(None)
            ).all()
            
            if not documents or not embedding_api_key:
                # Fallback to simple text search if no embeddings or API key
                return await self._simple_text_search(query, document_ids, db, top_k)
            
            # Generate query embedding
            query_embedding = await self._generate_gemini_embedding(query, embedding_api_key)
            if not query_embedding:
                return await self._simple_text_search(query, document_ids, db, top_k)
            
            # Search in each document's collection
            all_results = []
            
            for document in documents:
                try:
                    collection = self.chroma_client.get_collection(document.chroma_collection_name)
                    
                    # Query the collection
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, 10)  # Get more results per document
                    )
                    
                    # Add document results to all results
                    if results['documents'] and len(results['documents']) > 0:
                        for doc_chunk in results['documents'][0]:
                            all_results.append(doc_chunk)
                            
                except Exception as e:
                    print(f"Error querying collection {document.chroma_collection_name}: {str(e)}")
                    continue
            
            return all_results[:top_k]
            
        except Exception as e:
            print(f"Error in vector search: {str(e)}")
            # Fallback to simple text search
            return await self._simple_text_search(query, document_ids, db, top_k)
    
    async def _simple_text_search(self, query: str, document_ids: List[int], db: Session, top_k: int = 5) -> List[str]:
        """Fallback simple text search when vector search is not available"""
        try:
            # Get documents with extracted text
            documents = db.query(models.Document).filter(
                models.Document.id.in_(document_ids),
                models.Document.extracted_text.isnot(None)
            ).all()

            # Simple text matching - return document text chunks that contain the query
            results = []
            for document in documents:
                if document.extracted_text and query.lower() in document.extracted_text.lower():
                    # Split into chunks and return relevant ones
                    chunks = self._split_text_into_chunks(document.extracted_text)
                    for chunk in chunks:
                        if query.lower() in chunk.lower():
                            results.append(chunk)
                            if len(results) >= top_k:
                                break
                    if len(results) >= top_k:
                        break

            return results[:top_k]

        except Exception as e:
            print(f"Error in simple text search: {str(e)}")
            return []
