import asyncio

from src.models.schemas import QueryFeatures
import src.services.router as router_module
from src.services.router import Router


def test_route_rule_based_simple_query_prefers_llama():
    router = Router()
    features = QueryFeatures(
        token_count=10,
        query_length=40,
        word_count=8,
        sentence_count=1,
        is_coding=False,
        is_analytical=False,
        is_creative=False,
        has_code_block=False,
    )

    decision = asyncio.run(router.route_rule_based("hello", features, user_tier="free"))

    assert decision.selected_model == "llama-7b"
    assert decision.reason == "simple_query"


def test_route_rule_based_coding_with_code_prefers_premium_for_pro():
    router = Router()
    features = QueryFeatures(
        token_count=120,
        query_length=300,
        word_count=70,
        sentence_count=4,
        is_coding=True,
        is_analytical=False,
        is_creative=False,
        has_code_block=True,
    )

    decision = asyncio.run(
        router.route_rule_based("```python\nprint('x')\n```", features, user_tier="pro")
    )

    assert decision.selected_model == "gpt-4"
    assert decision.reason == "coding_query_with_code"


def test_get_ml_score_uses_ml_service():
    class FakeMLService:
        async def score_model(self, query: str, model_name: str) -> float:
            return 0.88 if model_name == "gpt-4" else 0.2

    router = Router()
    router.ml_classifier = FakeMLService()

    score = asyncio.run(router._get_ml_score("Write optimized code", "gpt-4"))
    assert score == 0.88


def test_get_rag_score_uses_rag_recommendations():
    class FakeRAGService:
        async def recommend_model(self, query_embedding, top_k: int):
            return {"claude-sonnet": 0.73, "gpt-4": 0.65}

    router = Router()
    router.rag_service = FakeRAGService()

    score = asyncio.run(router._get_rag_score([0.1, 0.2, 0.3], "claude-sonnet"))
    assert score == 0.73


def test_route_optimized_includes_phase5_phase6_scores(monkeypatch):
    class FakeMLService:
        async def score_model(self, query: str, model_name: str) -> float:
            scores = {"llama-7b": 0.2, "claude-sonnet": 0.5, "gpt-4": 1.0}
            return scores.get(model_name, 0.0)

    class FakeRAGService:
        async def recommend_model(self, query_embedding, top_k: int):
            return {"llama-7b": 0.1, "claude-sonnet": 0.6, "gpt-4": 0.9}

    router = Router()
    router.ml_classifier = FakeMLService()
    router.rag_service = FakeRAGService()

    monkeypatch.setattr(router_module.settings, "enable_ml_routing", True)
    monkeypatch.setattr(router_module.settings, "enable_rag_routing", True)

    features = QueryFeatures(
        token_count=180,
        query_length=600,
        word_count=130,
        sentence_count=7,
        is_coding=True,
        is_analytical=True,
        is_creative=False,
        has_code_block=True,
    )

    decision = asyncio.run(
        router.route_optimized(
            query="Analyze and optimize this distributed system code path",
            features=features,
            user_tier="enterprise",
            embedding=[0.1, 0.2, 0.3],
        )
    )

    assert decision.reason == "multi_factor_optimization"
    assert decision.selected_model == "gpt-4"
