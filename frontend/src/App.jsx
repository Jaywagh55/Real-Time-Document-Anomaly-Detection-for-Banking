import { useState } from "react";

const SAMPLE_DOCUMENTS = [
  {
    id: "doc-001",
    type: "land_record",
    filename: "encumbrance_certificate.pdf",
    content:
      "Customer name: Rajesh Kumar. Survey no: 12567. Area: 3500 sqft. Encumbrance date: 12-03-2026. Transaction amount: ₹1,25,00,000.",
  },
  {
    id: "doc-002",
    type: "financial_statement",
    filename: "profit_and_loss.pdf",
    content:
      "Total revenue: ₹1,20,00,000. Net profit: ₹32,00,000. GSTIN: 27ABCDE1234F1Z5. PAN: ABCDE1234F.",
  },
  {
    id: "doc-003",
    type: "legal_document",
    filename: "noc_letter.pdf",
    content:
      "NOC issued by seller: Suresh Patel. Property transfer date: 15-03-2026. Survey no: 12567.",
  },
];

const TEAM_DETAILS = {
  name: "AeroSpy",
  institution: "Nutan College Of Engineering And Research",
  track: "Banking & FinTech",
  members: [
    { name: "Siddhant Pawale", role: "Team Lead & Product Architect" },
    { name: "Jay Wagh", role: "Backend Developer" },
    { name: "Rohan More", role: "Frontend Developer" },
    { name: "Rutvik Chopade", role: "AI/ML Engineer" },
    { name: "Vedant Pawale", role: "Data Analyst & QA" },
  ],
};

function App() {
  const [applicationId, setApplicationId] = useState("app-001");
  const [customerId, setCustomerId] = useState("cust-001");
  const [documents, setDocuments] = useState(SAMPLE_DOCUMENTS.map((doc) => doc.content).join("\n"));
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [page, setPage] = useState("dashboard");

  const getPayload = () => ({
    application_id: applicationId,
    customer_id: customerId,
    documents: documents
      .split("\n")
      .filter(Boolean)
      .map((line, index) => ({
        id: `doc-${index + 1}`,
        type: index === 0 ? "land_record" : index === 1 ? "financial_statement" : "legal_document",
        filename: `document-${index + 1}.pdf`,
        content: line,
      })),
  });

  const submitAnalysis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (selectedFiles && selectedFiles.length > 0) {
        const form = new FormData();
        form.append("application_id", applicationId);
        form.append("customer_id", customerId);
        for (const f of selectedFiles) {
          form.append("files", f, f.name);
        }

        const response = await fetch("/api/v1/analyze_files", {
          method: "POST",
          body: form,
        });
        if (!response.ok) throw new Error(`Server returned ${response.status}`);
        const data = await response.json();
        setResult(data);
      } else {
        const payload = getPayload();
        const response = await fetch("/api/v1/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error(`Server returned ${response.status}`);
        const data = await response.json();
        setResult(data);
      }
    } catch (err) {
      setError(err.message || "Unable to analyze documents.");
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => {
    setApplicationId("app-001");
    setCustomerId("cust-001");
    setDocuments(SAMPLE_DOCUMENTS.map((doc) => doc.content).join("\n"));
    setResult(null);
    setError(null);
  };

  const prettyPrint = (value) => {
    if (!value) return "None detected";
    return typeof value === "string" ? value : JSON.stringify(value, null, 2);
  };

  const renderTeamPage = () => (
    <section className="panel team-page-panel">
      <div className="team-summary">
        <h2>Team Details</h2>
        <p>AeroSpy delivers secure underwriting signals for banking and finance.</p>
        <p><strong>Institution:</strong> {TEAM_DETAILS.institution}</p>
        <p><strong>Track:</strong> {TEAM_DETAILS.track}</p>
      </div>
      <div className="team-members">
        <h4>Members</h4>
        <ul>
          {TEAM_DETAILS.members.map((member, index) => (
            <li key={index}>
              <strong>{member.name}</strong>
              <span>{member.role}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );

  return (
    <div className="app-shell">
      <header>
        <div className="brand">
          <div className="brand-badge">DocuShield</div>
          <div>
            <h1>Real-time document anomaly detection</h1>
            <p>Banking underwriting gets a creative, easy-to-use review cockpit.</p>
          </div>
        </div>
      </header>

      <section className="panel hero-panel">
        <div>
          <h2>Run a demo in seconds</h2>
          <p>Load sample documents and get an instant risk verdict for underwriters. The UI shows the full document bundle, risk score, and anomaly evidence.</p>
        </div>
        <div className="hero-actions">
          <button className="secondary" onClick={loadSample} disabled={loading}>
            Load Sample Bundle
          </button>
          <button onClick={submitAnalysis} disabled={loading || !documents}>
            {loading ? "Analyzing..." : "Analyze Documents"}
          </button>
        </div>
      </section>

      <section className="panel page-nav">
        <button className={page === "dashboard" ? "active" : "secondary"} onClick={() => setPage("dashboard")}>Dashboard</button>
        <button className={page === "team" ? "active" : "secondary"} onClick={() => setPage("team")}>Team Details</button>
      </section>

      {page === "dashboard" && (
        <>
          <section className="panel grid-panel">
            <div className="panel-card">
              <h3>Application details</h3>
              <div className="field-row">
                <label>Application ID</label>
                <input value={applicationId} onChange={(e) => setApplicationId(e.target.value)} placeholder="app-001" />
              </div>
              <div className="field-row">
                <label>Customer ID</label>
                <input value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="cust-001" />
              </div>
            </div>

            <div className="panel-card large-card">
              <h3>Document contents</h3>
              <textarea value={documents} onChange={(e) => setDocuments(e.target.value)} rows={10} />
              <div style={{ marginTop: 12 }}>
                <label style={{ display: "block", marginBottom: 6 }}>Upload files (PDF / image) — optional</label>
                <input
                  type="file"
                  multiple
                  onChange={(e) => setSelectedFiles(Array.from(e.target.files || []))}
                  accept=".pdf,image/*"
                />
                <p className="hint">Files take precedence over pasted text. Remove files to use text input.</p>
              </div>
              <p className="hint">Enter one document per line, or click Load Sample Bundle.</p>
            </div>
          </section>

          {error && <section className="panel error-panel">Error: {error}</section>}

      {result && (
        <section className="panel result-panel">
          <div className="result-header">
            <div>
              <h2>Risk summary</h2>
              <p>{result.anomalies.length} anomaly findings detected</p>
            </div>
            <div className={`risk-pill risk-${result.risk_level}`}>
              {result.risk_level.toUpperCase()}
            </div>
          </div>

          <div className="score-card">
            <span>Risk score</span>
            <strong>{result.risk_score}</strong>
          </div>

          <div className="result-grid">
            <div className="result-box">
              <h4>Registry validation</h4>
              <pre>{prettyPrint(result.registry_validation)}</pre>
            </div>
            <div className="result-box">
              <h4>Cross-document links</h4>
              <pre>{prettyPrint(result.cross_document_matches)}</pre>
            </div>
          </div>

          {result.document_analysis && (
            <div className="analysis-panel">
              <h3>Document analysis</h3>
              <div className="document-grid">
                {result.document_analysis.map((doc) => (
                  <article key={doc.id} className="document-card">
                    <div className="document-card-header">
                      <div>
                        <h4>{doc.filename || doc.id}</h4>
                        <p>{doc.type.replace(/_/g, " ")}</p>
                      </div>
                      <span className="doc-badge">{doc.id}</span>
                    </div>
                    <div className="document-section">
                      <strong>Extracted text</strong>
                      <p>{doc.text || "No extracted text provided."}</p>
                    </div>
                    <div className="document-section">
                      <strong>Entities</strong>
                      <pre>{prettyPrint(doc.entities)}</pre>
                    </div>
                    <div className="document-section">
                      <strong>Forensics</strong>
                      <pre>{prettyPrint(doc.forensics)}</pre>
                      {doc.forensics && doc.forensics.ela && doc.forensics.ela.heatmap && (
                        <div style={{ marginTop: 8 }}>
                          <strong>ELA heatmap</strong>
                          <div>
                            <img
                              alt="ELA heatmap"
                              src={`data:image/png;base64,${doc.forensics.ela.heatmap}`}
                              style={{ maxWidth: "100%", borderRadius: 8, marginTop: 8 }}
                            />
                            <div style={{ marginTop: 6 }}>
                              <small>ELA score: {doc.forensics.ela.score}</small>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}

          <div className="anomalies-list">
            <h3>Flagged anomalies</h3>
            <ul>
              {result.anomalies.map((item, index) => (
                <li key={index} className={item.severity}>
                  <strong>{item.issue}</strong>
                  <p>{item.evidence}</p>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}
        </>
      )}

      {page === "team" && renderTeamPage()}
    </div>
  );
}

export default App;
