"""
Configuration management for RAG AI Agent
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_embedding_deployment: str = "text-embedding-ada-002"
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Vector Store Configuration
    vector_store_type: str = "faiss"  # Options: faiss, azure_search
    vector_store_path: str = "./data/vector_store"
    
    # Azure AI Search (Optional)
    azure_search_endpoint: Optional[str] = None
    azure_search_key: Optional[str] = None
    azure_search_index_name: str = "documents-index"
    
    # Application Settings
    app_name: str = "RAG AI Agent"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    session_timeout_minutes: int = 30
    
    # API Settings
    cors_origins: List[str] = ["*"]
    max_query_length: int = 2000
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 3
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
