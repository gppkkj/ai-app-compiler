"use client";

import { useState } from "react";

type GenerateResponse = {
  intent?: Record<string, unknown>;
  architecture?: Record<string, unknown>;
  schema?: Record<string, unknown>;
  validation?: {
    valid?: boolean;
    errors?: string[];
    warnings?: string[];
  };
  repaired_schema?: Record<string, unknown>;
  repair_log?: unknown[];
  runtime?: Record<string, unknown>;
  generated_files?: string[];
  metrics?: Record<string, unknown>;
  project_zip?: string;
};

export default function Home() {
  const [prompt, setPrompt] = useState(
    "Build an ice cream ordering app with menu, cart, payments, admin dashboard, and premium subscriptions"
  );

  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [evaluation, setEvaluation] = useState<Record<string, unknown> | null>(
    null
  );
  const [runtimeRoutes, setRuntimeRoutes] = useState<Record<
    string,
    unknown
  > | null>(null);

  const [loading, setLoading] = useState(false);
  const [evaluationLoading, setEvaluationLoading] = useState(false);
  const [runtimeLoading, setRuntimeLoading] = useState(false);
  const [error, setError] = useState("");

  const API_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function handleGenerate() {
    try {
      setLoading(true);
      setError("");
      setResult(null);

      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          prompt
        })
      });

      if (!response.ok) {
        throw new Error("Failed to generate application config");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while generating"
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleEvaluation() {
    try {
      setEvaluationLoading(true);
      setError("");
      setEvaluation(null);

      const response = await fetch(`${API_URL}/evaluation/run`);

      if (!response.ok) {
        throw new Error("Failed to run evaluation");
      }

      const data = await response.json();
      setEvaluation(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while running evaluation"
      );
    } finally {
      setEvaluationLoading(false);
    }
  }

  async function handleRuntimeRoutes() {
    try {
      setRuntimeLoading(true);
      setError("");
      setRuntimeRoutes(null);

      const response = await fetch(`${API_URL}/runtime/routes`);

      if (!response.ok) {
        throw new Error("Failed to load runtime routes");
      }

      const data = await response.json();
      setRuntimeRoutes(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while loading runtime routes"
      );
    } finally {
      setRuntimeLoading(false);
    }
  }

  const validationStatus =
    result?.validation?.valid === true
      ? "Valid"
      : result?.validation?.valid === false
      ? "Invalid"
      : "Not generated";

  const runtimeStatus =
    result?.runtime && "runtime_status" in result.runtime
      ? String(result.runtime.runtime_status)
      : "Not generated";

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <section className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-10 rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl">
          <p className="mb-3 text-sm font-semibold uppercase tracking-[0.3em] text-violet-400">
            AI Platform Engineering
          </p>

          <h1 className="mb-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            AI App Compiler
          </h1>

          <p className="max-w-4xl text-base leading-7 text-slate-300 md:text-lg">
            A compiler-style software generation system that converts natural
            language product requirements into structured intent, architecture,
            strict schema, validation, repair, runtime execution plan, and
            generated artifacts.
          </p>

          <div className="mt-6 grid gap-3 text-sm text-slate-300 md:grid-cols-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
              Natural Language
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
              Validated Schema
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
              Repair Engine
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
              Runtime Simulation
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
            <h2 className="mb-2 text-2xl font-semibold text-white">
              Generate Application
            </h2>

            <p className="mb-5 text-sm leading-6 text-slate-400">
              Enter a product prompt. The backend will run the full compiler
              pipeline: intent extraction, architecture planning, schema
              generation, validation, repair, runtime mapping, and codegen.
            </p>

            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              className="min-h-44 w-full rounded-2xl border border-slate-700 bg-slate-950 p-4 text-sm leading-6 text-slate-100 outline-none ring-0 placeholder:text-slate-500 focus:border-violet-500"
              placeholder="Build a CRM with login, contacts, dashboard, role-based access, and premium subscriptions..."
            />

            <button
              onClick={handleGenerate}
              disabled={loading || prompt.trim().length === 0}
              className="mt-4 w-full rounded-2xl bg-violet-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:bg-slate-700"
            >
              {loading ? "Generating..." : "Run Compiler Pipeline"}
            </button>

            {error && (
              <div className="mt-4 rounded-2xl border border-red-800 bg-red-950/60 p-4 text-sm text-red-200">
                {error}
              </div>
            )}

            <div className="mt-6 grid gap-3 text-sm">
              <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950 p-4">
                <span className="text-slate-400">Validation</span>
                <span
                  className={
                    validationStatus === "Valid"
                      ? "font-semibold text-emerald-400"
                      : "font-semibold text-amber-400"
                  }
                >
                  {validationStatus}
                </span>
              </div>

              <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950 p-4">
                <span className="text-slate-400">Runtime</span>
                <span className="font-semibold text-cyan-400">
                  {runtimeStatus}
                </span>
              </div>

              <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950 p-4">
                <span className="text-slate-400">Project ZIP</span>
                <span className="font-semibold text-slate-200">
                  {result?.project_zip || "Not generated"}
                </span>
              </div>
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-2">
              <button
                onClick={handleEvaluation}
                disabled={evaluationLoading}
                className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-violet-500"
              >
                {evaluationLoading ? "Running..." : "Run Evaluation"}
              </button>

              <button
                onClick={handleRuntimeRoutes}
                disabled={runtimeLoading}
                className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm font-semibold text-slate-100 transition hover:border-cyan-500"
              >
                {runtimeLoading ? "Loading..." : "View Runtime Routes"}
              </button>
            </div>
          </div>

          <div className="space-y-6">
            {result && (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
                <div className="mb-4 flex items-center justify-between gap-4">
                  <h2 className="text-2xl font-semibold text-white">
                    Generated Compiler Output
                  </h2>

                  <span className="rounded-full border border-emerald-700 bg-emerald-950 px-3 py-1 text-xs font-semibold text-emerald-300">
                    Generated
                  </span>
                </div>

                <div className="mb-5 grid gap-3 md:grid-cols-3">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">
                      App Type
                    </p>
                    <p className="mt-1 font-semibold text-white">
                      {String(result.intent?.app_type || "Unknown")}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">
                      Valid
                    </p>
                    <p className="mt-1 font-semibold text-emerald-400">
                      {String(result.validation?.valid)}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">
                      Latency
                    </p>
                    <p className="mt-1 font-semibold text-cyan-400">
                      {String(result.metrics?.latency_seconds || "N/A")}s
                    </p>
                  </div>
                </div>

                <pre className="max-h-[650px] overflow-auto rounded-2xl border border-slate-800 bg-black p-5 text-xs leading-6 text-slate-200">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}

            {evaluation && (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
                <h2 className="mb-4 text-2xl font-semibold text-white">
                  Evaluation Results
                </h2>

                <pre className="max-h-[500px] overflow-auto rounded-2xl border border-slate-800 bg-black p-5 text-xs leading-6 text-slate-200">
                  {JSON.stringify(evaluation, null, 2)}
                </pre>
              </div>
            )}

            {runtimeRoutes && (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
                <h2 className="mb-4 text-2xl font-semibold text-white">
                  Runtime Routes
                </h2>

                <pre className="max-h-[500px] overflow-auto rounded-2xl border border-slate-800 bg-black p-5 text-xs leading-6 text-slate-200">
                  {JSON.stringify(runtimeRoutes, null, 2)}
                </pre>
              </div>
            )}

            {!result && !evaluation && !runtimeRoutes && (
              <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 text-center shadow-xl">
                <h2 className="mb-3 text-2xl font-semibold text-white">
                  Ready to Compile
                </h2>

                <p className="text-sm leading-6 text-slate-400">
                  Run the compiler pipeline to see structured intent,
                  architecture, schema, validation, repair output, runtime
                  manifest, generated files, and metrics.
                </p>
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}