import time
from typing import List, Dict, Any, Optional
from uuid import UUID
import structlog

from app.core.context import TenantContext
from .prompts import prompt_registry, PromptBuilder, TenantPromptConfig, BrandProfile
from .rag import tenant_rag_retriever
from .tools import tool_registry, SecureToolExecutor, ToolExecutionOutcome
from .guardrails import InputSanitizer, PromptInjectionDetector, OutputVerifier
from .optimizer import tenant_safe_cache, ModelRouter, token_cost_tracker
from .observability import agent_tracer, AgentTraceRecord, ToolTraceEntry

logger = structlog.get_logger(__name__)


class AgentTurnResponse:
    """Result of an autonomous sales agent turn."""
    def __init__(
        self,
        response_text: str,
        status: str = "success",
        tool_outcomes: Optional[List[ToolExecutionOutcome]] = None,
        is_refusal: bool = False,
        escalation_triggered: bool = False,
        prompt_version: str = "1.0.0",
        model_used: str = "gemini-2.0-flash",
        latency_ms: float = 0.0
    ):
        self.response_text = response_text
        self.status = status
        self.tool_outcomes = tool_outcomes or []
        self.is_refusal = is_refusal
        self.escalation_triggered = escalation_triggered
        self.prompt_version = prompt_version
        self.model_used = model_used
        self.latency_ms = latency_ms


class ProductionSalesAgent:
    """
    Production-grade AI Sales Agent runtime orchestrating grounding,
    tool authorization, prompt injection defense, caching, and observability.
    """

    def __init__(self, uow=None, ai_client=None):
        self.uow = uow
        self.ai_client = ai_client
        self.tool_executor = SecureToolExecutor(uow=uow)

    async def execute_turn(
        self,
        customer_message: str,
        context: TenantContext,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        caller_customer_id: Optional[UUID] = None,
        caller_role: str = "customer",
        conversation_id: Optional[str] = None
    ) -> AgentTurnResponse:
        """Execute a complete customer turn through all 7 defensive layers."""
        start_time = time.monotonic()
        pid = context.project_id

        # Layer 5: Input Sanitization
        is_valid, clean_msg, reason = InputSanitizer.sanitize(customer_message)
        if not is_valid:
            elapsed = (time.monotonic() - start_time) * 1000.0
            return AgentTurnResponse(
                response_text="Message could not be processed.",
                status="rejected",
                is_refusal=True,
                latency_ms=round(elapsed, 2)
            )

        # Layer 5: Prompt Injection / Adversarial Scan
        inj_scan = PromptInjectionDetector.scan(clean_msg)
        if inj_scan.is_injection:
            elapsed = (time.monotonic() - start_time) * 1000.0
            agent_tracer.record_trace(AgentTraceRecord(
                project_id=pid,
                customer_id=caller_customer_id,
                conversation_id=conversation_id,
                prompt_version="guardrail",
                model_name="none",
                status="refused",
                flagged_reason=f"Injection detected: {','.join(inj_scan.detected_patterns)}",
                latency_total_ms=round(elapsed, 2)
            ))
            return AgentTurnResponse(
                response_text="I am here to assist you with our store's products and orders. How can I help you today?",
                status="refused",
                is_refusal=True,
                latency_ms=round(elapsed, 2)
            )

        # Layer 6: Tenant Safe Cache
        cached = tenant_safe_cache.get(pid, clean_msg)
        if cached:
            elapsed = (time.monotonic() - start_time) * 1000.0
            agent_tracer.record_trace(AgentTraceRecord(
                project_id=pid,
                customer_id=caller_customer_id,
                conversation_id=conversation_id,
                prompt_version="cached",
                model_name="cache",
                cache_hit=True,
                latency_total_ms=round(elapsed, 2)
            ))
            return AgentTurnResponse(response_text=cached, latency_ms=round(elapsed, 2))

        # Layer 1: Prompt Configuration & Version
        prompt_cfg = prompt_registry.get_active_config(pid)
        if not prompt_cfg:
            prompt_cfg = TenantPromptConfig(
                project_id=pid,
                brand=BrandProfile(store_name="Store"),
                version="1.0.0"
            )
            prompt_registry.register_version(prompt_cfg)

        # Layer 2: Grounded Knowledge (RAG) Retrieval
        rag_res = tenant_rag_retriever.retrieve(pid, clean_msg)
        retrieved_evidence = rag_res.formatted_context if rag_res.has_sufficient_evidence else None

        # Layer 6: Model Route
        route = ModelRouter.route(clean_msg)

        # Layer 1: Delimited Prompt Construction
        system_prompt = PromptBuilder.build_system_prompt(prompt_cfg)
        user_turn = PromptBuilder.assemble_user_turn(
            customer_message=clean_msg,
            conversation_history=conversation_history,
            retrieved_evidence=retrieved_evidence
        )

        # Execute Provider Turn (with tools)
        raw_text, tool_calls = await self._call_provider(system_prompt, user_turn, route)

        # Layer 3 & 4: Controlled Tool Execution with RBAC & IDOR Guard
        outcomes: List[ToolExecutionOutcome] = []
        tool_traces: List[ToolTraceEntry] = []
        for call in tool_calls:
            t_name = call.get("name", "")
            t_args = call.get("arguments", {})
            outcome = await self.tool_executor.execute(
                tool_name=t_name,
                arguments=t_args,
                context=context,
                caller_customer_id=caller_customer_id,
                caller_role=caller_role
            )
            outcomes.append(outcome)
            tool_traces.append(ToolTraceEntry(
                tool_name=t_name,
                risk_level=outcome.risk_level.value,
                status=outcome.status,
                execution_time_ms=outcome.execution_time_ms,
                error=outcome.error
            ))

        # If tools executed, format a follow-up answer or use primary response
        final_text = self._synthesize_response(raw_text, outcomes, prompt_cfg)

        # Layer 5: Output Verification
        max_disc = prompt_cfg.policy.max_discount_percent
        verified = OutputVerifier.verify(final_text, max_allowed_discount_percent=max_disc)
        delivered_text = verified.cleaned_output if verified.is_safe else (verified.suggested_safe_fallback or final_text)

        # Layer 6: Cache Set (if eligible)
        if verified.is_safe and not tool_calls:
            tenant_safe_cache.set(pid, clean_msg, delivered_text)

        # Layer 6: Token and Cost Tracking
        in_tok = max(1, len(user_turn) // 4)
        out_tok = max(1, len(delivered_text) // 4)
        token_cost_tracker.record_usage(pid, in_tok, out_tok, route.model_name)

        # Layer 7: Observability Trace Recording
        elapsed_total = (time.monotonic() - start_time) * 1000.0
        agent_tracer.record_trace(AgentTraceRecord(
            project_id=pid,
            customer_id=caller_customer_id,
            conversation_id=conversation_id,
            prompt_version=prompt_cfg.version,
            model_name=route.model_name,
            retrieval_count=len(rag_res.chunks),
            tools=tool_traces,
            latency_total_ms=round(elapsed_total, 2),
            input_tokens=in_tok,
            output_tokens=out_tok,
            status="success"
        ))

        return AgentTurnResponse(
            response_text=delivered_text,
            status="success",
            tool_outcomes=outcomes,
            prompt_version=prompt_cfg.version,
            model_used=route.model_name,
            latency_ms=round(elapsed_total, 2)
        )

    async def _call_provider(self, system_prompt: str, user_turn: str, route) -> tuple[str, list]:
        """Invoke AI provider or mock fallback."""
        if self.ai_client:
            resp = await self.ai_client.generate_response(
                prompt=user_turn,
                context={"persona": "custom", "persona_detail": system_prompt},
                use_functions=True
            )
            return resp.get("text", ""), resp.get("function_calls", [])
        return "I am glad to assist you. What can I help you find today?", []

    def _synthesize_response(self, text: str, outcomes: List[ToolExecutionOutcome], cfg: TenantPromptConfig) -> str:
        """Synthesize tool outcomes into customer message if tools were executed."""
        if not outcomes:
            return text
        pieces = [text] if text else []
        for o in outcomes:
            if o.status == "success":
                if o.tool_name == "check_inventory":
                    pieces.append(f"{o.data.get('product_name')}: {o.data.get('status_label')} (${o.data.get('unit_price', 0.0)})")
                elif o.tool_name == "get_order_status":
                    pieces.append(f"Order #{o.data.get('order_number')} is currently {o.data.get('status')}.")
                elif o.tool_name == "get_store_policy":
                    pieces.append(f"Store Policy: {o.data.get('summary')} (Return window: {o.data.get('max_return_days')} days).")
            else:
                pieces.append(o.error or "Action could not be completed.")
        return "\n".join(pieces)
