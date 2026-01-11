"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class QueryRequest(BaseModel):
    """Request model for /ask endpoint"""
    query: str = Field(..., description="User query", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the company's leave policy?",
                "session_id": "optional-session-id"
            }
        }


class QueryResponse(BaseModel):
    """Response model for /ask endpoint"""
    answer: str = Field(..., description="AI-generated answer")
    source: List[str] = Field(default_factory=list, description="List of source documents used")
    session_id: str = Field(..., description="Session ID for this conversation")
    metadata: Optional[Dict] = Field(None, description="Additional metadata about the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "According to company policy, employees are entitled to 15 days of paid leave per year.",
                "source": ["hr_policies.pdf"],
                "session_id": "abc-123-def",
                "metadata": {
                    "classification": "DOCUMENT",
                    "used_rag": True,
                    "num_sources": 1
                }
            }
        }


class ResetSessionRequest(BaseModel):
    """Request model for resetting a session"""
    session_id: str = Field(..., description="Session ID to reset")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    vector_store_stats: Optional[Dict] = None


class DocumentInfo(BaseModel):
    """Information about a document in the knowledge base"""
    name: str
    path: str
    type: str


class DocumentsResponse(BaseModel):
    """Response model for listing documents"""
    documents: List[DocumentInfo]
    total_count: int
