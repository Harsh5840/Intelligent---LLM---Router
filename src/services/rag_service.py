"""
Phase 6 runtime service for RAG-enhanced routing recommendations.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

import numpy as np

from src.config import settings
from src.services.data_collection import data_collection_service
from src.utils.logging import get_logger

logger = get_logger(__name__)

try:
    from pinecone import Pinecone

    PINECONE_AVAILABLE = True
except ImportError:
    Pinecone = None
    PINECONE_AVAILABLE = False


class RoutingRAGService:
    """
    Provides model recommendation scores from historical, semantically
    similar routing decisions.
    """

    def __init__(self):
        self.initialized = False
        self.index = None

        if not PINECONE_AVAILABLE or not settings.pinecone_api_key or Pinecone is None:
            logger.info("rag_runtime_using_db_fallback")
            return

        try:
            client = Pinecone(api_key=settings.pinecone_api_key)
            index_names = list(client.list_indexes().names())
            if settings.pinecone_index_name in index_names:
                self.index = client.Index(settings.pinecone_index_name)
                self.initialized = True
                logger.info("rag_runtime_initialized", index=settings.pinecone_index_name)
            else:
                logger.warning("rag_index_not_found", index=settings.pinecone_index_name)
        except Exception as exc:
            logger.error("rag_runtime_init_failed", error=str(exc))
            self.initialized = False

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        a = np.asarray(vec_a, dtype=float)
        b = np.asarray(vec_b, dtype=float)

        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0

        return float(np.dot(a, b) / denom)

    async def index_routing_log(
        self,
        log_id: str,
        query: str,
        embedding: List[float],
        model_used: str,
        latency_ms: float,
        success: bool,
        rating: Optional[float] = None,
    ) -> bool:
        """
        Persist routing decision into vector index when available.
        """
        if not self.initialized or self.index is None:
            return False

        try:
            metadata = {
                "query": query[:500],
                "model_used": model_used,
                "latency_ms": float(latency_ms),
                "success": bool(success),
                "rating": float(rating or 0.0),
            }
            self.index.upsert(
                vectors=[{"id": str(log_id), "values": embedding, "metadata": metadata}],
                namespace=settings.rag_namespace,
            )
            return True
        except Exception as exc:
            logger.error("rag_index_upsert_failed", error=str(exc))
            return False

    async def recommend_model(
        self,
        query_embedding: List[float],
        top_k: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Return recommendation score per model in [0,1].
        """
        if self.initialized and self.index is not None:
            recommendations = await self._recommend_from_pinecone(
                query_embedding=query_embedding,
                top_k=top_k or settings.rag_top_k,
            )
            if recommendations:
                return recommendations

        return await self._recommend_from_db(
            query_embedding=query_embedding,
            top_k=top_k or settings.rag_top_k,
        )

    async def _recommend_from_pinecone(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> Dict[str, float]:
        if self.index is None:
            return {}

        index = self.index

        try:
            result = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=settings.rag_namespace,
            )

            matches = getattr(result, "matches", None)
            if matches is None and isinstance(result, dict):
                matches = result["matches"] if "matches" in result else []

            model_scores: Dict[str, List[float]] = {}

            for match in matches or []:
                metadata = getattr(match, "metadata", None)
                score = getattr(match, "score", None)

                if metadata is None and isinstance(match, dict):
                    metadata = match.get("metadata", {})
                    score = match.get("score", 0.0)

                similarity = float(score or 0.0)
                if similarity < settings.rag_min_similarity:
                    continue

                if metadata is None:
                    continue

                model_name = metadata.get("model_used")
                if not model_name:
                    continue

                success = 1.0 if metadata.get("success", False) else 0.0
                rating = float(metadata.get("rating", 0.0)) / 5.0
                combined = (similarity * 0.5) + (success * 0.3) + (rating * 0.2)

                model_scores.setdefault(model_name, []).append(combined)

            return {
                model: float(np.mean(scores))
                for model, scores in model_scores.items()
            }
        except Exception as exc:
            logger.error("rag_pinecone_query_failed", error=str(exc))
            return {}

    async def _recommend_from_db(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> Dict[str, float]:
        try:
            historical_data = await data_collection_service.get_training_data(limit=2000)
            if not historical_data:
                return {}

            scored_rows = []
            for row in historical_data:
                embedding = row.get("embedding")
                if not embedding:
                    continue

                similarity = self._cosine_similarity(query_embedding, embedding)
                if similarity < settings.rag_min_similarity:
                    continue

                scored_rows.append((similarity, row))

            if not scored_rows:
                return {}

            scored_rows.sort(key=lambda item: item[0], reverse=True)
            top_rows = scored_rows[:top_k]

            model_scores: Dict[str, List[float]] = {}
            for similarity, row in top_rows:
                model_name = row.get("model_used")
                if not model_name:
                    continue

                combined = (similarity * 0.7) + 0.3
                model_scores.setdefault(model_name, []).append(combined)

            return {
                model: float(np.mean(scores))
                for model, scores in model_scores.items()
            }
        except Exception as exc:
            logger.error("rag_db_fallback_failed", error=str(exc))
            return {}
