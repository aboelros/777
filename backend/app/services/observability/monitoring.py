"""
Observability Service
Distributed tracing, metrics collection, and logging aggregation.
"""
from typing import Dict, Any, Optional
import time
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
import structlog

logger = structlog.get_logger(__name__)


class TracingService:
    """
    Distributed tracing for request flows.
    """
    
    def __init__(self):
        self.traces = {}
    
    def create_trace(self, operation: str) -> str:
        """Create a new trace."""
        trace_id = str(uuid.uuid4())
        self.traces[trace_id] = {
            'id': trace_id,
            'operation': operation,
            'started_at': datetime.utcnow(),
            'spans': []
        }
        return trace_id
    
    def add_span(
        self,
        trace_id: str,
        name: str,
        duration_ms: float,
        metadata: Optional[Dict] = None
    ):
        """Add span to trace."""
        if trace_id in self.traces:
            self.traces[trace_id]['spans'].append({
                'name': name,
                'duration_ms': duration_ms,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            })
    
    @asynccontextmanager
    async def trace_span(self, trace_id: str, span_name: str):
        """Context manager for tracing a span."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000
            self.add_span(trace_id, span_name, duration)
    
    def get_trace(self, trace_id: str) -> Optional[Dict]:
        """Get trace details."""
        return self.traces.get(trace_id)


class MetricsCollector:
    """
    Collect and aggregate application metrics.
    """
    
    def __init__(self):
        self.metrics = {}
    
    def increment(self, metric_name: str, value: int = 1, tags: Optional[Dict] = None):
        """Increment counter metric."""
        key = self._get_metric_key(metric_name, tags)
        if key not in self.metrics:
            self.metrics[key] = {'type': 'counter', 'value': 0, 'tags': tags}
        self.metrics[key]['value'] += value
    
    def gauge(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """Set gauge metric."""
        key = self._get_metric_key(metric_name, tags)
        self.metrics[key] = {'type': 'gauge', 'value': value, 'tags': tags}
    
    def histogram(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """Record histogram value."""
        key = self._get_metric_key(metric_name, tags)
        if key not in self.metrics:
            self.metrics[key] = {'type': 'histogram', 'values': [], 'tags': tags}
        self.metrics[key]['values'].append(value)
    
    def _get_metric_key(self, name: str, tags: Optional[Dict]) -> str:
        """Generate metric key with tags."""
        if tags:
            tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{name}[{tag_str}]"
        return name
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {}


class AuditLogger:
    """
    Audit logging for compliance and security.
    """
    
    def __init__(self):
        self.audit_log = []
    
    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        resource_type: str,
        resource_id: str,
        action: str,
        metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log audit event.
        
        Args:
            event_type: Type of event (access, modification, deletion)
            user_id: User performing action
            resource_type: Type of resource (user, project, order)
            resource_id: Resource identifier
            action: Action performed (create, read, update, delete)
            metadata: Additional context
            ip_address: Client IP address
        """
        event = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'metadata': metadata or {},
            'ip_address': ip_address
        }
        
        self.audit_log.append(event)
        
        logger.info(
            "Audit event logged",
            event_type=event_type,
            user_id=user_id,
            action=action,
            resource=f"{resource_type}:{resource_id}"
        )
    
    def get_audit_trail(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get audit trail with filters.
        
        Args:
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            user_id: Filter by user
            limit: Maximum events to return
            
        Returns:
            List of audit events
        """
        filtered = self.audit_log
        
        if resource_type:
            filtered = [e for e in filtered if e['resource_type'] == resource_type]
        if resource_id:
            filtered = [e for e in filtered if e['resource_id'] == resource_id]
        if user_id:
            filtered = [e for e in filtered if e['user_id'] == user_id]
        
        # Sort by timestamp descending
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered[:limit]


class PerformanceMonitor:
    """
    Monitor application performance and health.
    """
    
    def __init__(self):
        self.metrics = MetricsCollector()
    
    @asynccontextmanager
    async def measure(self, operation: str, tags: Optional[Dict] = None):
        """Measure operation duration."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000
            self.metrics.histogram(f'operation.duration', duration, tags={'operation': operation, **(tags or {})})
    
    async def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float
    ):
        """Record HTTP request metrics."""
        self.metrics.increment(
            'http.requests',
            tags={'method': method, 'path': path, 'status': status_code}
        )
        self.metrics.histogram(
            'http.duration',
            duration_ms,
            tags={'method': method, 'path': path}
        )
    
    async def record_error(self, error_type: str, context: Optional[Dict] = None):
        """Record error occurrence."""
        self.metrics.increment(
            'errors',
            tags={'type': error_type}
        )
        
        logger.error(
            "Error recorded",
            error_type=error_type,
            context=context
        )


# Global instances
tracing = TracingService()
metrics = MetricsCollector()
audit_logger = AuditLogger()
performance_monitor = PerformanceMonitor()
