"""
Session-based memory management for AI agent
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid


class SessionMemory:
    """Manage conversation sessions and memory"""
    
    def __init__(self, timeout_minutes: int = 30):
        self.sessions: Dict[str, Dict] = {}
        self.timeout_minutes = timeout_minutes
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "messages": [],
            "created_at": datetime.now(),
            "last_accessed": datetime.now()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if self._is_expired(session):
            self.delete_session(session_id)
            return None
        
        # Update last accessed time
        session["last_accessed"] = datetime.now()
        return session
    
    def _is_expired(self, session: Dict) -> bool:
        """Check if session has expired"""
        timeout = timedelta(minutes=self.timeout_minutes)
        return datetime.now() - session["last_accessed"] > timeout
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to session history"""
        session = self.get_session(session_id)
        if session:
            session["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session["messages"]
        if limit:
            return messages[-limit:]
        return messages
    
    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> str:
        """Get formatted conversation context for LLM"""
        messages = self.get_messages(session_id, limit=max_messages)
        
        if not messages:
            return ""
        
        context = "Previous conversation:\n"
        for msg in messages:
            context += f"{msg['role']}: {msg['content']}\n"
        
        return context
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions"""
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if self._is_expired(session)
        ]
        
        for sid in expired_sessions:
            self.delete_session(sid)
        
        return len(expired_sessions)
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            "total_sessions": len(self.sessions),
            "timeout_minutes": self.timeout_minutes
        }


# Global session memory instance
session_memory = SessionMemory()
