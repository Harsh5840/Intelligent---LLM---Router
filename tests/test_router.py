import asyncio

from src.models.schemas import QueryFeatures
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
