export interface DocumentMetadata {
  document_type: string;
  parties: string[];
  dates: string[];
  contract_value?: string;
  jurisdiction?: string;
  governing_law?: string;
}

export interface Clause {
  id: string;
  title: string;
  text: string;
  clause_type: string;
  metadata: Record<string, any>;
  start_page: number;
  end_page: number;
}

export interface DocumentAnalysis {
  document_id: string;
  document_name: string;
  metadata: DocumentMetadata;
  clauses: Clause[];
  summary?: string;
  processing_timestamp: string;
  confidence_score: number;
}

export interface ClauseExplanation {
  clause_id: string;
  original_text: string;
  explanation: string;
  key_points: string[];
  risks: string[];
  plain_language: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface SessionData {
  sessionId: string;
  documentName: string;
  analysis: DocumentAnalysis;
  conversationHistory: ChatMessage[];
}

export interface UploadResponse {
  session_id: string;
  document_name: string;
  analysis: DocumentAnalysis;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  timestamp: string;
}

export interface SummaryResponse {
  session_id: string;
  summary: string;
  message: string;
}

export interface SessionInfo {
  clauses_count: any;
  session_id: string;
  document_name: string;
  created_at: string;
  last_accessed: string;
  message_count: number;
}
