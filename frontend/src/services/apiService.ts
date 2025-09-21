import axios from "axios";
import {
  UploadResponse,
  ClauseExplanation,
  ChatResponse,
  SummaryResponse,
  SessionInfo,
  SessionData,
} from "../types";

const API_BASE_URL =  "https://lexly-ai-backend-303476233028.us-central1.run.app" || "http://localhost:8000";

class ApiService {
  private static api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
  });

  static async uploadDocument(file: File): Promise<{ data: UploadResponse }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response;
  }

  static async explainClause(
    sessionId: string,
    clauseId: string
  ): Promise<ClauseExplanation> {
    const response = await this.api.post(`/explain/${sessionId}/${clauseId}`);
    return response.data;
  }

  static async summarizeDocument(sessionId: string): Promise<SummaryResponse> {
    if (!sessionId) {
      throw new Error("Session ID is required");
    }
    const response = await this.api.post(`/summarize/${sessionId}`);
    return response.data;
  }

  static async chatWithDocument(
    sessionId: string,
    message: string
  ): Promise<ChatResponse> {
    if (!sessionId) {
      throw new Error("Session ID is required for chat");
    }
    try {
      const response = await this.api.post(`/chat/${sessionId}`, {
        content: message,
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error("Chat session not found. Please reload the page.");
      }
      throw error;
    }
  }

  static async getSession(sessionId: string): Promise<SessionData> {
    const response = await this.api.get(`/sessions/${sessionId}`);
    const payload = response.data;
    const data = payload.data;

    return {
      sessionId: payload.session_id || sessionId,
      documentName: data?.analysis?.document_name,
      analysis: data?.analysis,
      conversationHistory: data?.conversation_history || [],
    } as SessionData;
  }

  static async listSessions(): Promise<SessionInfo[]> {
    const response = await this.api.get("/sessions");
    return response.data.sessions;
  }

  static async getHealth(): Promise<{ message: string; version: string }> {
    const response = await this.api.get("/");
    return response.data;
  }

  static async deleteSession(sessionId: string): Promise<{ message: string }> {
    if (!sessionId) {
      throw new Error("Session ID is required");
    }
    const response = await this.api.delete(`/sessions/${sessionId}`);
    return response.data;
  }
}

export { ApiService };
