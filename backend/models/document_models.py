"""
Pydantic models for document analysis and API responses
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    """Metadata extracted from the document"""
    document_type: str
    parties: List[str]
    dates: List[str]
    contract_value: Optional[str] = None
    jurisdiction: Optional[str] = None
    governing_law: Optional[str] = None

class Clause(BaseModel):
    """Individual clause from the document"""
    id: str
    title: str
    text: str
    clause_type: str
    metadata: Dict[str, Any]
    start_page: int
    end_page: int

class DocumentAnalysis(BaseModel):
    """Complete analysis of a legal document"""
    document_id: str
    document_name: str
    metadata: DocumentMetadata
    clauses: List[Clause]
    summary: Optional[str] = None
    processing_timestamp: datetime
    confidence_score: float

class ClauseExplanation(BaseModel):
    """AI-generated explanation of a clause"""
    clause_id: str
    original_text: str
    explanation: str
    key_points: List[str]
    risks: List[str]
    plain_language: str

class ChatMessage(BaseModel):
    """Chat message from user"""
    content: str
    timestamp: Optional[datetime] = None

class ConversationMessage(BaseModel):
    """Message in conversation history"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class SessionData(BaseModel):
    """Session data stored in memory"""
    session_id: str
    analysis: DocumentAnalysis
    conversation_history: List[ConversationMessage]
    created_at: datetime
    last_accessed: datetime
