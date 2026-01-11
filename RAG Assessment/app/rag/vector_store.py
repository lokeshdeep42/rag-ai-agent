"""
Vector store management for document retrieval
"""
from typing import List, Dict, Optional
import os
import pickle
import faiss
import numpy as np
from pathlib import Path
from app.config import settings
from app.rag.embeddings import EmbeddingsGenerator


class VectorStore:
    """FAISS-based vector store for document retrieval"""
    
    def __init__(self):
        self.embeddings_generator = EmbeddingsGenerator()
        self.index = None
        self.documents = []  # Store document chunks with metadata
        self.dimension = 1536  # OpenAI embedding dimension
        self.store_path = Path(settings.vector_store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
    
    def initialize(self):
        """Initialize or load existing FAISS index"""
        index_file = self.store_path / "faiss_index.bin"
        docs_file = self.store_path / "documents.pkl"
        
        if index_file.exists() and docs_file.exists():
            # Load existing index
            self.index = faiss.read_index(str(index_file))
            with open(docs_file, 'rb') as f:
                self.documents = pickle.load(f)
            print(f"Loaded existing index with {len(self.documents)} documents")
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            print("Created new FAISS index")
    
    def add_documents(self, documents: List[Dict], save: bool = True):
        """Add documents to the vector store"""
        if not documents:
            return
        
        # Extract text content
        texts = [doc["content"] for doc in documents]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} documents...")
        embeddings = self.embeddings_generator.generate_embeddings_batch(texts)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store documents with metadata
        self.documents.extend(documents)
        
        print(f"Added {len(documents)} documents to vector store")
        
        # Save if requested
        if save:
            self.save()
    
    def save(self):
        """Save FAISS index and documents to disk"""
        index_file = self.store_path / "faiss_index.bin"
        docs_file = self.store_path / "documents.pkl"
        
        faiss.write_index(self.index, str(index_file))
        with open(docs_file, 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"Saved vector store to {self.store_path}")
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for relevant documents"""
        if top_k is None:
            top_k = settings.top_k_results
        
        if not self.documents:
            return []
        
        # Generate query embedding
        query_embedding = self.embeddings_generator.generate_embedding(query)
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search FAISS index
        distances, indices = self.index.search(query_vector, top_k)
        
        # Retrieve documents with scores
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score (inverse)
                similarity = 1 / (1 + distance)
                
                # Only include results above threshold
                if similarity >= settings.similarity_threshold:
                    result = {
                        **self.documents[idx],
                        "similarity_score": float(similarity),
                        "rank": i + 1
                    }
                    results.append(result)
        
        return results
    
    def get_relevant_chunks(self, query: str, top_k: int = None) -> tuple[List[str], List[str]]:
        """Get relevant document chunks and their sources"""
        results = self.search(query, top_k)
        
        chunks = [result["content"] for result in results]
        sources = [result["metadata"]["source"] for result in results]
        
        # Deduplicate sources while preserving order
        unique_sources = []
        for source in sources:
            if source not in unique_sources:
                unique_sources.append(source)
        
        return chunks, unique_sources
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "store_path": str(self.store_path)
        }
