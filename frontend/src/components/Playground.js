"use client";
import { useState, useCallback, useRef, useEffect } from "react";
import {
  simulateRouting,
  extractFeatures,
  calculateComplexity,
  MODEL_CONFIGS,
  DEMO_QUERIES,
} from "@/lib/router-engine";
import styles from "./Playground.module.css";

const TIERS = ["free", "pro", "enterprise"];

export default function Playground() {
  const [query, setQuery] = useState("");
  const [tier, setTier] = useState("free");
  const [useAdvanced, setUseAdvanced] = useState(false);
  const [result, setResult] = useState(null);
  const [isRouting, setIsRouting] = useState(false);
  const [routingStep, setRoutingStep] = useState(-1);
  const resultRef = useRef(null);

  const ROUTING_STEPS = [
    "Checking cache…",
    "Extracting features…",
    "Scoring candidate models…",
    "Selecting optimal model…",
    "Generating response…",
  ];

  const runRouting = useCallback(
    async (q, t) => {
      const text = q || query;
      const userTier = t || tier;
      if (!text.trim()) return;

      setIsRouting(true);
      setResult(null);

      for (let i = 0; i < ROUTING_STEPS.length; i++) {
        setRoutingStep(i);
        await new Promise((r) => setTimeout(r, 350 + Math.random() * 200));
      }

      const res = simulateRouting(text, userTier, useAdvanced);
      setResult(res);
      setIsRouting(false);
      setRoutingStep(-1);

      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }, 100);
    },
    [query, tier, useAdvanced]
  );

  const loadDemo = (demo) => {
    setQuery(demo.text);
    setTier(demo.tier);
    runRouting(demo.text, demo.tier);
  };

  // Live feature preview
  const liveFeatures = query.trim() ? extractFeatures(query) : null;
  const liveComplexity = liveFeatures ? calculateComplexity(liveFeatures) : 0;

  return (
    <section id="playground" className={styles.section}>
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLabel}>Interactive Demo</span>
          <h2 className={styles.sectionTitle}>Router Playground</h2>
          <p className={styles.sectionDesc}>
            Type any prompt and watch the routing engine analyze features, score models, and select the optimal LLM in real time.
          </p>
        </div>

        {/* Demo Query Chips */}
        <div className={styles.demoRow}>
          {DEMO_QUERIES.map((d, i) => (
            <button
              key={i}
              className={styles.demoChip}
              onClick={() => loadDemo(d)}
              data-category={d.category}
            >
              {d.label}
            </button>
          ))}
        </div>

        <div className={styles.playgroundGrid}>
          {/* Input Column */}
          <div className={styles.inputCol}>
            <div className={styles.inputCard}>
              <div className={styles.inputHeader}>
                <span className={styles.inputHeaderIcon}>📨</span>
                <span>Request Payload</span>
              </div>

              <textarea
                className={styles.textarea}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter a prompt to route… e.g. 'Write a Python function to merge sort a linked list'"
                rows={5}
              />

              <div className={styles.controls}>
                <div className={styles.tierSelect}>
                  <label className={styles.controlLabel}>User Tier</label>
                  <div className={styles.tierBtns}>
                    {TIERS.map((t) => (
                      <button
                        key={t}
                        className={`${styles.tierBtn} ${
                          tier === t ? styles.tierBtnActive : ""
                        }`}
                        onClick={() => setTier(t)}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>

                <div className={styles.toggleRow}>
                  <label className={styles.controlLabel}>Routing Mode</label>
                  <button
                    className={`${styles.modeToggle} ${
                      useAdvanced ? styles.modeToggleActive : ""
                    }`}
                    onClick={() => setUseAdvanced(!useAdvanced)}
                  >
                    <span className={styles.modeLabel}>
                      {useAdvanced ? "Phase 7 — Multi-Factor" : "Phase 3 — Rule-Based"}
                    </span>
                    <span className={styles.modeIndicator} />
                  </button>
                </div>
              </div>

              <button
                className={styles.routeBtn}
                onClick={() => runRouting()}
                disabled={!query.trim() || isRouting}
              >
                {isRouting ? (
                  <span className={styles.routingText}>
                    <span className={styles.spinner} />
                    {ROUTING_STEPS[routingStep]}
                  </span>
                ) : (
                  <>
                    Route Request
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                  </>
                )}
              </button>
            </div>

            {/* Live Feature Preview */}
            {liveFeatures && (
              <div className={styles.livePreview}>
                <div className={styles.liveHeader}>
                  <span className={styles.liveDot} />
                  Live Feature Extraction
                </div>
                <div className={styles.featureGrid}>
                  <div className={styles.featureItem}>
                    <span className={styles.featureLabel}>Tokens</span>
                    <span className={styles.featureValue}>{liveFeatures.token_count}</span>
                  </div>
                  <div className={styles.featureItem}>
                    <span className={styles.featureLabel}>Words</span>
                    <span className={styles.featureValue}>{liveFeatures.word_count}</span>
                  </div>
                  <div className={styles.featureItem}>
                    <span className={styles.featureLabel}>Complexity</span>
                    <span className={styles.featureValue}>
                      {(liveComplexity * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className={styles.featureItem}>
                    <span className={styles.featureLabel}>Coding</span>
                    <span
                      className={`${styles.featureFlag} ${
                        liveFeatures.is_coding ? styles.flagOn : ""
                      }`}
                    >
                      {liveFeatures.is_coding ? "YES" : "NO"}
                    </span>
                  </div>
                  <div className={styles.featureItem}>
                    <span className={styles.featureLabel}>Analytical</span>
                    <span
                      className={`${styles.featureFlag} ${
                        liveFeatures.is_analytical ? styles.flagOn : ""
                      }`}
                    >
                      {liveFeatures.is_analytical ? "YES" : "NO"}
                    </span>
                  </div>
                  <div className={styles.featureItem}>
                    <span className={styles.featureLabel}>Creative</span>
                    <span
                      className={`${styles.featureFlag} ${
                        liveFeatures.is_creative ? styles.flagOn : ""
                      }`}
                    >
                      {liveFeatures.is_creative ? "YES" : "NO"}
                    </span>
                  </div>
                </div>
                <div className={styles.complexityBar}>
                  <div
                    className={styles.complexityFill}
                    style={{ width: `${liveComplexity * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Results Column */}
          <div className={styles.resultCol} ref={resultRef}>
            {result ? (
              <>
                {/* Selected Model */}
                <div
                  className={styles.resultCard}
                  style={{
                    "--model-color": result.modelConfig.color,
                  }}
                >
                  <div className={styles.resultHeader}>
                    <span className={styles.resultIcon}>
                      {result.modelConfig.icon}
                    </span>
                    <div>
                      <div className={styles.resultModel}>
                        {result.decision.selected}
                      </div>
                      <div className={styles.resultProvider}>
                        {result.modelConfig.provider} ·{" "}
                        {result.modelConfig.quality_tier} tier
                      </div>
                    </div>
                    <div className={styles.confidenceBadge}>
                      {(result.decision.confidence * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className={styles.resultReason}>
                    <span className={styles.reasonLabel}>Routing Reason</span>
                    <code className={styles.reasonCode}>
                      {result.decision.reason}
                    </code>
                  </div>

                  <div className={styles.resultMetrics}>
                    <div className={styles.metricItem}>
                      <span className={styles.metricLabel}>Latency</span>
                      <span className={styles.metricValue}>
                        {result.estimatedLatency}ms
                      </span>
                    </div>
                    <div className={styles.metricItem}>
                      <span className={styles.metricLabel}>Cost</span>
                      <span className={styles.metricValue}>
                        ${result.estimatedCost.toFixed(4)}
                      </span>
                    </div>
                    <div className={styles.metricItem}>
                      <span className={styles.metricLabel}>Tokens</span>
                      <span className={styles.metricValue}>
                        {result.tokensUsed}
                      </span>
                    </div>
                    <div className={styles.metricItem}>
                      <span className={styles.metricLabel}>Method</span>
                      <span className={styles.metricValue}>
                        {result.decision.method === "optimized"
                          ? "Multi-Factor"
                          : "Rule-Based"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Feature Breakdown */}
                <div className={styles.breakdownCard}>
                  <h4 className={styles.breakdownTitle}>Feature Breakdown</h4>
                  <div className={styles.breakdownGrid}>
                    {Object.entries(result.features).map(([key, val]) => (
                      <div key={key} className={styles.breakdownItem}>
                        <span className={styles.breakdownKey}>
                          {key.replace(/_/g, " ")}
                        </span>
                        <span className={styles.breakdownVal}>
                          {typeof val === "boolean" ? (
                            <span
                              className={
                                val
                                  ? styles.boolTrue
                                  : styles.boolFalse
                              }
                            >
                              {val ? "true" : "false"}
                            </span>
                          ) : (
                            val
                          )}
                        </span>
                      </div>
                    ))}
                    <div className={styles.breakdownItem}>
                      <span className={styles.breakdownKey}>
                        complexity score
                      </span>
                      <span className={styles.breakdownVal}>
                        {result.complexity.toFixed(3)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Candidate Scores (Advanced Mode) */}
                {result.decision.candidates && (
                  <div className={styles.candidatesCard}>
                    <h4 className={styles.breakdownTitle}>
                      Model Scores (Weighted)
                    </h4>
                    {result.decision.candidates.map((c, i) => (
                      <div
                        key={c.model}
                        className={`${styles.candidateRow} ${
                          i === 0 ? styles.candidateWinner : ""
                        }`}
                      >
                        <div className={styles.candidateInfo}>
                          <span className={styles.candidateIcon}>
                            {MODEL_CONFIGS[c.model].icon}
                          </span>
                          <span className={styles.candidateName}>
                            {c.model}
                          </span>
                          {i === 0 && (
                            <span className={styles.winnerBadge}>SELECTED</span>
                          )}
                        </div>
                        <div className={styles.scoreBar}>
                          <div
                            className={styles.scoreFill}
                            style={{
                              width: `${c.overall_score * 100}%`,
                              background: MODEL_CONFIGS[c.model].color,
                            }}
                          />
                        </div>
                        <span className={styles.scoreValue}>
                          {(c.overall_score * 100).toFixed(1)}
                        </span>
                        <div className={styles.scoreBreakdown}>
                          <span title="Quality">Q:{(c.quality_score * 100).toFixed(0)}</span>
                          <span title="Cost">C:{(c.cost_score * 100).toFixed(0)}</span>
                          <span title="Latency">L:{(c.latency_score * 100).toFixed(0)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>🧪</div>
                <h3 className={styles.emptyTitle}>
                  Run a routing request
                </h3>
                <p className={styles.emptyDesc}>
                  Type a prompt or select a demo query to see the routing engine in action.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
