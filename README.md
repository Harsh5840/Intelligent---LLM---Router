# Intelligent LLM Router — FAANG-Level Recruiter + System Design Pitch

## 30-second executive pitch

I built an **Intelligent LLM Router**, a production-style decision layer that sits in front of multiple foundation models and chooses the best model per request. Instead of hardcoding one LLM, the router makes a real-time tradeoff between **quality, latency, and cost** using request features, model health, and policy constraints. The result is a system that improves unit economics while keeping response quality stable.

## 2-minute recruiter pitch (what I would say)

This project solves a common enterprise AI problem: teams either default to a single expensive model or manually switch models with brittle rules. I designed a centralized routing service that exposes one API to clients and dynamically dispatches requests to the right model.

From a system design perspective, I separated it into clear layers:
- **API layer** for request validation and response contracts.
- **Feature extraction layer** to convert prompts into routing signals.
- **Routing engine** that scores candidate models with business-aware policy.
- **Model client layer** for provider-specific integrations behind a uniform interface.
- **Caching + observability** to control cost and measure decision quality.

The architecture is optimized for extensibility and operational maturity. New providers can be added through the registry/client abstraction without changing API contracts. Routing logic is isolated, testable, and can evolve from rules to learned policies over time. I also built in metrics and logging so routing decisions are explainable and auditable.

The key impact is that this creates a **platform primitive** for any LLM application: product teams integrate once, then get continuous routing improvements in latency, quality, and spend without rewriting application code.

## System design details (FAANG-style depth)

### 1) Functional requirements
- Accept prompt requests through a single API.
- Select an optimal model per request based on complexity and constraints.
- Return model output with predictable latency and robust error handling.
- Support multiple providers and easy onboarding of new models.

### 2) Non-functional requirements
- **Low latency:** fast pre-processing and bounded routing overhead.
- **High availability:** graceful fallback if a model/provider degrades.
- **Cost efficiency:** route simple requests to cheaper models when possible.
- **Observability:** full traceability of routing decisions and outcomes.
- **Extensibility:** pluggable model registry and policy-driven routing.

### 3) High-level architecture
1. Client sends request to API.
2. API validates schema and normalizes payload.
3. Feature extractor computes complexity and context signals.
4. Router scores available models using policy + health + historical priors.
5. Selected model client executes inference.
6. Post-processing logs metrics, caches eligible responses, and returns output.

### 4) Core design decisions and tradeoffs
- **Centralized router vs app-level logic:** chose centralized router for governance and consistency.
- **Heuristic scoring first:** faster to production and easier to debug than immediate ML-only routing.
- **Provider abstraction:** avoids vendor lock-in and reduces integration churn.
- **Cache at response layer:** improves p95 latency and reduces repeated token costs.

### 5) Reliability strategy
- Timeouts and retry boundaries at model-client layer.
- Fallback model chain when preferred provider fails or violates SLO.
- Health-aware routing to avoid degraded backends.
- Idempotent request handling patterns for safe retries.

### 6) Scalability strategy
- Stateless API/router services for horizontal scale.
- Cache to reduce downstream inference pressure.
- Model registry abstraction to support dynamic capacity changes.
- Metrics-driven tuning of routing thresholds as traffic patterns evolve.

### 7) Observability and operational excellence
- Structured logging for request lifecycle and routing rationale.
- Metrics for latency, success rate, model utilization, and cost proxies.
- Endpoint and router tests to prevent regression in selection behavior.
- Deployment-ready artifacts (containerized setup and environment-driven config).

## Concrete tech details (what I actually implemented)

### Backend and API framework
- **Language/runtime:** Python 3.11.
- **Web framework:** FastAPI (`fastapi==0.109.0`) + Uvicorn (`uvicorn[standard]==0.27.0`).
- **Schema/validation:** Pydantic v2 (`pydantic==2.5.3`, `pydantic-settings==2.1.0`).
- **API surface:** `POST /api/v1/chat`, `POST /api/v1/feedback`, `GET /api/v1/health`, `GET /api/v1/metrics`, `GET /api/v1/stats`.
- **App lifecycle:** startup initializes data tables and verifies dependencies in production mode.

### Routing engine internals
- **Primary routing path:** `feature_extractor -> router -> model_registry -> model_client.generate()`.
- **Rule-based logic:** routes by complexity, coding/analytical/creative intent, code-block presence, token count, and user tier.
- **Advanced scoring mode:** weighted multi-factor score:
	- quality: `0.30`
	- cost: `0.25`
	- latency: `0.15`
	- ML score: `0.15` (feature-flag controlled)
	- RAG score: `0.15` (feature-flag controlled)
- **Fallback behavior:** if selected model is unavailable, router shifts to configured fallback model.

### Model orchestration and provider abstraction
- **Registry pattern:** model clients are resolved through a central registry, keeping provider specifics out of endpoint code.
- **Current routing targets in logic:** `llama-7b`, `claude-sonnet`, `gpt-4` with tier-aware behavior.
- **Cost-aware policy:** cheap/default model for low-complexity traffic, premium models for complex/coding-heavy requests.

### Data, storage, and feedback loop
- **Database stack:** SQLAlchemy 2 + Alembic + asyncpg / psycopg2-binary.
- **Decision logging:** each request can persist routing metadata, latency, estimated cost, and success outcome.
- **Human feedback path:** `POST /feedback` stores explicit ratings/comments for closed-loop improvement.
- **Vector support:** Pinecone client + embedding pathway available for RAG-assisted routing mode.

### Caching and performance
- **Cache backend:** Redis 5 (+ hiredis parser).
- **Cache strategy:** check cache before routing/model call; cache successful responses after inference.
- **Operational effect:** reduces repeated-token spend and improves tail latency on repeated prompts.

### Reliability and production safeguards
- **Dependency health checks:** startup validation in production for database and redis when caching is enabled.
- **Timeout/retry/circuit-breaker configuration:** env-driven controls (`REQUEST_TIMEOUT`, `MAX_RETRIES`, `CIRCUIT_BREAKER_THRESHOLD`).
- **Error handling:** API-level exception capture with structured error metrics and HTTP-safe responses.
- **Security middleware:** CORS controls and trusted-host middleware in production.

### Observability stack
- **Logging:** `structlog`-based structured logs with event names for each major lifecycle step.
- **Metrics:** Prometheus via `prometheus-client` with request count, latency histograms, and error counters.
- **Debuggability:** routing metadata returns reason/confidence/alternatives for transparent decision tracing.

### Configuration and feature flags
- **12-factor config:** `.env` + typed settings class.
- **Feature gates:** `ENABLE_ML_ROUTING`, `ENABLE_RAG_ROUTING`, `ENABLE_CACHING`.
- **Model defaults:** configurable `DEFAULT_MODEL` and `FALLBACK_MODEL`.

### DevEx, quality, and delivery
- **Testing:** `pytest`, `pytest-asyncio`, `pytest-cov` with focused coverage on router/cache/endpoints.
- **Code quality:** Black (format), Ruff (lint/import rules), MyPy (strict typed defs).
- **Deployment artifacts:** `Dockerfile`, `docker-compose.yml`, `nginx.conf`, and Kubernetes-style `manifests.yaml`.

## Leadership signals this project demonstrates

- **System thinking:** balanced product quality, latency SLOs, and cost constraints.
- **Design maturity:** modular boundaries with clear ownership per layer.
- **Execution depth:** built API, routing, provider integration, cache, and test surfaces end-to-end.
- **Production mindset:** added monitoring, error handling, and extensible policy hooks.
- **Future-proofing:** enabled path from rule-based routing to data-driven routing.

## Interview-ready “system design” answer (3-4 minutes)

If I had to explain the design in an interview, I’d say:

> “I designed the router as a control plane for LLM inference decisions. The key idea is to separate application logic from model-selection logic. Incoming requests are normalized, then converted into features like prompt complexity and context size. The routing engine computes a score per candidate model using weighted policy signals: expected quality, latency budget fit, and cost profile. It then selects the top model that satisfies constraints and calls it through a provider-agnostic client interface.
>
> For reliability, I enforce timeouts and fallback chains so degraded providers don’t impact user experience. For scalability, services are stateless and horizontally scalable, and a caching layer absorbs repeated requests to reduce cost and tail latency. For observability, every routing decision is logged with reason codes and emitted as metrics so we can audit behavior and tune policy thresholds.
>
> This architecture let me ship quickly with deterministic routing rules, while keeping the design open for a learned ranking model later. That tradeoff gave immediate business value and a strong path to continuous optimization.”

## One-line summary for recruiters

“I built a production-style intelligent routing layer for LLM applications that dynamically chooses the best model per request to optimize **quality, latency, reliability, and cost at scale**.”