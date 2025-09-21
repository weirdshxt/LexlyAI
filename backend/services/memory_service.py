"""
Memory service for managing user sessions and conversation history
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from utils.config import get_settings

class MemoryService:
    """Service for managing session memory and conversation history"""
    
    def __init__(self):
        self.settings = get_settings()
        # In-memory storage for demo (replace with Firestore in production)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize Firestore if configured
        self.firestore_client = None
        if self.settings.firestore_project_id:
            try:
                from google.cloud import firestore
                self.firestore_client = firestore.Client(project=self.settings.firestore_project_id)
            except Exception as e:
                print(f"Failed to initialize Firestore: {e}")
                print("Using in-memory storage instead")
    
    async def create_session(self, session_id: str, document_analysis: Any) -> bool:
        """Create a new session with document analysis"""
        try:
            session_data = {
                "session_id": session_id,
                "analysis": document_analysis.dict() if hasattr(document_analysis, 'dict') else document_analysis,
                "conversation_history": [],
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat()
            }
            
            if self.firestore_client:
                # Store in Firestore
                doc_ref = self.firestore_client.collection('sessions').document(session_id)
                doc_ref.set(session_data)
            else:
                # Store in memory
                self.sessions[session_id] = session_data
            
            return True
            
        except Exception as e:
            print(f"Error creating session {session_id}: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        try:
            if self.firestore_client:
                # Get from Firestore
                doc_ref = self.firestore_client.collection('sessions').document(session_id)
                doc = doc_ref.get()
                if doc.exists:
                    session_data = doc.to_dict()
                    # Update last accessed
                    session_data['last_accessed'] = datetime.utcnow().isoformat()
                    doc_ref.update({'last_accessed': session_data['last_accessed']})
                    return session_data
                else:
                    return None
            else:
                # Get from memory
                if session_id in self.sessions:
                    session_data = self.sessions[session_id]
                    # Update last accessed
                    session_data['last_accessed'] = datetime.utcnow().isoformat()
                    return session_data
                else:
                    return None
                    
        except Exception as e:
            print(f"Error retrieving session {session_id}: {e}")
            return None
    
    async def add_message(self, session_id: str, content: str, role: str) -> bool:
        """Add a message to the conversation history"""
        try:
            if False:
                pass
        except Exception as e:
            print(f"Error adding message to session: {e}")
            return False
            session_data = await self.get_session(session_id)
            if not session_data:
                return False
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add message to history
            session_data['conversation_history'].append(message)
            
            # Keep only last 50 messages to prevent memory bloat
            if len(session_data['conversation_history']) > 50:
                session_data['conversation_history'] = session_data['conversation_history'][-50:]
                
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated data"""
        try:
            if self.firestore_client:
                # Delete from Firestore
                doc_ref = self.firestore_client.collection('sessions').document(session_id)
                doc_ref.delete()
            else:
                # Delete from memory
                if session_id in self.sessions:
                    del self.sessions[session_id]
                else:
                    return False
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
            
            # Update session
            if self.firestore_client:
                doc_ref = self.firestore_client.collection('sessions').document(session_id)
                doc_ref.update({
                    'conversation_history': session_data['conversation_history'],
                    'last_accessed': datetime.utcnow().isoformat()
                })
            else:
                self.sessions[session_id] = session_data
            
            return True
            
        except Exception as e:
            print(f"Error adding message to session {session_id}: {e}")
            return False
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            if self.firestore_client:
                doc_ref = self.firestore_client.collection('sessions').document(session_id)
                doc_ref.update(updates)
            else:
                if session_id in self.sessions:
                    self.sessions[session_id].update(updates)
                else:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error updating session {session_id}: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            if self.firestore_client:
                doc_ref = self.firestore_client.collection('sessions').document(session_id)
                doc_ref.delete()
            else:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                else:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    async def list_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all sessions with basic info"""
        try:
            sessions = []
            
            if self.firestore_client:
                # Get from Firestore
                docs = self.firestore_client.collection('sessions').limit(limit).stream()
                for doc in docs:
                    data = doc.to_dict()
                    sessions.append({
                        "session_id": doc.id,
                        "document_name": data.get('analysis', {}).get('document_name', 'Unknown'),
                        "created_at": data.get('created_at'),
                        "last_accessed": data.get('last_accessed'),
                        "message_count": len(data.get('conversation_history', []))
                    })
            else:
                # Get from memory
                for session_id, data in self.sessions.items():
                    sessions.append({
                        "session_id": session_id,
                        "document_name": data.get('analysis', {}).get('document_name', 'Unknown'),
                        "created_at": data.get('created_at'),
                        "last_accessed": data.get('last_accessed'),
                        "message_count": len(data.get('conversation_history', []))
                    })
            
            # Sort by last accessed
            sessions.sort(key=lambda x: x.get('last_accessed', ''), reverse=True)
            
            return sessions
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            session_data = await self.get_session(session_id)
            if session_data:
                return session_data.get('conversation_history', [])
            else:
                return []
                
        except Exception as e:
            print(f"Error getting conversation history for session {session_id}: {e}")
            return []
    
    async def clear_conversation_history(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        try:
            if self.firestore_client:
                doc_ref = self.firestore_client.collection('sessions').document(session_id)
                doc_ref.update({'conversation_history': []})
            else:
                if session_id in self.sessions:
                    self.sessions[session_id]['conversation_history'] = []
                else:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error clearing conversation history for session {session_id}: {e}")
            return False
    
    async def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        """Search sessions by document name or content"""
        try:
            all_sessions = await self.list_sessions()
            matching_sessions = []
            
            query_lower = query.lower()
            
            for session in all_sessions:
                # Search in document name
                if query_lower in session.get('document_name', '').lower():
                    matching_sessions.append(session)
                    continue
                
                # Search in conversation history
                session_data = await self.get_session(session['session_id'])
                if session_data:
                    conversation_history = session_data.get('conversation_history', [])
                    for message in conversation_history:
                        if query_lower in message.get('content', '').lower():
                            matching_sessions.append(session)
                            break
            
            return matching_sessions
            
        except Exception as e:
            print(f"Error searching sessions: {e}")
            return []
