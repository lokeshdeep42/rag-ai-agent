"""
Core AI Agent with decision-making and tool calling
"""
from typing import Dict, List, Optional
from openai import AzureOpenAI
from app.config import settings
from app.rag.vector_store import VectorStore
from app.agent.memory import SessionMemory
from app.agent.tools import DocumentSearchTool


class AIAgent:
    """AI Agent with RAG capabilities and tool calling"""
    
    def __init__(self, vector_store: VectorStore, session_memory: SessionMemory):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment = settings.azure_openai_deployment_name
        self.vector_store = vector_store
        self.session_memory = session_memory
        self.document_search_tool = DocumentSearchTool(vector_store)
    
    def classify_query(self, query: str, conversation_context: str = "") -> Dict:
        """Determine if query needs RAG or can be answered directly"""
        
        classification_prompt = f"""You are a query classifier. Determine if the following query requires searching company documents or can be answered with general knowledge.

Company documents contain information about:
- HR policies (leave, benefits, code of conduct)
- Product FAQs and features
- Security policies
- Employee onboarding
- Technical API documentation

Query: {query}

{conversation_context}

Respond with ONLY one word: "DOCUMENT" if it needs company documents, or "DIRECT" if it's general knowledge.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0,
                max_tokens=10
            )
            
            classification = response.choices[0].message.content.strip().upper()
            
            needs_rag = "DOCUMENT" in classification
            
            return {
                "needs_rag": needs_rag,
                "classification": classification
            }
        except Exception as e:
            # Default to RAG if classification fails
            print(f"Classification error: {str(e)}")
            return {"needs_rag": True, "classification": "DOCUMENT"}
    
    def generate_response(
        self, 
        query: str, 
        context: str = "", 
        conversation_history: str = ""
    ) -> str:
        """Generate response using LLM"""
        
        system_prompt = """You are a helpful AI assistant. Answer questions clearly and concisely.
If context from documents is provided, use it to answer the question accurately.
If no context is provided, use your general knowledge.
Always be professional and helpful."""
        
        user_message = query
        if context:
            user_message = f"""Context from company documents:
{context}

Question: {query}

Please answer based on the provided context. If the context doesn't contain relevant information, say so."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            messages.append({"role": "user", "content": conversation_history})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def execute(self, query: str, session_id: Optional[str] = None) -> Dict:
        """Main agent execution - process query and return response"""
        
        # Create or get session
        if not session_id:
            session_id = self.session_memory.create_session()
        elif not self.session_memory.get_session(session_id):
            session_id = self.session_memory.create_session()
        
        # Get conversation context
        conversation_context = self.session_memory.get_conversation_context(session_id)
        
        # Add user query to memory
        self.session_memory.add_message(session_id, "user", query)
        
        # Classify query
        classification = self.classify_query(query, conversation_context)
        
        sources = []
        context = ""
        
        # Execute based on classification
        if classification["needs_rag"]:
            # Use RAG - search documents
            context, sources = self.document_search_tool.run(query)
            
            if not sources:
                # No documents found
                answer = "I couldn't find relevant information in the company documents. This might be outside my knowledge base."
            else:
                # Generate response with document context
                answer = self.generate_response(query, context, conversation_context)
        else:
            # Direct answer using LLM
            answer = self.generate_response(query, "", conversation_context)
        
        # Add assistant response to memory
        self.session_memory.add_message(session_id, "assistant", answer)
        
        return {
            "answer": answer,
            "source": sources,
            "session_id": session_id,
            "metadata": {
                "classification": classification["classification"],
                "used_rag": classification["needs_rag"],
                "num_sources": len(sources)
            }
        }
