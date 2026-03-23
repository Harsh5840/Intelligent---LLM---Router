import asyncio
import pytest
from fastapi import HTTPException

from src.api import endpoints
from src.models.schemas import ChatRequest, QueryFeatures, RoutingDecision


def test_chat_propagates_http_exception(monkeypatch):
    request = ChatRequest(
        query="Need help with Python",
        user_id="u1",
        context=None,
        user_tier="pro",
    )

    async def fake_cache_lookup(query, models):
        return None

    async def fake_extract_features(query):
        return QueryFeatures(
            token_count=20,
            query_length=80,
            word_count=15,
            sentence_count=1,
            is_coding=True,
            is_analytical=False,
            is_creative=False,
            has_code_block=False,
        )

    async def fake_route(**kwargs):
        return RoutingDecision(
            selected_model="missing-model",
            reason="test",
            confidence=1.0,
            fallback=False,
        )

    monkeypatch.setattr(endpoints.cache_service, "get_cached_response_any_model", fake_cache_lookup)
    monkeypatch.setattr(endpoints.feature_extractor, "extract_features", fake_extract_features)
    monkeypatch.setattr(endpoints.router, "route", fake_route)
    monkeypatch.setattr(endpoints.model_registry, "get_client", lambda model_name: None)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(endpoints.chat(request))

    assert exc_info.value.status_code == 503


def test_stats_uses_aggregate_stats(monkeypatch):
    async def fake_cache_stats():
        return {
            "keyspace_hits": 30,
            "keyspace_misses": 10,
        }

    async def fake_aggregate_stats():
        return {
            "total_requests": 42,
            "avg_latency_ms": 250.0,
            "model_distribution": {
                "llama-7b": 20,
                "gpt-4": 12,
                "claude-sonnet": 10,
            },
            "error_rate": 0.05,
        }

    monkeypatch.setattr(endpoints.cache_service, "get_cache_stats", fake_cache_stats)
    monkeypatch.setattr(endpoints.data_collection_service, "get_aggregate_stats", fake_aggregate_stats)

    response = asyncio.run(endpoints.get_stats())

    assert response.total_requests == 42
    assert response.avg_latency_ms == 250.0
    assert response.cache_hit_rate == 0.75
    assert response.error_rate == 0.05
    assert response.model_distribution["gpt-4"] == 12
