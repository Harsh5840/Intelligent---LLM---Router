"use client";
import { useState, useEffect, useRef } from "react";
import styles from "./Architecture.module.css";

const PHASES = [
  {
    num: 1,
    title: "API Layer",
    desc: "FastAPI with Pydantic v2 schema validation. Single /chat endpoint receives all requests.",
    color: "var(--accent-indigo)",
    tech: "FastAPI · Pydantic v2 · Uvicorn",
  },
  {
    num: 2,
    title: "Feature Extraction",
    desc: "Converts raw prompts into routing signals — token count, domain flags, code detection, complexity score.",
    color: "var(--accent-cyan)",
    tech: "NLP · Regex · SentenceTransformers",
  },
  {
    num: 3,
    title: "Rule-Based Router",
    desc: "Heuristic routing using complexity thresholds, domain flags, user tier, and code-block presence.",
    color: "var(--accent-violet)",
    tech: "Decision Rules · Tier Logic",
  },
  {
    num: 4,
    title: "Data Collection",
    desc: "Logs every routing decision with features, latency, cost estimate, and outcome for feedback loops.",
    color: "var(--accent-emerald)",
    tech: "SQLAlchemy 2 · PostgreSQL · asyncpg",
  },
  {
    num: 5,
    title: "ML Classifier",
    desc: "Feature-flag controlled ML model that predicts optimal model based on historical performance data.",
    color: "var(--accent-rose)",
    tech: "scikit-learn · Feature Flags",
  },
  {
    num: 6,
    title: "RAG Routing",
    desc: "Vector similarity search against past query embeddings to recommend models with proven track records.",
    color: "var(--accent-amber)",
    tech: "Pinecone · Embeddings · Cosine Sim",
  },
  {
    num: 7,
    title: "Decision Engine",
    desc: "Multi-factor weighted scorer: quality (0.30), cost (0.25), latency (0.15), ML (0.15), RAG (0.15).",
    color: "var(--accent-indigo)",
    tech: "Weighted Scoring · ModelCandidate",
  },
  {
    num: 8,
    title: "Response Cache",
    desc: "Redis-backed semantic cache. Checks before routing, caches after inference to cut repeated costs.",
    color: "var(--accent-cyan)",
    tech: "Redis 7 · hiredis · TTL Policies",
  },
  {
    num: 9,
    title: "Observability",
    desc: "Prometheus metrics, structlog events, and routing metadata returned to client for full traceability.",
    color: "var(--accent-emerald)",
    tech: "Prometheus · structlog · Health Checks",
  },
];

const FLOW_STEPS = [
  { label: "Client Request", icon: "📨" },
  { label: "Validate & Normalize", icon: "✅" },
  { label: "Check Cache", icon: "💾" },
  { label: "Extract Features", icon: "🔍" },
  { label: "Score Models", icon: "📊" },
  { label: "Select & Execute", icon: "⚡" },
  { label: "Log & Cache", icon: "📝" },
  { label: "Return Response", icon: "📤" },
];

export default function Architecture() {
  const [activePhase, setActivePhase] = useState(0);
  const [flowStep, setFlowStep] = useState(0);

  useEffect(() => {
    const iv = setInterval(() => {
      setFlowStep((p) => (p + 1) % FLOW_STEPS.length);
    }, 1800);
    return () => clearInterval(iv);
  }, []);

  return (
    <section id="architecture" className={styles.section}>
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLabel}>System Design</span>
          <h2 className={styles.sectionTitle}>Architecture Deep Dive</h2>
          <p className={styles.sectionDesc}>
            9-phase modular architecture — each layer is isolated, testable, and can evolve independently.
          </p>
        </div>

        {/* Request Flow Animation */}
        <div className={styles.flowContainer}>
          <div className={styles.flowTrack}>
            {FLOW_STEPS.map((step, i) => (
              <div
                key={i}
                className={`${styles.flowNode} ${
                  i === flowStep ? styles.flowNodeActive : ""
                } ${i < flowStep ? styles.flowNodeDone : ""}`}
              >
                <div className={styles.flowIcon}>{step.icon}</div>
                <span className={styles.flowLabel}>{step.label}</span>
                {i < FLOW_STEPS.length - 1 && (
                  <div
                    className={`${styles.flowConnector} ${
                      i < flowStep ? styles.flowConnectorActive : ""
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Phase Grid */}
        <div className={styles.phaseGrid}>
          {PHASES.map((phase, idx) => (
            <button
              key={phase.num}
              className={`${styles.phaseCard} ${
                activePhase === idx ? styles.phaseCardActive : ""
              }`}
              onClick={() => setActivePhase(idx)}
              style={{ "--phase-color": phase.color }}
            >
              <div className={styles.phaseNum}>Phase {phase.num}</div>
              <h3 className={styles.phaseTitle}>{phase.title}</h3>
              <p className={styles.phaseDesc}>{phase.desc}</p>
              <div className={styles.phaseTech}>{phase.tech}</div>
            </button>
          ))}
        </div>

        {/* Design Decisions */}
        <div className={styles.decisions}>
          <h3 className={styles.decisionsTitle}>Key Design Decisions</h3>
          <div className={styles.decisionGrid}>
            {[
              {
                q: "Why centralized router?",
                a: "Governance and consistency — one place to update routing policy vs scattered app-level logic.",
              },
              {
                q: "Why heuristics first?",
                a: "Faster to production, easier to debug. ML can be layered on via feature flags without rewriting.",
              },
              {
                q: "Why provider abstraction?",
                a: "Avoids vendor lock-in. New models plug in through the registry without touching API contracts.",
              },
              {
                q: "Why cache at response layer?",
                a: "Repeated prompts skip inference entirely — directly improves p95 latency and cuts token spend.",
              },
            ].map((d, i) => (
              <div key={i} className={styles.decisionCard}>
                <h4 className={styles.decisionQ}>{d.q}</h4>
                <p className={styles.decisionA}>{d.a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
