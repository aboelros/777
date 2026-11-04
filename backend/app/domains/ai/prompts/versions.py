from typing import Dict, List, Optional
from uuid import UUID
import hashlib
import json
from .models import TenantPromptConfig, PromptVersionInfo


class PromptRegistry:
    """
    In-memory and persistent version registry for tenant prompt configurations.
    Enforces deterministic SHA-256 fingerprinting and rollback support.
    """

    def __init__(self):
        # project_id -> list of PromptVersionInfo
        self._history: Dict[UUID, List[PromptVersionInfo]] = {}
        # project_id -> {version_str: TenantPromptConfig}
        self._configs: Dict[UUID, Dict[str, TenantPromptConfig]] = {}

    @staticmethod
    def compute_hash(config: TenantPromptConfig) -> str:
        """Compute deterministic SHA-256 fingerprint for a prompt configuration."""
        raw_dict = config.model_dump(exclude={"version"})
        serialized = json.dumps(raw_dict, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def register_version(
        self,
        config: TenantPromptConfig,
        activate: bool = True
    ) -> PromptVersionInfo:
        """
        Register a new prompt configuration version for a tenant.
        Prevents silent in-place regressions.
        """
        project_id = config.project_id
        sha256 = self.compute_hash(config)
        version_str = config.version

        if project_id not in self._history:
            self._history[project_id] = []
            self._configs[project_id] = {}

        # Deactivate previous versions if this one is activated
        if activate:
            for item in self._history[project_id]:
                item.is_active = False

        version_info = PromptVersionInfo(
            version=version_str,
            sha256_hash=sha256,
            project_id=project_id,
            is_active=activate
        )

        self._history[project_id].append(version_info)
        self._configs[project_id][version_str] = config
        return version_info

    def get_active_config(self, project_id: UUID) -> Optional[TenantPromptConfig]:
        """Retrieve the currently active configuration for a tenant."""
        versions = self._history.get(project_id, [])
        for v in reversed(versions):
            if v.is_active:
                return self._configs.get(project_id, {}).get(v.version)
        return None

    def rollback(self, project_id: UUID, target_version: str) -> Optional[PromptVersionInfo]:
        """Roll back to a previously registered prompt version safely."""
        configs = self._configs.get(project_id, {})
        if target_version not in configs:
            return None

        versions = self._history.get(project_id, [])
        selected: Optional[PromptVersionInfo] = None
        for v in versions:
            if v.version == target_version:
                v.is_active = True
                selected = v
            else:
                v.is_active = False
        return selected


# Global singleton instance
prompt_registry = PromptRegistry()
