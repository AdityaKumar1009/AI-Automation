from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.database import engine
from app.models import Base
from app.routers import components, workflows, documents, llm


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="LLM Workflow Builder API",
    description="Backend API for drag-and-drop LLM workflow builder",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(components.router, prefix="/api/components", tags=["components"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])


@app.get("/")
async def root():
    return {"message": "LLM Workflow Builder API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
