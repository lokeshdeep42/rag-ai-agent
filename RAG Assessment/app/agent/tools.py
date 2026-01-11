"""
Tool definitions for AI agent
"""
from typing import List, Tuple
from app.rag.vector_store import VectorStore


class DocumentSearchTool:
    """Tool for searching documents in vector store"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.name = "document_search"
        self.description = """
        Search the company's knowledge base for relevant information.
        Use this tool when the query is about:
        - Company policies (HR, leave, benefits)
        - Product information and FAQs
        - Security policies
        - Onboarding procedures
        - Technical documentation
        Input should be the user's question.
        """
    
    def run(self, query: str) -> Tuple[str, List[str]]:
        """Execute document search"""
        chunks, sources = self.vector_store.get_relevant_chunks(query)
        
        if not chunks:
            return "No relevant documents found.", []
        
        # Combine chunks into context
        context = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(chunks)])
        
        return context, sources


class DirectAnswerTool:
    """Tool for direct LLM answers (general knowledge)"""
    
    def __init__(self):
        self.name = "direct_answer"
        self.description = """
        Answer general knowledge questions directly without searching documents.
        Use this tool when the query is about:
        - General facts
        - Common knowledge
        - Math calculations
        - Definitions
        - Current events (if you have knowledge)
        Input should be the user's question.
        """
    
    def run(self, query: str) -> str:
        """This is a placeholder - actual answering is done by the agent"""
        return f"Direct answer needed for: {query}"


def get_available_tools(vector_store: VectorStore) -> List:
    """Get list of available tools for the agent"""
    return [
        DocumentSearchTool(vector_store),
        DirectAnswerTool()
    ]
