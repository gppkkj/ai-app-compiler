"use client";

import { useState } from "react";

type ApiResult = {
  intent?: unknown;
  architecture?: unknown;
  schema?: unknown;
  validation?: unknown;
  repaired_schema?: unknown;
  runtime?: unknown;
  metrics?: unknown;
  error?: string;
};

export default function Home() {
  const [prompt, setPrompt] = useState(
    "Build a CRM with login, contacts, analytics dashboard, and premium subscriptions"
  );

  const [result, setResult] = useState<ApiResult | null>(null);
  const [loading, setLoading] = useState(false);

  const generateApp = async () => {
    try {
      setLoading(true);
      setResult(null);

      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();

      if (!response.ok) {
        setResult({
          error: data?.detail || "Request failed",
        });
        return;
      }

      setResult(data);
    } catch (error) {
      setResult({
        error:
          error instanceof Error
            ? error.message
            : "Something went wrong while calling backend",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <section className="container">
        <div className="hero">
          <p className="kicker">AI App Compiler</p>

          <h1 className="title">Prompt to Production Architecture</h1>

          <p className="subtitle">
            Generate a structured software blueprint with intent extraction,
            architecture planning, schema design, validation, repair, runtime
            mapping, and metrics.
          </p>
        </div>

        <div className="grid">
          <div className="card">
            <label className="label">Product Prompt</label>

            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              className="textarea"
              placeholder="Describe the app you want to generate..."
            />

            <button
              onClick={generateApp}
              disabled={loading || !prompt.trim()}
              className="button"
            >
              {loading ? "Generating..." : "Generate App Blueprint"}
            </button>

            <div className="pipeline">
              <h2>Compiler Pipeline</h2>

              <ul>
                <li>Intent Extraction</li>
                <li>Architecture Planning</li>
                <li>Schema Generation</li>
                <li>Validation</li>
                <li>Repair Engine</li>
                <li>Runtime Mapping</li>
                <li>Metrics Tracking</li>
              </ul>
            </div>
          </div>

          <div className="card">
            <div className="output-header">
              <h2>Generated Output</h2>

              {result && !result.error && <span className="badge">Success</span>}
            </div>

            {!result && !loading && (
              <div className="empty">
                Your generated app blueprint will appear here.
              </div>
            )}

            {loading && (
              <div className="loading">Running compiler pipeline...</div>
            )}

            {result && (
              <pre className="result">{JSON.stringify(result, null, 2)}</pre>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}