"""
API routes for RAG AI Agent
"""
from fastapi import APIRouter, HTTPException, status
from pathlib import Path
from app.api.models import (
    QueryRequest, QueryResponse, ResetSessionRequest,
    HealthResponse, DocumentsResponse, DocumentInfo
)
from app.agent.ai_agent import AIAgent
from app.rag.vector_store import VectorStore
from app.agent.memory import SessionMemory
from app.config import settings


# Initialize router
router = APIRouter()

# Global instances (will be initialized in main.py)
agent: AIAgent = None
vector_store: VectorStore = None
session_memory: SessionMemory = None


def initialize_dependencies(vs: VectorStore, sm: SessionMemory, ag: AIAgent):
    """Initialize global dependencies"""
    global vector_store, session_memory, agent
    vector_store = vs
    session_memory = sm
    agent = ag


@router.post("/ask", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def ask_question(request: QueryRequest):
    """
    Process a user query and return an AI-generated response.
    
    The agent will automatically determine whether to:
    - Answer directly using general knowledge, OR
    - Search company documents and use RAG
    """
    try:
        # Validate query length
        if len(request.query) > settings.max_query_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Query too long. Maximum length is {settings.max_query_length} characters."
            )
        
        # Execute agent
        result = agent.execute(request.query, request.session_id)
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/reset-session", status_code=status.HTTP_200_OK)
async def reset_session(request: ResetSessionRequest):
    """Reset a conversation session"""
    try:
        session_memory.delete_session(request.session_id)
        return {"message": "Session reset successfully", "session_id": request.session_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting session: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    try:
        vs_stats = vector_store.get_stats() if vector_store else None
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            vector_store_stats=vs_stats
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version=settings.app_version,
            vector_store_stats={"error": str(e)}
        )


@router.get("/documents", response_model=DocumentsResponse, status_code=status.HTTP_200_OK)
async def list_documents():
    """List all documents in the knowledge base"""
    try:
        documents_path = Path("documents")
        
        if not documents_path.exists():
            return DocumentsResponse(documents=[], total_count=0)
        
        docs = []
        for file_path in documents_path.glob("**/*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt']:
                docs.append(DocumentInfo(
                    name=file_path.name,
                    path=str(file_path),
                    type=file_path.suffix[1:]  # Remove the dot
                ))
        
        return DocumentsResponse(documents=docs, total_count=len(docs))
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )


@router.get("/sessions/stats", status_code=status.HTTP_200_OK)
async def session_stats():
    """Get session memory statistics"""
    try:
        # Cleanup expired sessions first
        expired_count = session_memory.cleanup_expired_sessions()
        stats = session_memory.get_stats()
        stats["expired_cleaned"] = expired_count
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting session stats: {str(e)}"
        )
