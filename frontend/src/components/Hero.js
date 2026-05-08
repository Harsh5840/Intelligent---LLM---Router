"use client";
import { useEffect, useRef } from "react";
import styles from "./Hero.module.css";

const TECH_STACK = [
  "FastAPI", "Python 3.11", "Pydantic v2", "PostgreSQL",
  "Redis", "Prometheus", "Docker", "Nginx", "Kubernetes",
];

export default function Hero() {
  const orbRef = useRef(null);

  useEffect(() => {
    let frame;
    let t = 0;
    const animate = () => {
      t += 0.003;
      if (orbRef.current) {
        orbRef.current.style.transform = `translate(${Math.sin(t) * 30}px, ${
          Math.cos(t * 0.7) * 20
        }px)`;
      }
      frame = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <section className={styles.hero}>
      {/* Background Effects */}
      <div className={styles.bgGrid} />
      <div className={styles.bgGlow} ref={orbRef} />
      <div className={styles.bgGlow2} />

      <div className={styles.content}>
        <div className={styles.badge}>
          <span className={styles.badgeDot} />
          Production-Grade System Design Project
        </div>

        <h1 className={styles.title}>
          <span className={styles.titleLine}>Intelligent</span>
          <span className={styles.titleGradient}>LLM Router</span>
        </h1>

        <p className={styles.subtitle}>
          A decision layer that sits in front of <strong>multiple foundation models</strong>{" "}
          and dynamically chooses the best model per request — optimizing{" "}
          <span className={styles.highlight}>quality</span>,{" "}
          <span className={styles.highlightCyan}>latency</span>, and{" "}
          <span className={styles.highlightAmber}>cost</span>{" "}
          in real time.
        </p>

        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statValue}>5</span>
            <span className={styles.statLabel}>API Endpoints</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <span className={styles.statValue}>3</span>
            <span className={styles.statLabel}>Model Providers</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <span className={styles.statValue}>9</span>
            <span className={styles.statLabel}>Architecture Phases</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <span className={styles.statValue}>7</span>
            <span className={styles.statLabel}>Routing Factors</span>
          </div>
        </div>

        <div className={styles.actions}>
          <a href="#playground" className={styles.primaryBtn}>
            Try the Router
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
          <a href="#architecture" className={styles.secondaryBtn}>
            View Architecture
          </a>
        </div>

        <div className={styles.techRow}>
          {TECH_STACK.map((tech) => (
            <span key={tech} className={styles.techPill}>{tech}</span>
          ))}
        </div>
      </div>
    </section>
  );
}
