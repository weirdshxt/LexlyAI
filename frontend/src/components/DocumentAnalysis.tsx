import React, { useEffect, useState } from "react";
import { ApiService } from "../services/apiService";
import {
  SessionData,
  DocumentAnalysis as DocumentAnalysisType,
  ClauseExplanation,
} from "../types";
import "../style.css";

interface DocumentAnalysisProps {
  sessionData: SessionData;
  documentAnalysis: DocumentAnalysisType;
}

const DocumentAnalysis: React.FC<DocumentAnalysisProps> = ({
  sessionData,
  documentAnalysis,
}) => {
  const [expandedClause, setExpandedClause] = useState<string | false>(false);
  const [clauseExplanations, setClauseExplanations] = useState<
    Record<string, ClauseExplanation>
  >({});
  const [loadingExplanations, setLoadingExplanations] = useState<Set<string>>(
    new Set()
  );
  const [documentSummary, setDocumentSummary] = useState<string | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionData?.sessionId) {
      setError("Invalid session: No session ID available");
    } else {
      setError(null);
    }
  }, [sessionData]);

  const handleClauseExpand = async (clauseId: string) => {
    setExpandedClause(expandedClause === clauseId ? false : clauseId);
    if (!clauseExplanations[clauseId] && expandedClause !== clauseId) {
      setLoadingExplanations((prev) => new Set(prev).add(clauseId));
      try {
        const explanation = await ApiService.explainClause(
          sessionData.sessionId,
          clauseId
        );
        setClauseExplanations((prev) => ({ ...prev, [clauseId]: explanation }));
      } catch (error) {
        // handle error silently
      } finally {
        setLoadingExplanations((prev) => {
          const newSet = new Set(prev);
          newSet.delete(clauseId);
          return newSet;
        });
      }
    }
  };

  const handleGenerateSummary = async () => {
    if (!sessionData?.sessionId) return;
    setLoadingSummary(true);
    try {
      const response = await ApiService.summarizeDocument(
        sessionData.sessionId
      );
      setDocumentSummary(response.summary);
    } catch (error: any) {
      setDocumentSummary("Failed to generate summary. Please try again.");
    } finally {
      setLoadingSummary(false);
    }
  };

  const cleanMarkdown = (text: string) => {
    let t = text.replace(/^[-*•]\s+/, "");
    t = t.replace(/\*\*(.*?)\*\*/g, "$1");
    return t.trim();
  };

  const renderPoint = (text: string) => {
    const cleaned = cleanMarkdown(text);
    const idx = cleaned.indexOf(":");
    if (idx > 0 && idx < cleaned.length - 1) {
      const title = cleaned.slice(0, idx).trim();
      const desc = cleaned.slice(idx + 1).trim();
      return (
        <span>
          <span className="da-point-title">{title}:</span> {desc}
        </span>
      );
    }
    return <span>{cleaned}</span>;
  };

  return (
    <div className="da-root">
      {error && <div className="da-alert error">{error}</div>}
      <section className="da-overview">
        <h1>Legal Document Analysis</h1>
        <div className="da-meta-grid">
          <div className="da-meta-card">
            <div className="da-meta-title">Parties</div>
            {documentAnalysis.metadata.parties.length > 0 ? (
              <ul className="da-meta-list">
                {documentAnalysis.metadata.parties.map((party, index) => (
                  <li key={index}>{party}</li>
                ))}
              </ul>
            ) : (
              <div className="da-meta-empty">No parties identified</div>
            )}
          </div>
          <div className="da-meta-card">
            <div className="da-meta-title">Key Dates</div>
            {documentAnalysis.metadata.dates.length > 0 ? (
              <ul className="da-meta-list">
                {documentAnalysis.metadata.dates.map((date, index) => (
                  <li key={index}>{date}</li>
                ))}
              </ul>
            ) : (
              <div className="da-meta-empty">No dates identified</div>
            )}
          </div>
          <div className="da-meta-card">
            <div className="da-meta-title">Document Info</div>
            <div>
              Type:{" "}
              {documentAnalysis.metadata.document_type
                .replace("_", " ")
                .toUpperCase()}
            </div>
            {documentAnalysis.metadata.contract_value && (
              <div>Value: {documentAnalysis.metadata.contract_value}</div>
            )}
            {documentAnalysis.metadata.jurisdiction && (
              <div>Jurisdiction: {documentAnalysis.metadata.jurisdiction}</div>
            )}
            <div>
              Confidence: {(documentAnalysis.confidence_score * 100).toFixed(1)}
              %
            </div>
          </div>
        </div>
      </section>
      <section className="da-summary">
        <div className="da-summary-header">
          <h2>Executive Summary</h2>
          <button
            className="da-summary-btn"
            onClick={handleGenerateSummary}
            disabled={loadingSummary}
          >
            {loadingSummary ? "Generating..." : "Generate Summary"}
          </button>
        </div>
        {documentSummary ? (
          <div className="da-summary-content info">{documentSummary}</div>
        ) : (
          <div className="da-summary-placeholder">
            Click "Generate Summary" to get an AI-powered overview of the entire
            document.
          </div>
        )}
      </section>
      <section className="da-clauses">
        <h2>Document Clauses ({documentAnalysis.clauses.length})</h2>
        {documentAnalysis.clauses.length > 0 ? (
          <ul className="da-clause-list">
            {documentAnalysis.clauses.map((clause) => (
              <li key={clause.id} className="da-clause-item">
                <div
                  className="da-clause-header"
                  onClick={() => handleClauseExpand(clause.id)}
                >
                  <span className="da-clause-title">{clause.title}</span>
                  <span className="da-clause-type">
                    [{clause.clause_type.replace("_", " ").toUpperCase()}]
                  </span>
                  <span className="da-clause-length">
                    {clause.text.length} chars
                  </span>
                  <span className="da-clause-toggle">
                    {expandedClause === clause.id ? "▲" : "▼"}
                  </span>
                </div>
                {expandedClause === clause.id && (
                  <div className="da-clause-details">
                    <div className="da-clause-original">
                      <div className="da-clause-label">Original Text:</div>
                      <div className="da-clause-text">
                        {clause.text.length > 1200
                          ? clause.text.slice(0, 1200) + "\n... [truncated]"
                          : clause.text}
                      </div>
                    </div>
                    {loadingExplanations.has(clause.id) ? (
                      <div className="da-clause-loading">
                        Loading explanation...
                      </div>
                    ) : clauseExplanations[clause.id] ? (
                      <div className="da-clause-explanation">
                        <div className="da-clause-label">AI Explanation:</div>
                        <div className="da-explanation-main">
                          {clauseExplanations[clause.id].explanation}
                        </div>
                        <div className="da-explanation-grid">
                          <div className="da-explanation-points">
                            <div className="da-clause-label">Key Points:</div>
                            <ul>
                              {clauseExplanations[clause.id].key_points.map(
                                (point, idx) => (
                                  <li key={idx}>{renderPoint(point)}</li>
                                )
                              )}
                            </ul>
                          </div>
                          <div className="da-explanation-risks">
                            <div className="da-clause-label">
                              Risks & Concerns:
                            </div>
                            <ul>
                              {clauseExplanations[clause.id].risks.map(
                                (risk, idx) => (
                                  <li key={idx}>{renderPoint(risk)}</li>
                                )
                              )}
                            </ul>
                          </div>
                        </div>
                        <div className="da-explanation-plain">
                          <div className="da-clause-label">
                            Plain Language Version:
                          </div>
                          <div className="da-explanation-plain-content">
                            {clauseExplanations[clause.id].plain_language}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="da-clause-placeholder">
                        Expand to see AI-powered explanation of this clause.
                      </div>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <div className="da-alert warning">
            No clauses were extracted from this document. This might be due to
            document format or content issues.
          </div>
        )}
      </section>
    </div>
  );
};

export default DocumentAnalysis;
