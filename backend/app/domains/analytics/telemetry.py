import structlog
import time
from uuid import UUID
from typing import Dict, Any, Optional
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.core.database import AsyncSessionLocal
from app.domains.analytics.models import APILog, AITraceLog

logger = structlog.get_logger(__name__)

class TelemetryService:
    """
    Handles logging APILogs and AITraceLogs asynchronously to prevent
    blocking the main request/response cycle.
    """
    
    @staticmethod
    async def log_api_request_async(
        project_id: UUID, 
        endpoint: str, 
        method: str, 
        status_code: int,
        duration_ms: float,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
        user_id: Optional[UUID] = None
    ):
        """Asynchronously insert an APILog"""
        try:
            async with AsyncSessionLocal() as session:
                log_entry = APILog(
                    project_id=project_id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    request=request_data,
                    response=response_data,
                    user_id=user_id
                )
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            # We explicitly swallow exceptions so telemetry failure doesn't crash the app
            logger.error("failed_to_write_api_telemetry", error=str(e))
            
    @staticmethod
    async def log_ai_trace_async(
        project_id: UUID,
        trace_id: str,
        provider: str,
        model_version: str,
        system_prompt: str,
        user_prompt: str,
        completion: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        estimated_cost: float = 0.0
    ):
        """Asynchronously insert an AITraceLog"""
        try:
            async with AsyncSessionLocal() as session:
                trace_entry = AITraceLog(
                    project_id=project_id,
                    trace_id=trace_id,
                    provider=provider,
                    model_version=model_version,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    completion=completion,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    latency_ms=latency_ms,
                    estimated_cost=estimated_cost
                )
                session.add(trace_entry)
                await session.commit()
        except Exception as e:
            logger.error("failed_to_write_ai_trace", error=str(e))
            
    @classmethod
    def emit_ai_trace(
        cls, 
        background_tasks: BackgroundTasks, 
        **kwargs
    ):
        """
        Helper to cleanly queue an AI trace write in the background.
        Usage: TelemetryService.emit_ai_trace(background_tasks, project_id=...)
        """
        background_tasks.add_task(cls.log_ai_trace_async, **kwargs)
