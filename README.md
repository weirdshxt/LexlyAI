# Generative AI for Demystifying Legal Documents

An AI-powered web tool that simplifies complex legal documents by extracting and summarizing key clauses in plain language, with interactive Q&A capabilities and a persistent memory system.

---

## Features

- **Document Upload & Processing**: Upload PDF/DOCX legal documents
- **AI-Powered Analysis**: Extract clauses, dates, parties, and terms using Google Document AI
- **Plain Language Explanations**: Generate easy-to-understand summaries using LLMs
- **Interactive Q&A**: Ask follow-up questions with contextual memory
- **Session Management**: Persistent memory across conversations

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **Document Processing**: Google Document AI
- **AI/LLM**: Google Vertex AI (PaLM), LangChain
- **Memory**: Cloud Firestore
- **Orchestration**: LangChain for AI workflows
- **Cloud Platform**: Google Cloud Platform

## Project Structure

```
lexly-ai-Prototype/
├── backend/           # FastAPI backend
├── frontend/          # React frontend
└── README.md         # This file
```

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `POST /upload` - Upload legal document
- `POST /process` - Process document with Document AI
- `POST /explain` - Get clause explanation
- `POST /chat` - Interactive Q&A with memory
- `GET /sessions` - Get user sessions

## Environment Variables

See `backend/env.example` for required Google Cloud configuration.

### Required Google Cloud Services:

- **Document AI API** - For document parsing
- **Vertex AI API** - For LLM capabilities
- **Firestore API** - For session storage

---
