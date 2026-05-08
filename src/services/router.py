"""
Routing service - decides which model to use for a given query.
Production-grade with circuit breaker, metrics, and observability.
"""

import time
from typing import Optional, List
from src.models.schemas import QueryFeatures, RoutingDecision, ModelCandidate
from src.services.model_registry import model_registry, MODEL_CONFIGS
from src.services.feature_extractor import feature_extractor
from src.services.ml_service import MLRoutingService
from src.services.rag_service import RoutingRAGService
from src.services.circuit_breaker import circuit_breaker_registry
from src.utils.logging import get_logger
from src.utils.metrics import (
    routing_decisions_total,
    routing_overhead_ms,
    fallback_triggers_total,
    circuit_breaker_state,
)
from src.config import settings

logger = get_logger(__name__)


# ============================================================================
# PHASE 3: Rule-Based Router
# ============================================================================


class Router:
    """
    Intelligent router that selects the optimal model for each query
    Evolves from simple rules to ML-based decisions
    """

    def __init__(self):
        self.ml_classifier: Optional[MLRoutingService] = None
        self.rag_service: Optional[RoutingRAGService] = None

        if settings.enable_ml_routing:
            try:
                self.ml_classifier = MLRoutingService()
                if not self.ml_classifier.initialized:
                    logger.warning("ml_routing_using_heuristic_fallback")
            except Exception as e:
                logger.error("ml_routing_init_failed", error=str(e))

        if settings.enable_rag_routing:
            try:
                self.rag_service = RoutingRAGService()
            except Exception as e:
                logger.error("rag_routing_init_failed", error=str(e))

    # ========================================================================
    # PHASE 1: Hardcoded Routing (Initial Implementation)
    # ========================================================================

    async def route_hardcoded(self, query: str, user_id: str) -> RoutingDecision:
        """
        Initial hardcoded routing - always returns default model
        PHASE 1 ONLY - Replaced in Phase 3
        """
        return RoutingDecision(
            model_selected=settings.default_model,
            routing_method="rule_based",
            complexity_tier="low",
            complexity_score=0.0,
            routing_reason="hardcoded_default",
            cost_estimate_usd=0.001,
            fallback_used=False,
            fallback_reason=None,
            candidates_scored=[],
            routing_overhead_ms=0.0,
            # Legacy fields
            selected_model=settings.default_model,
            reason="hardcoded_default",
            confidence=1.0,
            fallback=False,
        )

    # ========================================================================
    # PHASE 3: Rule-Based Routing
    # ========================================================================

    async def route_rule_based(
        self,
        query: str,
        features: QueryFeatures,
        user_tier: str = "free"
    ) -> RoutingDecision:
        """
        Rule-based routing using extracted features
        Simple heuristics for model selection
        """
        start_time = time.time()
        complexity_score = feature_extractor.calculate_complexity_score(features)
        candidates_scored = []

        # Rule 1: Simple queries -> cheap model
        if complexity_score < 0.3 and not features.has_code_block:
            selected = "llama-7b"
            complexity_tier = "low"
            routing_reason = "simple_query"
            cost_estimate = 0.001
            candidates_scored = [
                {"model": "llama-7b", "score": 0.9, "reason": "matches_rule_1"},
                {"model": "claude-sonnet", "score": 0.3, "reason": "too_expensive"},
            ]

        # Rule 2: Coding queries with code blocks -> premium model
        elif features.is_coding and features.has_code_block:
            selected = "gpt-4" if user_tier in ["pro", "enterprise"] else "claude-sonnet"
            complexity_tier = "high"
            routing_reason = "coding_query_with_code"
            cost_estimate = 0.05 if selected == "gpt-4" else 0.02
            candidates_scored = [
                {"model": selected, "score": 0.85, "reason": "matches_rule_2"},
            ]

        # Rule 3: Long analytical queries -> premium model
        elif features.is_analytical and features.token_count > 100:
            selected = "claude-sonnet"
            complexity_tier = "medium"
            routing_reason = "analytical_query"
            cost_estimate = 0.02
            candidates_scored = [
                {"model": "claude-sonnet", "score": 0.8, "reason": "matches_rule_3"},
            ]

        # Rule 4: Creative queries -> medium model
        elif features.is_creative:
            selected = "claude-sonnet"
            complexity_tier = "medium"
            routing_reason = "creative_query"
            cost_estimate = 0.02
            candidates_scored = [
                {"model": "claude-sonnet", "score": 0.75, "reason": "matches_rule_4"},
            ]

        # Rule 5: Complex queries -> premium model
        elif complexity_score > 0.6:
            selected = "gpt-4" if user_tier == "enterprise" else "claude-sonnet"
            complexity_tier = "high"
            routing_reason = "high_complexity"
            cost_estimate = 0.05 if selected == "gpt-4" else 0.02
            candidates_scored = [
                {"model": selected, "score": 0.8, "reason": "matches_rule_5"},
            ]

        # Default: Use cheap model
        else:
            selected = "llama-7b"
            complexity_tier = "low"
            routing_reason = "default_fallback"
            cost_estimate = 0.001
            candidates_scored = [
                {"model": "llama-7b", "score": 0.7, "reason": "default"},
            ]

        # Check circuit breaker
        breaker = circuit_breaker_registry.get_breaker(selected)
        fallback_used = False
        fallback_reason = None

        if not breaker.can_attempt():
            logger.warning(
                "circuit_breaker.blocked_request",
                model=selected,
                state=breaker.get_state(),
            )
            # Try fallback
            selected = settings.fallback_model
            fallback_used = True
            fallback_reason = f"circuit_breaker_open"
            routing_reason = f"fallback_from_{breaker.model_name}"
            cost_estimate = 0.001
            
            fallback_triggers_total.labels(
                primary_model=breaker.model_name,
                fallback_model=selected,
                reason="circuit_breaker_open",
            ).inc()

        # Fallback if selected model not available
        if not model_registry.is_model_available(selected):
            requested = selected
            logger.warning("model_unavailable", requested=selected)
            selected = settings.fallback_model
            routing_reason = f"fallback_from_{requested}"
            fallback_used = True
            fallback_reason = "model_unavailable"
            cost_estimate = 0.001
            
            fallback_triggers_total.labels(
                primary_model=requested,
                fallback_model=selected,
                reason="model_unavailable",
            ).inc()

        routing_overhead = (time.time() - start_time) * 1000

        logger.info(
            "router.decision",
            model_selected=selected,
            routing_method="rule_based",
            complexity_tier=complexity_tier,
            routing_reason=routing_reason,
            cost_estimate_usd=cost_estimate,
            fallback=fallback_used,
            routing_overhead_ms=routing_overhead,
        )

        # Record metric
        routing_decisions_total.labels(
            model_selected=selected,
            routing_method="rule_based",
            complexity_tier=complexity_tier,
        ).inc()

        routing_overhead_ms.observe(routing_overhead)

        return RoutingDecision(
            model_selected=selected,
            routing_method="rule_based",
            complexity_tier=complexity_tier,
            complexity_score=complexity_score,
            routing_reason=routing_reason,
            cost_estimate_usd=cost_estimate,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            candidates_scored=candidates_scored,
            routing_overhead_ms=routing_overhead,
            # Legacy fields
            selected_model=selected,
            reason=routing_reason,
            confidence=0.8,
            fallback=fallback_used,
        )

    # ========================================================================
    # PHASE 7: Advanced Decision Engine
    # ========================================================================

    async def route_optimized(
        self,
        query: str,
        features: QueryFeatures,
        user_tier: str = "free",
        embedding: Optional[List[float]] = None,
    ) -> RoutingDecision:
        """
        Advanced routing using multi-factor optimization
        Combines ML predictions, RAG, circuit breaker, and scoring
        """
        start_time = time.time()
        candidates: List[ModelCandidate] = []

        # Score each available model
        for model_name, config in MODEL_CONFIGS.items():
            if not model_registry.is_model_available(model_name):
                continue

            # Check circuit breaker first
            breaker = circuit_breaker_registry.get_breaker(model_name)
            if not breaker.can_attempt():
                logger.debug(
                    "model_excluded_by_circuit_breaker",
                    model=model_name,
                    state=breaker.get_state(),
                )
                continue

            # Calculate individual scores
            quality_score = self._calculate_quality_score(config, features)
            cost_score = self._calculate_cost_score(config, user_tier)
            latency_score = self._calculate_latency_score(config)

            # PHASE 5: Add ML prediction score
            ml_score = 0.0
            if settings.enable_ml_routing and self.ml_classifier:
                ml_score = await self._get_ml_score(query, model_name)

            # PHASE 6: Add RAG recommendation score
            rag_score = 0.0
            if settings.enable_rag_routing and self.rag_service and embedding:
                rag_score = await self._get_rag_score(embedding, model_name)

            # Weighted overall score
            overall_score = (
                quality_score * 0.3 +
                cost_score * 0.25 +
                latency_score * 0.15 +
                ml_score * 0.15 +
                rag_score * 0.15
            )

            candidates.append(
                ModelCandidate(
                    model_name=model_name,
                    quality_score=quality_score,
                    cost_score=cost_score,
                    latency_score=latency_score,
                    overall_score=overall_score,
                    metadata={
                        "ml_score": ml_score,
                        "rag_score": rag_score,
                    }
                )
            )

        # Sort by overall score
        candidates.sort(key=lambda x: x.overall_score, reverse=True)

        if not candidates:
            logger.warning("all_models_filtered_by_circuit_breaker")
            return await self.route_rule_based(query, features, user_tier)

        best = candidates[0]
        alternatives = [
            {"model": c.model_name, "score": c.overall_score}
            for c in candidates[1:3]
        ]

        complexity_score = feature_extractor.calculate_complexity_score(features)
        routing_overhead = (time.time() - start_time) * 1000

        logger.info(
            "router.decision",
            model_selected=best.model_name,
            routing_method="ml_scoring",
            complexity_tier="medium",
            complexity_score=complexity_score,
            routing_reason="multi_factor_optimization",
            cost_estimate_usd=0.02,
            fallback=False,
            routing_overhead_ms=routing_overhead,
        )

        routing_decisions_total.labels(
            model_selected=best.model_name,
            routing_method="ml_scoring",
            complexity_tier="medium",
        ).inc()

        routing_overhead_ms.observe(routing_overhead)

        return RoutingDecision(
            model_selected=best.model_name,
            routing_method="ml_scoring",
            complexity_tier="medium",
            complexity_score=best.overall_score,
            routing_reason="multi_factor_optimization",
            cost_estimate_usd=0.02,
            fallback_used=False,
            fallback_reason=None,
            candidates_scored=[
                {
                    "model": c.model_name,
                    "score": c.overall_score,
                    "quality": c.quality_score,
                    "cost": c.cost_score,
                }
                for c in candidates
            ],
            routing_overhead_ms=routing_overhead,
            # Legacy fields
            selected_model=best.model_name,
            reason="multi_factor_optimization",
            confidence=best.overall_score,
            alternatives=alternatives,
            fallback=False,
        )

    def _calculate_quality_score(self, config, features: QueryFeatures) -> float:
        """Calculate quality score for a model"""
        base_score = {"low": 0.3, "medium": 0.6, "high": 1.0}[config.quality_tier]
        
        # Boost for complex queries
        complexity = feature_extractor.calculate_complexity_score(features)
        if complexity > 0.6 and config.quality_tier == "high":
            base_score *= 1.2
        
        return min(base_score, 1.0)

    def _calculate_cost_score(self, config, user_tier: str) -> float:
        """Calculate cost score (higher is better = cheaper)"""
        if config.cost_per_1k_tokens == 0:
            return 1.0
        
        # Normalize cost (inverse - cheaper is better)
        max_cost = 0.03
        cost_score = 1.0 - (config.cost_per_1k_tokens / max_cost)
        
        # Enterprise users care less about cost
        if user_tier == "enterprise":
            cost_score = 0.5 + (cost_score * 0.5)
        
        return max(cost_score, 0.0)

    def _calculate_latency_score(self, config) -> float:
        """Calculate latency score (higher is better = faster)"""
        max_latency = 2000
        return 1.0 - min(config.avg_latency_ms / max_latency, 1.0)

    async def _get_ml_score(self, query: str, model_name: str) -> float:
        """
        Phase 5: Get ML classifier score.
        """
        if self.ml_classifier is None:
            return 0.0

        try:
            return await self.ml_classifier.score_model(query=query, model_name=model_name)
        except Exception as e:
            logger.error("ml_score_failed", error=str(e), model=model_name)
            return 0.0

    async def _get_rag_score(self, embedding: List[float], model_name: str) -> float:
        """
        Phase 6: Get RAG recommendation score.
        """
        if self.rag_service is None:
            return 0.0

        try:
            recommendations = await self.rag_service.recommend_model(
                query_embedding=embedding,
                top_k=settings.rag_top_k,
            )
            return float(recommendations.get(model_name, 0.0))
        except Exception as e:
            logger.error("rag_score_failed", error=str(e), model=model_name)
            return 0.0

    # ========================================================================
    # Main Routing Entry Point
    # ========================================================================

    async def route(
        self,
        query: str,
        user_id: str,
        user_tier: str = "free",
        features: Optional[QueryFeatures] = None,
        embedding: Optional[List[float]] = None,
    ) -> RoutingDecision:
        """
        Main routing method - dispatches to appropriate routing strategy
        """
        # Extract features if not provided
        if features is None:
            features = await feature_extractor.extract_features(query)

        # PHASE 7+: Use optimized routing if advanced features enabled
        if settings.enable_ml_routing or settings.enable_rag_routing:
            return await self.route_optimized(query, features, user_tier, embedding)
        
        # PHASE 3+: Use rule-based routing
        return await self.route_rule_based(query, features, user_tier)


# Global router instance
router = Router()
