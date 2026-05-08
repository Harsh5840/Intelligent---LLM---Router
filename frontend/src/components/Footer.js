"use client";
import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.topRow}>
          <div className={styles.brand}>
            <span className={styles.logo}>⚡ LLM Router</span>
            <p className={styles.tagline}>
              Production-style intelligent routing layer for LLM applications —
              optimizing quality, latency, reliability, and cost at scale.
            </p>
          </div>

          <div className={styles.linksGroup}>
            <h4 className={styles.linksTitle}>Quick Links</h4>
            <a href="#architecture">Architecture</a>
            <a href="#playground">Playground</a>
            <a href="#models">Models</a>
            <a href="#metrics">Metrics</a>
          </div>

          <div className={styles.linksGroup}>
            <h4 className={styles.linksTitle}>Tech Stack</h4>
            <span>FastAPI + Python 3.11</span>
            <span>PostgreSQL + Redis</span>
            <span>Docker + Kubernetes</span>
            <span>Prometheus + structlog</span>
          </div>

          <div className={styles.linksGroup}>
            <h4 className={styles.linksTitle}>Signals</h4>
            <span>System Thinking</span>
            <span>Design Maturity</span>
            <span>Execution Depth</span>
            <span>Production Mindset</span>
          </div>
        </div>

        <div className={styles.divider} />

        <div className={styles.bottomRow}>
          <span className={styles.copy}>
            Built as a system design demonstration project
          </span>
          <a
            href="https://github.com/Harsh5840/Intelligent---LLM---Router"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.ghLink}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
            View Source on GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
