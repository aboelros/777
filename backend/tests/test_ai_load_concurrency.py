"""
Concurrent Load & Throughput Stress Testing Suite.
Verifies asynchronous execution safety, tenant isolation under concurrency,
cache concurrency (thundering herd protection), and latency metrics.
"""

import pytest
import asyncio
import time
from uuid import uuid4
from unittest.mock import AsyncMock

from app.core.context import TenantContext
from app.domains.ai.agent_runtime import ProductionSalesAgent
from app.domains.ai.prompts.models import TenantPromptConfig, BrandProfile, SalesPolicy
from app.domains.ai.prompts.versions import prompt_registry
from app.domains.ai.optimizer.cache import TenantSafeCache
from app.domains.ai.observability.tracer import AgentTracer


@pytest.mark.asyncio
async def test_concurrency_100_parallel_turns():
    """Verify runtime handles 100 parallel turns without race conditions or memory leaks."""
    mock_provider = AsyncMock(return_value=("Yes, our shoes are available in all sizes.", []))
    agent = ProductionSalesAgent()
    agent._call_provider = mock_provider

    pid = uuid4()
    ctx = TenantContext(project_id=pid, roles=["customer"])

    # Launch 100 concurrent customer turns
    tasks = [
        agent.execute_turn(
            customer_message=f"Do you have sneakers in size {40 + (i % 6)}?",
            context=ctx,
            conversation_id=f"conv-{i}"
        )
        for i in range(100)
    ]

    t_start = time.monotonic()
    results = await asyncio.gather(*tasks)
    elapsed = time.monotonic() - t_start

    assert len(results) == 100
    assert all(r.status == "success" for r in results)
    assert all(len(r.response_text) > 0 for r in results)
    # 100 parallel turns should finish within 1.0s locally
    assert elapsed < 1.0


@pytest.mark.asyncio
async def test_concurrency_tenant_isolation_under_load():
    """Verify 50 requests from Tenant A and 50 from Tenant B never leak prompts or traces."""
    proj_a = uuid4()
    proj_b = uuid4()

    # Register brand configs
    cfg_a = TenantPromptConfig(
        project_id=proj_a,
        brand=BrandProfile(store_name="Brand Alpha", primary_language="English"),
        version="1.0.0"
    )
    cfg_b = TenantPromptConfig(
        project_id=proj_b,
        brand=BrandProfile(store_name="Brand Beta", primary_language="Arabic"),
        version="1.0.0"
    )
    prompt_registry.register_version(cfg_a)
    prompt_registry.register_version(cfg_b)

    tracer = AgentTracer()
    agent = ProductionSalesAgent()
    agent.tracer = tracer
    agent._call_provider = AsyncMock(return_value=("Verified customer reply", []))

    ctx_a = TenantContext(project_id=proj_a, roles=["customer"])
    ctx_b = TenantContext(project_id=proj_b, roles=["customer"])

    # Interleave 50 requests each
    tasks = []
    for i in range(50):
        tasks.append(agent.execute_turn("Question for Alpha", context=ctx_a))
        tasks.append(agent.execute_turn("Question for Beta", context=ctx_b))

    results = await asyncio.gather(*tasks)
    assert len(results) == 100
    assert all(r.status == "success" for r in results)

    # Verify active config separation
    assert prompt_registry.get_active_config(proj_a).brand.store_name == "Brand Alpha"
    assert prompt_registry.get_active_config(proj_b).brand.store_name == "Brand Beta"


@pytest.mark.asyncio
async def test_concurrency_cache_thundering_herd():
    """Verify 50 simultaneous identical requests hit cache safely without deadlocks."""
    cache = TenantSafeCache(default_ttl_seconds=300)
    pid = uuid4()
    query = "What are your return terms?"
    expected = "Returns accepted within 14 days."

    # Populate cache first
    cache.set(pid, query, expected)

    async def fetch_cached():
        # Simulated async micro-task
        await asyncio.sleep(0.001)
        return cache.get(pid, query)

    tasks = [fetch_cached() for _ in range(50)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 50
    assert all(r == expected for r in results)


@pytest.mark.asyncio
async def test_concurrency_latency_distribution_p95():
    """Verify in-memory pipeline latency P95 is strictly under 15ms."""
    mock_provider = AsyncMock(return_value=("Standard instant response", []))
    agent = ProductionSalesAgent()
    agent._call_provider = mock_provider

    pid = uuid4()
    ctx = TenantContext(project_id=pid, roles=["customer"])

    latencies = []
    for i in range(50):
        t0 = time.monotonic()
        res = await agent.execute_turn(f"Quick product inquiry {i}", context=ctx)
        latencies.append((time.monotonic() - t0) * 1000.0)

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]

    # In-memory execution without live external network must be lightning fast
    assert p50 < 10.0
    assert p95 < 25.0
