"""
Setup script for initializing the RAG AI Agent system
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.rag.document_processor import DocumentProcessor
from app.rag.vector_store import VectorStore
from app.config import settings


def check_environment():
    """Check if required environment variables are set"""
    print("Checking environment configuration...")
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        print("See .env.example for reference")
        return False
    
    print("✓ All required environment variables are set")
    return True


def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = [
        "documents",
        "data/vector_store",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")


def index_documents():
    """Process and index all documents"""
    print("\nIndexing documents...")
    
    documents_path = Path("documents")
    
    if not documents_path.exists() or not any(documents_path.iterdir()):
        print("⚠️  No documents found in documents/ directory")
        print("   Please add PDF or TXT files to the documents/ directory")
        return False
    
    # Initialize document processor and vector store
    processor = DocumentProcessor()
    vector_store = VectorStore()
    vector_store.initialize()
    
    # Process all documents
    try:
        chunks = processor.process_directory(str(documents_path))
        
        if not chunks:
            print("⚠️  No documents were successfully processed")
            return False
        
        print(f"\n✓ Processed {len(chunks)} document chunks")
        
        # Add to vector store
        vector_store.add_documents(chunks, save=True)
        
        print(f"✓ Indexed documents successfully")
        print(f"✓ Vector store saved to {settings.vector_store_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error indexing documents: {str(e)}")
        return False


def verify_setup():
    """Verify the setup is complete"""
    print("\nVerifying setup...")
    
    # Check vector store exists
    vector_store_path = Path(settings.vector_store_path)
    index_file = vector_store_path / "faiss_index.bin"
    docs_file = vector_store_path / "documents.pkl"
    
    if not index_file.exists() or not docs_file.exists():
        print("❌ Vector store not found")
        return False
    
    print("✓ Vector store verified")
    
    # Load and check vector store
    try:
        vector_store = VectorStore()
        vector_store.initialize()
        stats = vector_store.get_stats()
        
        print(f"✓ Vector store contains {stats['total_documents']} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading vector store: {str(e)}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("RAG AI Agent - Setup Script")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Index documents
    if not index_documents():
        print("\n⚠️  Setup completed with warnings")
        print("   Documents were not indexed. You can run this script again")
        print("   after adding documents to the documents/ directory")
        sys.exit(1)
    
    # Verify setup
    if not verify_setup():
        print("\n❌ Setup verification failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the configuration in .env file")
    print("2. Start the application:")
    print("   python -m uvicorn app.main:app --reload")
    print("3. Access the API documentation:")
    print("   http://localhost:8000/docs")
    print("\nFor production deployment, see deployment/ directory")
    print("=" * 60)


if __name__ == "__main__":
    main()
