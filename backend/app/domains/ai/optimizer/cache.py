import hashlib
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


class TenantSafeCache:
    """
    Tenant-partitioned in-memory and distributed cache.
    Guarantees that cached responses can never leak across tenant boundaries.
    Strictly forbids caching dynamic, stateful, or customer-specific private data.
    """

    UNCACHEABLE_KEYWORDS = [
        "order", "status", "track", "refund", "ticket", "address",
        "phone", "email", "cancel", "طلبي", "الأوردر", "تتبع", "عنواني", "إلغاء"
    ]

    def __init__(self, default_ttl_seconds: int = 1800):
        # Key: "project_id:sha256" -> {"response": str, "expires_at": datetime}
        self._store: Dict[str, Dict[str, Any]] = {}
        self.default_ttl_seconds = default_ttl_seconds

    def _generate_key(self, project_id: UUID, prompt: str) -> str:
        """Construct a tenant-scoped SHA-256 cache key."""
        prompt_hash = hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
        return f"{str(project_id)}:{prompt_hash}"

    def is_cacheable(self, prompt: str) -> bool:
        """Determine if a prompt is eligible for response caching."""
        lower_prompt = prompt.lower()
        for kw in self.UNCACHEABLE_KEYWORDS:
            if kw in lower_prompt:
                return False
        return True

    def get(self, project_id: UUID, prompt: str) -> Optional[str]:
        """Retrieve cached response if within TTL and tenant-matched."""
        if not self.is_cacheable(prompt):
            return None

        key = self._generate_key(project_id, prompt)
        entry = self._store.get(key)
        if not entry:
            return None

        if datetime.utcnow() > entry["expires_at"]:
            self._store.pop(key, None)
            return None

        logger.debug("Tenant cache hit", project_id=str(project_id))
        return entry["response"]

    def set(
        self,
        project_id: UUID,
        prompt: str,
        response: str,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Store response in tenant partition if cacheable."""
        if not self.is_cacheable(prompt):
            return False

        key = self._generate_key(project_id, prompt)
        ttl = ttl_seconds or self.default_ttl_seconds
        self._store[key] = {
            "response": response,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
        }
        return True

    def clear_tenant(self, project_id: UUID) -> int:
        """Evict all entries for a specific tenant during prompt or catalog updates."""
        prefix = f"{str(project_id)}:"
        keys_to_del = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_del:
            self._store.pop(k, None)
        return len(keys_to_del)


# Global cache instance
tenant_safe_cache = TenantSafeCache()
