import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { ApiService } from "../services/apiService";
import { SessionInfo, SessionData } from "../types";
import "../style.css";

interface DocumentUploadProps {
  onUpload: (file: File) => void;
  onSessionLoad: (session: SessionData) => void;
  loading: boolean;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUpload,
  onSessionLoad,
  loading,
}) => {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    multiple: false,
    disabled: loading,
  });

  const loadSessions = async () => {
    try {
      const sessionList = await ApiService.listSessions();
      setSessions(sessionList);
    } catch (error) {
      // handle error silently
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      const sessionData = await ApiService.getSession(sessionId);
      onSessionLoad(sessionData);
    } catch (error) {
      // handle error silently
    }
  };

  React.useEffect(() => {
    loadSessions();
  }, []);

  return (
    <div className="upload-root">
      <section className="upload-hero">
        <h1>Legal Document Analysis</h1>
        <p className="upload-desc">
          Transform your legal documents with AI-powered insights. Upload your document to get instant analysis, smart explanations, and interactive Q&amp;A capabilities.
        </p>
      </section>
      <div {...getRootProps()} className={`upload-dropzone${isDragActive ? " active" : ""}${loading ? " disabled" : ""}`}>
        <input {...getInputProps()} />
        <div className="upload-icon">📄</div>
        <div className="upload-instructions">
          <div className="upload-title">Drag &amp; Drop Your Legal Document</div>
          <div className="upload-sub">or click here to browse files (PDF, DOCX, max 10MB)</div>
        </div>
      </div>
      {sessions.length > 0 && (
        <div className="upload-sessions">
          <h2>Recent Legal Documents</h2>
          <ul className="upload-session-list">
            {sessions.map((session) => (
              <li key={session.session_id} className="upload-session-item">
                <div className="upload-session-info">
                  <span className="upload-session-name">{session.document_name}</span>
                  <span className="upload-session-meta">Created: {new Date(session.created_at).toLocaleDateString()}</span>
                  <span className="upload-session-meta">Last accessed: {new Date(session.last_accessed).toLocaleDateString()}</span>
                  <span className="upload-session-meta">{session.message_count} Messages</span>
                </div>
                <div className="upload-session-actions">
                  <button onClick={() => loadSession(session.session_id)} title="View History">View</button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="upload-help">
        <strong>What happens after upload?</strong>
        <ul>
          <li>Document AI extracts key clauses, parties, and terms</li>
          <li>AI generates plain-language explanations</li>
          <li>Interactive Q&amp;A with document context and memory</li>
          <li>Session data is saved for future reference</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentUpload;
