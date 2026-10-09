from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, FrozenSet, List

@dataclass(frozen=True)
class TenantContext:
    """
    Represents an explicitly authorized tenant scope for a given request or task.
    
    This context is the ONLY permitted way to pass a `project_id` into the repository layer.
    It guarantees that the caller (user_id) has been verified against the project membership,
    preventing raw UUID strings from bypassing authorization checks.
    """
    project_id: UUID
    user_id: Optional[UUID] = None
    role: str = "member"
    roles: Optional[List[str]] = None
    permissions: FrozenSet[str] = field(default_factory=frozenset)
    membership_id: Optional[UUID] = None

    def __post_init__(self):
        if self.roles and self.role == "member":
            object.__setattr__(self, "role", self.roles[0])

@dataclass(frozen=True)
class ServiceContext:
    """
    Represents a trusted internal service operation executing on behalf of a tenant.
    
    For background tasks (e.g. Celery) and webhooks. This bypasses user membership checks
    but must still restrict data access to the explicit `project_id` scope.
    """
    service_name: str
    project_id: UUID
    operation: str
