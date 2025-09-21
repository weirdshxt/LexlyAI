"""
Main FastAPI application for Legal Document AI Demo
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import uuid
from datetime import datetime

from services.document_processor import DocumentProcessor
from services.ai_service import AIService
from services.memory_service import MemoryService
from models.document_models import DocumentAnalysis, ClauseExplanation, ChatMessage
from utils.config import get_settings

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Legal Document AI API",
    description="AI-powered legal document analysis and Q&A",
    version="1.0.0"
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
ai_service = AIService()
memory_service = MemoryService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Legal Document AI API is running", "version": "1.0.0"}

@app.post("/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a legal document (PDF or DOCX) for processing
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Process document with Document AI
        document_analysis = await document_processor.process_document(
            content, 
            file.filename, 
            session_id
        )
        
        # Store in memory service
        await memory_service.create_session(session_id, document_analysis)
        
        return {
            "session_id": session_id,
            "document_name": file.filename,
            "analysis": document_analysis.model_dump(),
            "message": "Document uploaded and processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/explain/{session_id}/{clause_id}", response_model=ClauseExplanation)
async def explain_clause(session_id: str, clause_id: str):
    """
    Get plain language explanation for a specific clause
    """
    try:
        # Get session data
        session_data = await memory_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find clause in document analysis
        clause = None
        for c in session_data.get("analysis", {}).get("clauses", []):
            if c["id"] == clause_id:
                clause = c
                break
        
        if not clause:
            raise HTTPException(status_code=404, detail="Clause not found")
        
        # Generate explanation using AI
        explanation = await ai_service.explain_clause(clause["text"], clause["metadata"])
        
        return ClauseExplanation(
            clause_id=clause_id,
            original_text=clause["text"],
            explanation=explanation["explanation"],
            key_points=explanation["key_points"],
            risks=explanation["risks"],
            plain_language=explanation["plain_language"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining clause: {str(e)}")

@app.post("/summarize/{session_id}")
async def summarize_document(session_id: str):
    """
    Generate a summary of the entire document
    """
    try:
        # Get session data
        session_data = await memory_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate summary using AI
        summary = await ai_service.summarize_document(session_data["analysis"])
        
        return {
            "session_id": session_id,
            "summary": summary,
            "message": "Document summarized successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing document: {str(e)}")

@app.post("/chat/{session_id}")
async def chat_with_document(session_id: str, message: ChatMessage):
    """
    Interactive Q&A with the document using memory system
    """
    try:
        # Get session data
        session_data = await memory_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Add user message to conversation
        await memory_service.add_message(session_id, message.content, "user")
        
        # Generate response using AI with memory context
        response = await ai_service.chat_with_document(
            message.content,
            session_data["analysis"],
            session_data.get("conversation_history", [])
        )
        
        # Add AI response to conversation
        await memory_service.add_message(session_id, response, "assistant")
        
        return {
            "session_id": session_id,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get session data and conversation history
    """
    try:
        session_data = await memory_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "data": session_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    try:
        sessions = await memory_service.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its associated data"""
    try:
        success = await memory_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
