"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Google Cloud Configuration
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    google_cloud_project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
    document_ai_location: str = os.getenv("DOCUMENT_AI_LOCATION", "us")
    document_ai_processor_id: str = os.getenv("DOCUMENT_AI_PROCESSOR_ID", "")
    
    # Vertex AI Configuration
    vertex_ai_location: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    # Use a currently supported model by default
    vertex_ai_model: str = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-flash")
    # Optional fallback model if primary isn't accessible
    vertex_ai_fallback_model: str = os.getenv("VERTEX_AI_FALLBACK_MODEL", "gemini-1.5-flash")
    
    # Firestore Configuration
    firestore_project_id: str = os.getenv("FIRESTORE_PROJECT_ID", "")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://lexly-ai.vercel.app").split(",")
    
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
