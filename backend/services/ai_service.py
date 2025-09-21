"""
AI service using LangChain for legal document analysis and Q&A
"""
from typing import Dict, Any, List, Optional
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import json
import re

# Import Google Vertex AI LLM
from utils.config import get_settings

class AIService:
    """AI service for legal document analysis using LangChain"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._initialize_llm()
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Initialize prompt templates
        self._setup_prompts()
    
    def _initialize_llm(self):
        """Initialize the LLM using Google Vertex AI"""
        if not self.settings.google_cloud_project_id:
            raise ValueError("Google Cloud project ID is required")
            
        # Set up credentials if provided
        if self.settings.google_application_credentials:
            import os
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.settings.google_application_credentials
        
        try:
            # Use VertexAI (text) for bison models, ChatVertexAI for Gemini chat models
            model_name = self.settings.vertex_ai_model
            fallback_model = getattr(self.settings, 'vertex_ai_fallback_model', None)
            try:
                if model_name and "bison" in model_name:
                    from langchain_google_vertexai import VertexAI
                    return VertexAI(
                        project=self.settings.google_cloud_project_id,
                        location=self.settings.vertex_ai_location,
                        model_name=model_name,
                        temperature=0.3,
                    )
                else:
                    from langchain_google_vertexai import ChatVertexAI
                    return ChatVertexAI(
                        project=self.settings.google_cloud_project_id,
                        location=self.settings.vertex_ai_location,
                        model_name=model_name,
                        temperature=0.3,
                    )
            except Exception as primary_error:
                # If primary model not found or inaccessible, try fallback
                if fallback_model and fallback_model != model_name:
                    try:
                        if "bison" in fallback_model:
                            from langchain_google_vertexai import VertexAI
                            return VertexAI(
                                project=self.settings.google_cloud_project_id,
                                location=self.settings.vertex_ai_location,
                                model_name=fallback_model,
                                temperature=0.3,
                            )
                        else:
                            from langchain_google_vertexai import ChatVertexAI
                            return ChatVertexAI(
                                project=self.settings.google_cloud_project_id,
                                location=self.settings.vertex_ai_location,
                                model_name=fallback_model,
                                temperature=0.3,
                            )
                    except Exception:
                        pass
                # Reraise original
                raise primary_error
        except Exception as e:
            self._handle_llm_error(e)
    
    def _handle_llm_error(self, error: Exception) -> None:
        """Handle LLM initialization errors"""
        print(f"Error initializing LLM: {str(error)}")
        raise error
        
        return MockLLM()
    
    def _setup_prompts(self):
        """Setup prompt templates for different tasks"""
        
        # Clause explanation prompt
        self.clause_explanation_template = PromptTemplate(
            input_variables=["clause_text", "clause_type", "document_context"],
            template="""
You are a legal assistant AI. Given this clause from a complex legal document, explain its meaning clearly and concisely in simple language. Highlight any points users should watch out for or risks involved.

Document Context: {document_context}
Clause Type: {clause_type}
Clause Text: {clause_text}

Please provide:
1. A clear, plain-language explanation
2. Key points to remember
3. Potential risks or concerns
4. Any important deadlines or obligations

Format your response as JSON with these fields:
- explanation: Main explanation in plain language
- key_points: List of important points
- risks: List of potential risks or concerns
- plain_language: Simplified version of the clause
"""
        )
        
        # Document summarization prompt
        self.summarization_template = PromptTemplate(
            input_variables=["document_analysis"],
            template="""
You are a legal assistant AI. Analyze this legal document and provide a comprehensive summary in plain language.

Document Analysis: {document_analysis}

Please provide a structured summary that includes:
1. Document type and purpose
2. Key parties involved
3. Main terms and conditions
4. Important dates and deadlines
5. Key obligations for each party
6. Potential risks or areas of concern

Format your response as a clear, bulleted summary that a non-lawyer can understand.
"""
        )
        
        # Chat Q&A prompt with memory
        self.chat_template = PromptTemplate(
            input_variables=["user_question", "document_context", "conversation_history"],
            template="""
You are a helpful legal AI assistant. You have access to a legal document and previous conversation history.

Document Context: {document_context}
Previous Conversation: {conversation_history}
User Question: {user_question}

Provide a helpful answer based on the document content and conversation history. If the user asks about specific clauses, refer to them by their IDs. If you don't have enough information, ask for clarification.

Be conversational but professional, and always cite specific parts of the document when relevant.
"""
        )
    
    async def explain_clause(self, clause_text: str, clause_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for a specific clause"""
        try:
            # Create chain using RunnableSequence
            chain: RunnableSequence = self.clause_explanation_template | self.llm
            
            # Prepare inputs
            inputs = {
                "clause_text": clause_text,
                "clause_type": clause_metadata.get("type", "general"),
                "document_context": f"Document type: {clause_metadata.get('document_type', 'contract')}"
            }
            
            # Generate explanation
            response_msg = await chain.ainvoke(inputs)
            response = getattr(response_msg, 'content', str(response_msg))
            
            # Try to parse JSON response (handle code fences / markdown)
            explanation_data = self._parse_llm_json_or_text(response)
            
            return explanation_data
            
        except Exception as e:
            print(f"Error in clause explanation: {str(e)}")
            return {
                "explanation": f"I encountered an error analyzing this clause: {str(e)}",
                "key_points": ["Error occurred during analysis"],
                "risks": ["Unable to assess risks due to processing error"],
                "plain_language": "Unable to provide simplified explanation"
            }
    
    async def summarize_document(self, document_analysis: Dict[str, Any]) -> str:
        """Generate summary of the entire document"""
        try:
            # Create chain using RunnableSequence
            chain: RunnableSequence = self.summarization_template | self.llm
            
            # Prepare document analysis summary
            analysis_summary = self._prepare_analysis_summary(document_analysis)
            
            # Generate summary
            response_msg = await chain.ainvoke({"document_analysis": analysis_summary})
            response = getattr(response_msg, 'content', str(response_msg))
            
            return response
            
        except Exception as e:
            print(f"Error in document summarization: {str(e)}")
            return f"I encountered an error summarizing the document: {str(e)}"
    
    async def chat_with_document(self, user_question: str, document_analysis: Dict[str, Any], conversation_history: List[Dict[str, str]]) -> str:
        """Handle chat interaction with document context and memory"""
        try:
            # Create chain using RunnableSequence
            chain: RunnableSequence = self.chat_template | self.llm
            
            # Prepare conversation history
            history_text = self._format_conversation_history(conversation_history)
            
            # Prepare document context
            document_context = self._prepare_document_context(document_analysis)
            
            # Generate response
            response_msg = await chain.ainvoke({
                "user_question": user_question,
                "document_context": document_context,
                "conversation_history": history_text
            })
            response = getattr(response_msg, 'content', str(response_msg))
            
            return response
            
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return f"I encountered an error processing your question: {str(e)}"
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse non-JSON response into structured format with multi-line bullets handling"""
        response = self._strip_code_fences(response)
        response = self._strip_markdown(response)
        lines = response.split('\n')
        explanation = ""
        key_points: List[str] = []
        risks: List[str] = []
        plain_language = ""
        current_section = "explanation"
        buffer: List[str] = []

        def flush_buffer():
            nonlocal buffer, current_section, key_points, risks, explanation
            if not buffer:
                return
            joined = " ".join(buffer).strip()
            joined = self._normalize_bullet(joined)
            if current_section == "key_points":
                key_points.append(joined)
            elif current_section == "risks":
                risks.append(joined)
            else:
                explanation += joined + " "
            buffer = []

        for line in lines:
            raw = line
            line = raw.strip()
            if not line:
                flush_buffer()
                continue

            lower = line.lower()
            if "key points" in lower or "important points" in lower:
                flush_buffer()
                current_section = "key_points"
                continue
            if "risk" in lower or "concern" in lower:
                flush_buffer()
                current_section = "risks"
                continue
            if "plain language" in lower or "simplified" in lower:
                flush_buffer()
                current_section = "plain_language"
                continue

            if current_section in ("key_points", "risks"):
                buffer.append(line)
            elif current_section == "explanation":
                explanation += line + " "
            elif current_section == "plain_language":
                plain_language += line + " "

        flush_buffer()

        return {
            "explanation": explanation.strip(),
            "key_points": key_points,
            "risks": risks,
            "plain_language": plain_language.strip() or explanation.strip()
        }

    def _parse_llm_json_or_text(self, response: str) -> Dict[str, Any]:
        """Attempt to parse a JSON object from LLM output, with fallbacks."""
        cleaned = self._strip_code_fences(response)
        # Try direct JSON
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Try to find the first JSON object substring
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        # Fallback to text parsing
        return self._parse_text_response(response)

    def _strip_code_fences(self, text: str) -> str:
        """Remove ```json ... ``` or ``` ... ``` fences."""
        return re.sub(r"```(?:json)?\n([\s\S]*?)```", r"\1", text).strip()

    def _strip_markdown(self, text: str) -> str:
        """Lightweight markdown cleanup: remove bold/italics markers and quotes artifacts."""
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # bold
        text = re.sub(r"\*(.*?)\*", r"\1", text)  # italics
        text = text.replace('"', '"')  # noop placeholder; keep quotes but avoid escaping issues
        return text

    def _normalize_bullet(self, text: str) -> str:
        """Remove leading bullet markers and normalize spacing; keep Title: Description intact."""
        text = re.sub(r"^[-\*\u2022]\s+", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    
    def _prepare_analysis_summary(self, document_analysis: Dict[str, Any]) -> str:
        """Prepare document analysis for summarization"""
        summary_parts = []
        
        # Document info
        summary_parts.append(f"Document: {document_analysis.get('document_name', 'Unknown')}")
        summary_parts.append(f"Type: {document_analysis.get('metadata', {}).get('document_type', 'Unknown')}")
        
        # Parties
        parties = document_analysis.get('metadata', {}).get('parties', [])
        if parties:
            summary_parts.append(f"Parties: {', '.join(parties)}")
        
        # Key dates
        dates = document_analysis.get('metadata', {}).get('dates', [])
        if dates:
            summary_parts.append(f"Key dates: {', '.join(dates)}")
        
        # Clauses summary
        clauses = document_analysis.get('clauses', [])
        if clauses:
            clause_types = {}
            for clause in clauses:
                clause_type = clause.get('clause_type', 'general')
                clause_types[clause_type] = clause_types.get(clause_type, 0) + 1
            
            summary_parts.append(f"Clause types: {', '.join([f'{k}: {v}' for k, v in clause_types.items()])}")
        
        return '\n'.join(summary_parts)
    
    def _format_conversation_history(self, conversation_history: List[Dict[str, str]]) -> str:
        """Format conversation history for prompt"""
        if not conversation_history:
            return "No previous conversation."
        
        formatted_history = []
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted_history.append(f"{role.title()}: {content}")
        
        return '\n'.join(formatted_history)
    
    def _prepare_document_context(self, document_analysis: Dict[str, Any]) -> str:
        """Prepare document context for chat"""
        context_parts = []
        
        # Document metadata
        metadata = document_analysis.get('metadata', {})
        context_parts.append(f"Document Type: {metadata.get('document_type', 'Unknown')}")
        context_parts.append(f"Parties: {', '.join(metadata.get('parties', []))}")
        
        # Available clauses
        clauses = document_analysis.get('clauses', [])
        if clauses:
            context_parts.append("Available clauses:")
            for clause in clauses[:10]:  # Limit to first 10 clauses
                context_parts.append(f"- {clause.get('id', 'Unknown')}: {clause.get('title', 'No title')}")
        
        return '\n'.join(context_parts)
