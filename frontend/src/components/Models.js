"use client";
import { MODEL_CONFIGS } from "@/lib/router-engine";
import styles from "./Models.module.css";

const QUALITY_MAP = {
  low: { label: "Low", color: "var(--text-muted)" },
  medium: { label: "Medium", color: "var(--accent-amber)" },
  high: { label: "High", color: "var(--accent-emerald)" },
};

export default function Models() {
  const models = Object.values(MODEL_CONFIGS);

  return (
    <section id="models" className={styles.section}>
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLabel}>Model Registry</span>
          <h2 className={styles.sectionTitle}>Provider Abstraction</h2>
          <p className={styles.sectionDesc}>
            Models are resolved through a central registry. New providers plug in without changing API contracts.
          </p>
        </div>

        <div className={styles.modelGrid}>
          {models.map((model) => {
            const quality = QUALITY_MAP[model.quality_tier];
            return (
              <div
                key={model.name}
                className={styles.modelCard}
                style={{ "--model-color": model.color }}
              >
                <div className={styles.cardGlow} />

                <div className={styles.cardHeader}>
                  <span className={styles.modelIcon}>{model.icon}</span>
                  <div>
                    <h3 className={styles.modelName}>{model.name}</h3>
                    <span className={styles.modelProvider}>
                      {model.provider}
                    </span>
                  </div>
                  <span
                    className={styles.qualityBadge}
                    style={{ color: quality.color }}
                  >
                    {quality.label}
                  </span>
                </div>

                <p className={styles.modelDesc}>{model.description}</p>

                <div className={styles.specGrid}>
                  <div className={styles.specItem}>
                    <span className={styles.specLabel}>Cost / 1k tokens</span>
                    <span className={styles.specValue}>
                      {model.cost_per_1k_tokens === 0
                        ? "Free"
                        : `$${model.cost_per_1k_tokens}`}
                    </span>
                  </div>
                  <div className={styles.specItem}>
                    <span className={styles.specLabel}>Avg Latency</span>
                    <span className={styles.specValue}>
                      {model.avg_latency_ms}ms
                    </span>
                  </div>
                  <div className={styles.specItem}>
                    <span className={styles.specLabel}>Max Tokens</span>
                    <span className={styles.specValue}>
                      {model.max_tokens.toLocaleString()}
                    </span>
                  </div>
                  <div className={styles.specItem}>
                    <span className={styles.specLabel}>Streaming</span>
                    <span className={styles.specValue}>
                      {model.supports_streaming ? "Yes" : "No"}
                    </span>
                  </div>
                </div>

                {/* Cost vs Quality visual */}
                <div className={styles.barRow}>
                  <div className={styles.barGroup}>
                    <span className={styles.barLabel}>Quality</span>
                    <div className={styles.bar}>
                      <div
                        className={styles.barFill}
                        style={{
                          width:
                            model.quality_tier === "high"
                              ? "100%"
                              : model.quality_tier === "medium"
                              ? "60%"
                              : "30%",
                          background: model.color,
                        }}
                      />
                    </div>
                  </div>
                  <div className={styles.barGroup}>
                    <span className={styles.barLabel}>Cost Efficiency</span>
                    <div className={styles.bar}>
                      <div
                        className={styles.barFill}
                        style={{
                          width:
                            model.cost_per_1k_tokens === 0
                              ? "100%"
                              : model.cost_per_1k_tokens < 0.02
                              ? "60%"
                              : "30%",
                          background: "var(--accent-emerald)",
                        }}
                      />
                    </div>
                  </div>
                  <div className={styles.barGroup}>
                    <span className={styles.barLabel}>Speed</span>
                    <div className={styles.bar}>
                      <div
                        className={styles.barFill}
                        style={{
                          width:
                            model.avg_latency_ms <= 500
                              ? "100%"
                              : model.avg_latency_ms <= 800
                              ? "65%"
                              : "40%",
                          background: "var(--accent-cyan)",
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Routing Weights Breakdown */}
        <div className={styles.weightsCard}>
          <h3 className={styles.weightsTitle}>Multi-Factor Scoring Weights</h3>
          <p className={styles.weightsDesc}>
            Phase 7 decision engine uses weighted scoring to rank candidate models:
          </p>
          <div className={styles.weightsGrid}>
            {[
              { label: "Quality", weight: 0.3, color: "var(--accent-violet)" },
              { label: "Cost", weight: 0.25, color: "var(--accent-emerald)" },
              { label: "Latency", weight: 0.15, color: "var(--accent-cyan)" },
              { label: "ML Score", weight: 0.15, color: "var(--accent-rose)", flag: "ENABLE_ML_ROUTING" },
              { label: "RAG Score", weight: 0.15, color: "var(--accent-amber)", flag: "ENABLE_RAG_ROUTING" },
            ].map((w) => (
              <div key={w.label} className={styles.weightItem}>
                <div className={styles.weightHeader}>
                  <span className={styles.weightLabel}>{w.label}</span>
                  <span
                    className={styles.weightValue}
                    style={{ color: w.color }}
                  >
                    {(w.weight * 100).toFixed(0)}%
                  </span>
                </div>
                <div className={styles.weightBar}>
                  <div
                    className={styles.weightFill}
                    style={{
                      width: `${w.weight * 100 * 3.33}%`,
                      background: w.color,
                    }}
                  />
                </div>
                {w.flag && (
                  <span className={styles.flagLabel}>
                    Feature flag: {w.flag}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
