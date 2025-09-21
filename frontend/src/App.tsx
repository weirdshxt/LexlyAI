import React, { useState } from "react";
import DocumentUpload from "./components/DocumentUpload";
import DocumentAnalysis from "./components/DocumentAnalysis";
import ChatInterface from "./components/ChatInterface";
import { ApiService } from "./services/apiService";
import { DocumentAnalysis as DocumentAnalysisType, SessionData } from "./types";
import "./style.css";

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [documentAnalysis, setDocumentAnalysis] =
    useState<DocumentAnalysisType | null>(null);

  const handleTabChange = (tabIdx: number) => setCurrentTab(tabIdx);

  const handleDocumentUpload = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const response = await ApiService.uploadDocument(file);
      if (response.data?.session_id) {
        const newSessionData = {
          sessionId: response.data.session_id,
          documentName: response.data.document_name,
          analysis: response.data.analysis,
          conversationHistory: [],
        };
        setSessionData(newSessionData);
        setDocumentAnalysis(response.data.analysis);
        setSuccess("Document uploaded and processed successfully!");
        setCurrentTab(1);
      } else {
        throw new Error("Invalid response: missing session ID");
      }
    } catch (err: any) {
      setError(err.message || "Failed to upload document");
      setSessionData(null);
      setDocumentAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSessionLoad = (session: SessionData) => {
    setSessionData(session);
    setDocumentAnalysis(session.analysis);
    setCurrentTab(1);
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="app-title">Lexly AI</div>
        <nav className="app-nav">
          <button
            className={currentTab === 0 ? "active" : ""}
            onClick={() => handleTabChange(0)}
          >
            Upload
          </button>
          <button
            className={currentTab === 1 ? "active" : ""}
            onClick={() => handleTabChange(1)}
            disabled={!documentAnalysis}
          >
            Analysis
          </button>
          <button
            className={currentTab === 2 ? "active" : ""}
            onClick={() => handleTabChange(2)}
            disabled={!documentAnalysis}
          >
            AI Assistant
          </button>
        </nav>
      </header>
      <main className="app-main">
        {currentTab === 0 && (
          <DocumentUpload
            onUpload={handleDocumentUpload}
            onSessionLoad={handleSessionLoad}
            loading={loading}
          />
        )}
        {currentTab === 1 && documentAnalysis && sessionData && (
          <DocumentAnalysis
            sessionData={sessionData}
            documentAnalysis={documentAnalysis}
          />
        )}
        {currentTab === 2 && documentAnalysis && sessionData && (
          <ChatInterface
            sessionData={sessionData}
            onSessionUpdate={setSessionData}
          />
        )}
        {error && <div className="app-alert error">{error}</div>}
        {success && <div className="app-alert success">{success}</div>}
      </main>
    </div>
  );
}

export default App;
