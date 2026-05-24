import { useState } from "react";

function App() {
  const [applicationId, setApplicationId] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [documents, setDocuments] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submitAnalysis = async () => {
    setLoading(true);
    const payload = {
      application_id: applicationId || "app-001",
      customer_id: customerId || "cust-001",
      documents: documents
        .split("\n")
        .filter(Boolean)
        .map((line, index) => ({
          id: `doc-${index + 1}`,
          type: "unknown",
          filename: `document-${index + 1}.pdf`,
          content: line,
        })),
    };

    const response = await fetch("/api/v1/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div className="app-shell">
      <header>
        <h1>DocuShield</h1>
        <p>Real-time document anomaly detection for banking underwriting.</p>
      </header>

      <section className="panel">
        <div className="field-row">
          <label>Application ID</label>
          <input value={applicationId} onChange={(e) => setApplicationId(e.target.value)} placeholder="app-001" />
        </div>

        <div className="field-row">
          <label>Customer ID</label>
          <input value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="cust-001" />
        </div>

        <div className="field-row">
          <label>Document Content (one line per document)</label>
          <textarea value={documents} onChange={(e) => setDocuments(e.target.value)} rows={8} placeholder="Enter document text samples here..." />
        </div>

        <button onClick={submitAnalysis} disabled={loading || !documents}>Analyze Documents</button>
      </section>

      {loading && <p>Analyzing documents...</p>}

      {result && (
        <section className="panel result-panel">
          <h2>Risk Summary</h2>
          <p>
            Risk score: <strong>{result.risk_score}</strong> ({result.risk_level})
          </p>
          <h3>Anomalies</h3>
          <ul>
            {result.anomalies.map((item, index) => (
              <li key={index}>
                <strong>{item.issue}</strong> — {item.severity}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export default App;
