"""
FastAPI Application - RAG AI Agent
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.rag.vector_store import VectorStore
from app.agent.memory import SessionMemory, session_memory
from app.agent.ai_agent import AIAgent
from app.api.routes import router, initialize_dependencies


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global instances
vector_store: VectorStore = None
agent: AIAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global vector_store, agent
    
    # Startup
    logger.info("Starting RAG AI Agent application...")
    
    try:
        # Initialize vector store
        logger.info("Initializing vector store...")
        vector_store = VectorStore()
        vector_store.initialize()
        
        # Initialize agent
        logger.info("Initializing AI agent...")
        agent = AIAgent(vector_store, session_memory)
        
        # Initialize route dependencies
        initialize_dependencies(vector_store, session_memory, agent)
        
        logger.info("Application startup complete!")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Save vector store
    if vector_store:
        try:
            vector_store.save()
            logger.info("Vector store saved successfully")
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RAG-based AI Agent with intelligent document retrieval",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(router, prefix="/api/v1", tags=["AI Agent"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG AI Agent API",
        "version": settings.app_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
