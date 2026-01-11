"""
Document processing and chunking for RAG
"""
from typing import List, Dict
import os
from pathlib import Path
import PyPDF2
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings


class DocumentProcessor:
    """Process documents for RAG indexing"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                raise Exception(f"Failed to extract text from {file_path}: {str(e2)}")
        
        return text.strip()
    
    def load_text(self, file_path: str) -> str:
        """Load text from .txt file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_document(self, file_path: str) -> str:
        """Load document based on file extension"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if path.suffix.lower() == '.pdf':
            return self.load_pdf(file_path)
        elif path.suffix.lower() == '.txt':
            return self.load_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into chunks with metadata"""
        chunks = self.text_splitter.split_text(text)
        
        # Add metadata to each chunk
        chunked_docs = []
        for i, chunk in enumerate(chunks):
            doc = {
                "content": chunk,
                "metadata": {
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            }
            chunked_docs.append(doc)
        
        return chunked_docs
    
    def process_document(self, file_path: str) -> List[Dict]:
        """Process a document: load and chunk"""
        # Load document
        text = self.load_document(file_path)
        
        # Create metadata
        path = Path(file_path)
        metadata = {
            "source": path.name,
            "file_path": str(path.absolute()),
            "file_type": path.suffix
        }
        
        # Chunk the text
        chunks = self.chunk_text(text, metadata)
        
        return chunks
    
    def process_directory(self, directory_path: str) -> List[Dict]:
        """Process all documents in a directory"""
        all_chunks = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Process all PDF and TXT files
        for file_path in directory.glob("**/*"):
            if file_path.suffix.lower() in ['.pdf', '.txt']:
                try:
                    chunks = self.process_document(str(file_path))
                    all_chunks.extend(chunks)
                    print(f"Processed: {file_path.name} ({len(chunks)} chunks)")
                except Exception as e:
                    print(f"Error processing {file_path.name}: {str(e)}")
        
        return all_chunks
