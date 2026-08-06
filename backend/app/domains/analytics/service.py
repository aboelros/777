from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func

from app.core.uow import UnitOfWork
from app.domains.analytics.repository import ReportRepository, APILogRepository
from app.domains.analytics.models import Report, APILog
from app.domains.projects.repository import ProjectRepository

class AnalyticsService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _verify_project_access(self, project_id: UUID, user_id: UUID) -> Any:
        project_repo = ProjectRepository(self.uow.session)
        project = await project_repo.get(project_id)
        if not project or project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        return project

    async def list_reports(self, project_id: str, user_id: str) -> List[Report]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = ReportRepository(uow.session)
            return await repo.get_by_project(proj_uuid)

    async def get_report(self, project_id: str, report_id: str, user_id: str) -> Report:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = ReportRepository(uow.session)
            report = await repo.get(UUID(report_id))
            if not report or report.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Report not found")
            return report
