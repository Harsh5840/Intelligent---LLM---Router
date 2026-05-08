"use client";
import { useState, useEffect, useRef } from "react";
import styles from "./Metrics.module.css";

/* Simulated live metrics that animate */
function useAnimatedValue(target, duration = 2000) {
  const [value, setValue] = useState(0);
  const frameRef = useRef();

  useEffect(() => {
    const start = performance.now();
    const from = 0;
    const animate = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(from + (target - from) * eased);
      if (progress < 1) frameRef.current = requestAnimationFrame(animate);
    };
    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [target, duration]);

  return value;
}

const ENDPOINTS = [
  {
    method: "POST",
    path: "/api/v1/chat",
    desc: "Main router — routes query to optimal LLM",
    color: "var(--accent-indigo)",
  },
  {
    method: "POST",
    path: "/api/v1/feedback",
    desc: "Submit ratings for closed-loop improvement",
    color: "var(--accent-violet)",
  },
  {
    method: "GET",
    path: "/api/v1/health",
    desc: "Service status and model availability",
    color: "var(--accent-emerald)",
  },
  {
    method: "GET",
    path: "/api/v1/metrics",
    desc: "Prometheus metrics in text format",
    color: "var(--accent-cyan)",
  },
  {
    method: "GET",
    path: "/api/v1/stats",
    desc: "Aggregated stats and model distribution",
    color: "var(--accent-amber)",
  },
  {
    method: "GET",
    path: "/api/v1/models",
    desc: "List all models with configs and health",
    color: "var(--accent-rose)",
  },
];

const INFRA_STACK = [
  {
    name: "FastAPI + Uvicorn",
    role: "ASGI Web Framework",
    detail: "Async request handling, Pydantic v2 validation, auto OpenAPI docs",
    icon: "⚡",
  },
  {
    name: "PostgreSQL 15",
    role: "Primary Database",
    detail: "SQLAlchemy 2 + asyncpg. Stores routing decisions, feedback, and training data",
    icon: "🗄️",
  },
  {
    name: "Redis 7",
    role: "Response Cache",
    detail: "Semantic cache with hiredis parser. Checks before routing, caches after inference",
    icon: "💾",
  },
  {
    name: "Prometheus",
    role: "Metrics Collector",
    detail: "Request counts, latency histograms, error counters per model",
    icon: "📊",
  },
  {
    name: "Nginx",
    role: "Reverse Proxy",
    detail: "Rate limiting, SSL termination, load balancing",
    icon: "🔒",
  },
  {
    name: "Docker + K8s",
    role: "Deployment",
    detail: "Containerized with health checks, Kubernetes manifests for horizontal scale",
    icon: "🐳",
  },
];

export default function Metrics() {
  const reqCount = useAnimatedValue(14827, 2500);
  const cacheRate = useAnimatedValue(34.2, 2000);
  const avgLatency = useAnimatedValue(642, 2200);
  const errorRate = useAnimatedValue(0.12, 1800);
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setVisible(true);
      },
      { threshold: 0.2 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  return (
    <section id="metrics" className={styles.section} ref={ref}>
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLabel}>Observability</span>
          <h2 className={styles.sectionTitle}>Metrics & Infrastructure</h2>
          <p className={styles.sectionDesc}>
            Full traceability of routing decisions, health-aware monitoring, and production-grade deployment.
          </p>
        </div>

        {/* KPI Cards */}
        <div className={styles.kpiGrid}>
          {[
            {
              label: "Total Requests",
              value: Math.round(reqCount).toLocaleString(),
              sub: "simulated demo data",
              color: "var(--accent-indigo)",
            },
            {
              label: "Cache Hit Rate",
              value: `${cacheRate.toFixed(1)}%`,
              sub: "Redis semantic cache",
              color: "var(--accent-emerald)",
            },
            {
              label: "Avg Latency",
              value: `${Math.round(avgLatency)}ms`,
              sub: "end-to-end p50",
              color: "var(--accent-cyan)",
            },
            {
              label: "Error Rate",
              value: `${errorRate.toFixed(2)}%`,
              sub: "circuit breaker threshold: 5",
              color: "var(--accent-rose)",
            },
          ].map((kpi) => (
            <div key={kpi.label} className={styles.kpiCard}>
              <span className={styles.kpiLabel}>{kpi.label}</span>
              <span className={styles.kpiValue} style={{ color: kpi.color }}>
                {visible ? kpi.value : "—"}
              </span>
              <span className={styles.kpiSub}>{kpi.sub}</span>
            </div>
          ))}
        </div>

        {/* Simulated Model Distribution */}
        <div className={styles.distCard}>
          <h3 className={styles.cardTitle}>Model Distribution</h3>
          <div className={styles.distBars}>
            {[
              { model: "llama-7b", pct: 48, color: "#34d399", icon: "🦙" },
              { model: "claude-sonnet", pct: 35, color: "#f59e0b", icon: "🧠" },
              { model: "gpt-4", pct: 17, color: "#6366f1", icon: "⚡" },
            ].map((d) => (
              <div key={d.model} className={styles.distRow}>
                <div className={styles.distInfo}>
                  <span className={styles.distIcon}>{d.icon}</span>
                  <span className={styles.distModel}>{d.model}</span>
                  <span className={styles.distPct}>{d.pct}%</span>
                </div>
                <div className={styles.distBar}>
                  <div
                    className={styles.distFill}
                    style={{
                      width: visible ? `${d.pct}%` : "0%",
                      background: d.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* API Endpoints */}
        <div className={styles.endpointsCard}>
          <h3 className={styles.cardTitle}>API Surface</h3>
          <div className={styles.endpointList}>
            {ENDPOINTS.map((ep) => (
              <div key={ep.path} className={styles.endpoint}>
                <span
                  className={styles.method}
                  style={{ color: ep.color }}
                >
                  {ep.method}
                </span>
                <code className={styles.path}>{ep.path}</code>
                <span className={styles.epDesc}>{ep.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Infrastructure Stack */}
        <div className={styles.infraGrid}>
          {INFRA_STACK.map((item) => (
            <div key={item.name} className={styles.infraCard}>
              <span className={styles.infraIcon}>{item.icon}</span>
              <div>
                <h4 className={styles.infraName}>{item.name}</h4>
                <span className={styles.infraRole}>{item.role}</span>
                <p className={styles.infraDetail}>{item.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
