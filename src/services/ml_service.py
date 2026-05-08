"""
Phase 5 runtime service for ML-enhanced routing decisions.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import torch
    from transformers import BertTokenizer, BertForSequenceClassification

    TORCH_TRANSFORMERS_AVAILABLE = True
except ImportError:
    torch = None
    BertTokenizer = None
    BertForSequenceClassification = None
    TORCH_TRANSFORMERS_AVAILABLE = False


class MLRoutingService:
    """
    Runtime service that loads trained classifiers and converts predictions
    into per-model routing affinity scores.
    """

    def __init__(self):
        self.tokenizer: Optional[Any] = None
        self.complexity_model: Optional[Any] = None
        self.domain_model: Optional[Any] = None
        self.initialized = False

        if not TORCH_TRANSFORMERS_AVAILABLE:
            logger.warning("ml_runtime_dependencies_missing")
            return

        self._load_models()

    def _resolve_model_path(self, path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute():
            return path
        return Path.cwd() / path

    def _load_models(self) -> None:
        complexity_path = self._resolve_model_path(settings.ml_complexity_model_path)
        domain_path = self._resolve_model_path(settings.ml_domain_model_path)

        if not complexity_path.exists() or not domain_path.exists():
            logger.warning(
                "ml_model_paths_not_found",
                complexity_path=str(complexity_path),
                domain_path=str(domain_path),
            )
            return

        try:
            if BertTokenizer is None or BertForSequenceClassification is None:
                logger.warning("ml_runtime_dependencies_unavailable")
                return

            self.tokenizer = BertTokenizer.from_pretrained(str(complexity_path))
            self.complexity_model = BertForSequenceClassification.from_pretrained(
                str(complexity_path)
            )
            self.domain_model = BertForSequenceClassification.from_pretrained(str(domain_path))

            self.complexity_model.eval()
            self.domain_model.eval()
            self.initialized = True

            logger.info(
                "ml_runtime_initialized",
                complexity_path=str(complexity_path),
                domain_path=str(domain_path),
            )
        except Exception as exc:
            logger.error("ml_runtime_init_failed", error=str(exc))
            self.initialized = False

    async def predict(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Predict complexity and domain labels with confidence.

        Returns None when runtime ML model is unavailable.
        """
        if not self.initialized or self.tokenizer is None:
            return self._heuristic_predict(query)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._predict_sync, query)

    def _heuristic_predict(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        words = [word for word in query_lower.split() if word]
        token_estimate = int(len(words) * 1.3)

        code_markers = ["```", "def ", "class ", "function ", "import ", "sql", "python"]
        analysis_markers = ["analyze", "compare", "evaluate", "trend", "performance"]
        creative_markers = ["story", "creative", "brainstorm", "poem", "blog"]

        code_hits = sum(marker in query_lower for marker in code_markers)
        analysis_hits = sum(marker in query_lower for marker in analysis_markers)
        creative_hits = sum(marker in query_lower for marker in creative_markers)

        if code_hits >= 2:
            domain = "code"
        elif analysis_hits >= 2:
            domain = "analysis"
        elif creative_hits >= 2:
            domain = "creative"
        else:
            domain = "chat"

        if token_estimate > 180 or code_hits >= 2 or analysis_hits >= 3:
            complexity = "complex"
            confidence = 0.75
        elif token_estimate > 80 or analysis_hits >= 1 or creative_hits >= 2:
            complexity = "medium"
            confidence = 0.7
        else:
            complexity = "simple"
            confidence = 0.75

        return {
            "complexity": complexity,
            "complexity_confidence": confidence,
            "domain": domain,
            "domain_confidence": 0.7,
        }

    def _predict_sync(self, query: str) -> Optional[Dict[str, Any]]:
        if (
            self.tokenizer is None
            or self.complexity_model is None
            or self.domain_model is None
            or torch is None
        ):
            return None

        encoding = self.tokenizer(
            query,
            max_length=128,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        with torch.no_grad():
            complexity_out = self.complexity_model(**encoding)
            complexity_probs = torch.softmax(complexity_out.logits, dim=1)[0]
            complexity_idx = int(torch.argmax(complexity_probs).item())
            complexity_conf = float(complexity_probs[complexity_idx].item())

            domain_out = self.domain_model(**encoding)
            domain_probs = torch.softmax(domain_out.logits, dim=1)[0]
            domain_idx = int(torch.argmax(domain_probs).item())
            domain_conf = float(domain_probs[domain_idx].item())

        complexity_labels = {0: "simple", 1: "medium", 2: "complex"}
        domain_labels = {0: "code", 1: "analysis", 2: "creative", 3: "chat"}

        return {
            "complexity": complexity_labels.get(complexity_idx, "medium"),
            "complexity_confidence": complexity_conf,
            "domain": domain_labels.get(domain_idx, "chat"),
            "domain_confidence": domain_conf,
        }

    async def score_model(self, query: str, model_name: str) -> float:
        """
        Return model affinity score in [0,1] from ML predictions.
        """
        prediction = await self.predict(query)
        if not prediction:
            return 0.0

        complexity = prediction["complexity"]
        domain = prediction["domain"]
        confidence = max(0.0, min(prediction["complexity_confidence"], 1.0))

        complexity_scores = {
            "simple": {"llama-7b": 1.0, "claude-sonnet": 0.6, "gpt-4": 0.4},
            "medium": {"llama-7b": 0.6, "claude-sonnet": 0.9, "gpt-4": 0.8},
            "complex": {"llama-7b": 0.3, "claude-sonnet": 0.85, "gpt-4": 1.0},
        }

        domain_boost = {
            "code": {"gpt-4": 0.1, "claude-sonnet": 0.05},
            "analysis": {"claude-sonnet": 0.08, "gpt-4": 0.05},
            "creative": {"claude-sonnet": 0.1},
            "chat": {"llama-7b": 0.1},
        }

        base_score = complexity_scores.get(complexity, complexity_scores["medium"]).get(
            model_name,
            0.5,
        )
        boost = domain_boost.get(domain, {}).get(model_name, 0.0)
        final_score = min(max((base_score + boost) * confidence, 0.0), 1.0)

        logger.debug(
            "ml_model_score",
            model=model_name,
            complexity=complexity,
            domain=domain,
            confidence=confidence,
            score=final_score,
        )

        return final_score
