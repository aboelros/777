"""
Unit and regression tests for Model Routing, Caching, and Cost Controls.
Verifies tenant-safe caching keys, dynamic data exclusion, and budget tracking.
"""

import pytest
from uuid import uuid4
from app.domains.ai.optimizer.cache import TenantSafeCache
from app.domains.ai.optimizer.router import ModelRouter
from app.domains.ai.optimizer.cost_tracker import TokenCostTracker


def test_tenant_safe_cache_isolation_and_exclusion():
    cache = TenantSafeCache(default_ttl_seconds=300)
    proj_a = uuid4()
    proj_b = uuid4()

    prompt = "What are your business hours?"
    response_a = "We are open 9am to 9pm in Store A."

    # Cache for Tenant A
    cached_set = cache.set(proj_a, prompt, response_a)
    assert cached_set is True

    # Tenant A retrieves its own cached response
    hit_a = cache.get(proj_a, prompt)
    assert hit_a == response_a

    # Tenant B querying the exact same prompt MUST NOT receive Tenant A's cached response!
    hit_b = cache.get(proj_b, prompt)
    assert hit_b is None

    # Dynamic data exclusion: Order status must never be cached
    order_prompt = "What is the status of my order #ORD-1234?"
    assert cache.is_cacheable(order_prompt) is False
    assert cache.set(proj_a, order_prompt, "Order is delivered") is False
    assert cache.get(proj_a, order_prompt) is None


def test_model_router_complexity_classification():
    # Simple greeting -> fast tier
    route_fast = ModelRouter.route("Hello")
    assert route_fast.tier == "fast"
    assert route_fast.model_name == "gemini-2.0-flash"

    # Arabic greeting -> fast tier
    route_fast_ar = ModelRouter.route("مساء الخير")
    assert route_fast_ar.tier == "fast"

    # High complexity complaint -> reasoning tier
    route_complex = ModelRouter.route("I want a full refund and I am filing a complaint with my lawyer!")
    assert route_complex.tier == "reasoning"
    assert route_complex.model_name == "gemini-1.5-pro"

    # Standard sales question -> standard tier
    route_std = ModelRouter.route("Do you have running shoes in red color?")
    assert route_std.tier == "standard"


def test_token_cost_tracker_budget_bounds():
    tracker = TokenCostTracker(monthly_budget_usd=10.0)
    proj = uuid4()

    # Record small turn
    rec1 = tracker.record_usage(proj, input_tokens=500, output_tokens=150, model_name="gemini-2.0-flash")
    assert rec1.estimated_cost_usd > 0
    assert tracker.is_within_budget(proj) is True

    # Record massive usage that exceeds budget
    rec2 = tracker.record_usage(proj, input_tokens=100_000_000, output_tokens=10_000_000, model_name="gemini-2.0-flash")
    assert tracker.get_tenant_spend(proj) > 10.0
    assert tracker.is_within_budget(proj) is False
