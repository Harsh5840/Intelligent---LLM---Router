/* ═══════════════════════════════════════════════════════════════════════
   Simulated Routing Engine — mirrors the Python backend logic exactly
   ═══════════════════════════════════════════════════════════════════════ */

const CODING_KEYWORDS = new Set([
  "code", "function", "class", "debug", "error", "api", "implementation",
  "algorithm", "python", "javascript", "java", "sql", "bug", "syntax",
  "variable", "loop", "array", "object", "import", "package",
]);

const ANALYTICAL_KEYWORDS = new Set([
  "analyze", "compare", "evaluate", "calculate", "explain", "why",
  "data", "statistics", "trend", "pattern", "insight", "metric",
  "performance", "optimization", "breakdown", "impact",
]);

const CREATIVE_KEYWORDS = new Set([
  "write", "story", "create", "imagine", "design", "brainstorm",
  "idea", "creative", "poem", "blog", "article", "narrative",
  "describe", "visualize", "concept",
]);

export const MODEL_CONFIGS = {
  "llama-7b": {
    name: "llama-7b",
    provider: "local",
    cost_per_1k_tokens: 0.0,
    max_tokens: 2048,
    supports_streaming: true,
    avg_latency_ms: 500,
    quality_tier: "medium",
    color: "#34d399",
    icon: "🦙",
    description: "Self-hosted, zero-cost inference for simple queries",
  },
  "gpt-4": {
    name: "gpt-4",
    provider: "openai",
    cost_per_1k_tokens: 0.03,
    max_tokens: 8192,
    supports_streaming: true,
    avg_latency_ms: 1000,
    quality_tier: "high",
    color: "#6366f1",
    icon: "⚡",
    description: "Premium quality for complex coding and enterprise tier",
  },
  "claude-sonnet": {
    name: "claude-sonnet",
    provider: "anthropic",
    cost_per_1k_tokens: 0.015,
    max_tokens: 4096,
    supports_streaming: true,
    avg_latency_ms: 800,
    quality_tier: "high",
    color: "#f59e0b",
    icon: "🧠",
    description: "High-quality reasoning for analytical and creative tasks",
  },
};

function countTokens(text) {
  return Math.round(text.split(/\s+/).filter(Boolean).length * 1.3);
}

function countSentences(text) {
  return text.split(/[.!?]+/).filter((s) => s.trim()).length;
}

function matchKeywords(query, keywords) {
  const lower = query.toLowerCase();
  let count = 0;
  for (const kw of keywords) {
    if (lower.includes(kw)) count++;
  }
  return count;
}

export function extractFeatures(query) {
  const words = query.split(/\s+/).filter(Boolean);
  const token_count = countTokens(query);
  const sentence_count = countSentences(query);
  const has_code_block =
    query.includes("```") ||
    /\b(def |class |function |import )\b/.test(query);
  const is_coding =
    has_code_block ||
    query.includes("```") ||
    query.includes("def ") ||
    query.includes("function ") ||
    matchKeywords(query, CODING_KEYWORDS) >= 2;
  const is_analytical = matchKeywords(query, ANALYTICAL_KEYWORDS) >= 2;
  const is_creative = matchKeywords(query, CREATIVE_KEYWORDS) >= 2;

  return {
    token_count,
    query_length: query.length,
    word_count: words.length,
    sentence_count,
    is_coding,
    is_analytical,
    is_creative,
    has_code_block,
  };
}

export function calculateComplexity(features) {
  let score = 0;
  score += Math.min(features.token_count / 500, 1.0) * 0.3;
  score += Math.min(features.sentence_count / 5, 1.0) * 0.2;
  if (features.is_coding || features.has_code_block) score += 0.3;
  if (features.is_analytical) score += 0.2;
  return Math.min(score, 1.0);
}

/* Multi-factor scoring (identical to router.py Phase 7) */
function qualityScore(config, features) {
  const base = { low: 0.3, medium: 0.6, high: 1.0 }[config.quality_tier];
  const c = calculateComplexity(features);
  return Math.min(c > 0.6 && config.quality_tier === "high" ? base * 1.2 : base, 1.0);
}

function costScore(config, userTier) {
  if (config.cost_per_1k_tokens === 0) return 1.0;
  let s = 1.0 - config.cost_per_1k_tokens / 0.03;
  if (userTier === "enterprise") s = 0.5 + s * 0.5;
  return Math.max(s, 0);
}

function latencyScore(config) {
  return 1.0 - Math.min(config.avg_latency_ms / 2000, 1.0);
}

/* ── Rule-based route (Phase 3) ──────────────────────── */
function routeRuleBased(query, features, userTier) {
  const complexity = calculateComplexity(features);
  let selected, reason, confidence;

  if (complexity < 0.3 && !features.has_code_block) {
    selected = "llama-7b";
    reason = "simple_query";
    confidence = 0.9;
  } else if (features.is_coding && features.has_code_block) {
    selected = ["pro", "enterprise"].includes(userTier) ? "gpt-4" : "claude-sonnet";
    reason = "coding_query_with_code";
    confidence = 0.85;
  } else if (features.is_analytical && features.token_count > 100) {
    selected = "claude-sonnet";
    reason = "analytical_query";
    confidence = 0.8;
  } else if (features.is_creative) {
    selected = "claude-sonnet";
    reason = "creative_query";
    confidence = 0.75;
  } else if (complexity > 0.6) {
    selected = userTier === "enterprise" ? "gpt-4" : "claude-sonnet";
    reason = "high_complexity";
    confidence = 0.8;
  } else {
    selected = "llama-7b";
    reason = "default_fallback";
    confidence = 0.7;
  }

  return { selected, reason, confidence, method: "rule_based" };
}

/* ── Optimized route (Phase 7 multi-factor) ──────────── */
function routeOptimized(query, features, userTier) {
  const candidates = Object.values(MODEL_CONFIGS).map((config) => {
    const qs = qualityScore(config, features);
    const cs = costScore(config, userTier);
    const ls = latencyScore(config);
    const overall = qs * 0.3 + cs * 0.25 + ls * 0.15 + 0.0 * 0.15 + 0.0 * 0.15;
    return {
      model: config.name,
      quality_score: qs,
      cost_score: cs,
      latency_score: ls,
      ml_score: 0,
      rag_score: 0,
      overall_score: overall,
    };
  });

  candidates.sort((a, b) => b.overall_score - a.overall_score);
  const best = candidates[0];

  return {
    selected: best.model,
    reason: "multi_factor_optimization",
    confidence: best.overall_score,
    method: "optimized",
    candidates,
  };
}

/* ── Public API ──────────────────────────────────────── */
export function simulateRouting(query, userTier = "free", useAdvanced = false) {
  const features = extractFeatures(query);
  const complexity = calculateComplexity(features);

  const decision = useAdvanced
    ? routeOptimized(query, features, userTier)
    : routeRuleBased(query, features, userTier);

  const config = MODEL_CONFIGS[decision.selected];
  const tokenCount = features.token_count + (config.quality_tier === "high" ? 100 : 50);
  const estimatedCost = (tokenCount / 1000) * config.cost_per_1k_tokens;
  const simulatedLatency = config.avg_latency_ms + Math.random() * 200 - 100;

  return {
    features,
    complexity,
    decision,
    estimatedCost: Math.round(estimatedCost * 10000) / 10000,
    estimatedLatency: Math.round(simulatedLatency),
    tokensUsed: tokenCount,
    modelConfig: config,
  };
}

/* ── Demo Queries ────────────────────────────────────── */
export const DEMO_QUERIES = [
  {
    text: "Write a Python function to reverse a linked list and explain time complexity.",
    tier: "pro",
    label: "Coding (Pro)",
    category: "coding",
  },
  {
    text: "Compare Redis and PostgreSQL caching strategies with pros and cons for read-heavy systems.",
    tier: "free",
    label: "Analytical (Free)",
    category: "analytical",
  },
  {
    text: "Write a creative blog post about the future of AI assistants and brainstorm some article ideas.",
    tier: "free",
    label: "Creative (Free)",
    category: "creative",
  },
  {
    text: "Hello, how are you?",
    tier: "free",
    label: "Simple Chat (Free)",
    category: "simple",
  },
  {
    text: "```python\ndef merge_sort(arr):\n    pass\n```\nComplete this implementation with an efficient algorithm and add error handling.",
    tier: "enterprise",
    label: "Code Block (Enterprise)",
    category: "coding",
  },
  {
    text: "Analyze the performance breakdown and evaluate the optimization impact. Calculate the data trend patterns.",
    tier: "pro",
    label: "Deep Analysis (Pro)",
    category: "analytical",
  },
];
