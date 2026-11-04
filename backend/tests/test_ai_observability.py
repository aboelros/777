"""
Unit and regression tests for Observability, Structured Tracing, and PII Redaction.
Verifies redaction of customer phone numbers, emails, cards, and structured trace emissions.
"""

import pytest
from uuid import uuid4
from app.domains.ai.observability.redactor import PIIRedactor
from app.domains.ai.observability.models import AgentTraceRecord, ToolTraceEntry
from app.domains.ai.observability.tracer import AgentTracer


def test_pii_redactor_multi_format():
    # Email redaction
    text_email = "Contact me at customer.doe@example.com for shipping details."
    redacted_email = PIIRedactor.redact(text_email)
    assert "customer.doe@example.com" not in redacted_email
    assert "[REDACTED_EMAIL]" in redacted_email

    # Egyptian and international phone numbers
    text_phone_eg = "My Egyptian phone number is 01012345678 and my international is +201198765432."
    redacted_phone = PIIRedactor.redact(text_phone_eg)
    assert "01012345678" not in redacted_phone
    assert "[REDACTED_PHONE]" in redacted_phone

    # Secret and token redaction
    text_token = "Authorization header: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.abc_12345"
    redacted_token = PIIRedactor.redact(text_token)
    assert "[REDACTED_BEARER]" in redacted_token


def test_agent_tracer_recording_and_retrieval():
    tracer = AgentTracer(max_retained_traces=50)
    proj_id = uuid4()
    cust_id = uuid4()

    trace = AgentTraceRecord(
        project_id=proj_id,
        customer_id=cust_id,
        prompt_version="1.0.0",
        model_name="gemini-2.0-flash",
        tools=[
            ToolTraceEntry(
                tool_name="search_products",
                risk_level="read_only",
                status="success",
                execution_time_ms=45.2
            )
        ],
        latency_total_ms=180.5,
        input_tokens=250,
        output_tokens=65,
        status="success"
    )

    tracer.record_trace(trace)
    tenant_traces = tracer.get_tenant_traces(proj_id)

    assert len(tenant_traces) == 1
    assert tenant_traces[0].trace_id == trace.trace_id
    assert tenant_traces[0].tools[0].tool_name == "search_products"
    assert tenant_traces[0].input_tokens == 250
