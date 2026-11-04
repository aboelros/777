from typing import List, Dict, Optional
from uuid import UUID
import structlog
from .models import AgentTraceRecord, ToolTraceEntry
from .redactor import PIIRedactor

logger = structlog.get_logger("ai.trace")


class AgentTracer:
    """
    Records and emits privacy-safe, structured traces for every AI sales agent turn.
    """

    def __init__(self, max_retained_traces: int = 1000):
        # project_id -> list of AgentTraceRecord
        self._traces: Dict[UUID, List[AgentTraceRecord]] = {}
        self.max_retained_traces = max_retained_traces

    def record_trace(self, trace: AgentTraceRecord):
        """Store trace record and emit structured privacy-safe log event."""
        pid = trace.project_id
        if pid not in self._traces:
            self._traces[pid] = []

        self._traces[pid].append(trace)
        if len(self._traces[pid]) > self.max_retained_traces:
            self._traces[pid].pop(0)

        # Log structured event with redacted reason
        clean_reason = PIIRedactor.redact(trace.flagged_reason) if trace.flagged_reason else None
        logger.info(
            "ai_turn_executed",
            trace_id=str(trace.trace_id),
            project_id=str(trace.project_id),
            prompt_version=trace.prompt_version,
            model=trace.model_name,
            cache_hit=trace.cache_hit,
            latency_ms=trace.latency_total_ms,
            tools_count=len(trace.tools),
            input_tokens=trace.input_tokens,
            output_tokens=trace.output_tokens,
            status=trace.status,
            flagged=clean_reason
        )

    def get_tenant_traces(self, project_id: UUID, limit: int = 20) -> List[AgentTraceRecord]:
        """Fetch latest trace history for a tenant."""
        traces = self._traces.get(project_id, [])
        return list(reversed(traces[-limit:]))


# Global tracer instance
agent_tracer = AgentTracer()
