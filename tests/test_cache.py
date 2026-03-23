import asyncio

from src.services.cache import CacheService


def test_get_cached_response_any_model_returns_first_match(monkeypatch):
    service = CacheService()

    async def fake_get_cached_response(query: str, model: str):
        if model == "gpt-4":
            return {
                "response": "cached response",
                "model": "gpt-4",
                "latency_ms": 123.0,
            }
        return None

    monkeypatch.setattr(service, "get_cached_response", fake_get_cached_response)

    result = asyncio.run(
        service.get_cached_response_any_model(
            query="test-query",
            models=["llama-7b", "gpt-4", "claude-sonnet"],
        )
    )

    assert result is not None
    assert result["model"] == "gpt-4"
