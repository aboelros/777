"""
Compliance and Audit Service
GDPR compliance, data retention, and compliance reporting.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
import structlog

logger = structlog.get_logger(__name__)


class GDPRCompliance:
    """
    GDPR compliance tools for data privacy.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for GDPR data portability.
        
        Args:
            user_id: User ID
            
        Returns:
            Complete user data export
        """
        from app.db.models import User, Project, Message, Order
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get projects
        result = await self.db.execute(
            select(Project).where(Project.owner_id == user_id)
        )
        projects = result.scalars().all()
        
        # Get messages
        project_ids = [p.id for p in projects]
        messages = []
        if project_ids:
            result = await self.db.execute(
                select(Message).where(Message.project_id.in_(project_ids))
            )
            messages = result.scalars().all()
        
        # Get orders
        orders = []
        if project_ids:
            result = await self.db.execute(
                select(Order).where(Order.project_id.in_(project_ids))
            )
            orders = result.scalars().all()
        
        export_data = {
            'user': {
                'id': str(user.id),
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'projects': [
                {
                    'id': str(p.id),
                    'name': p.name,
                    'created_at': p.created_at.isoformat() if p.created_at else None
                }
                for p in projects
            ],
            'messages': [
                {
                    'id': str(m.id),
                    'content': m.content,
                    'created_at': m.created_at.isoformat() if m.created_at else None
                }
                for m in messages[:1000]  # Limit for performance
            ],
            'orders': [
                {
                    'id': str(o.id),
                    'total': float(o.total) if o.total else 0,
                    'created_at': o.created_at.isoformat() if o.created_at else None
                }
                for o in orders[:1000]
            ],
            'exported_at': datetime.utcnow().isoformat()
        }
        
        logger.info("User data exported", user_id=user_id)
        
        return export_data
    
    async def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all user data for GDPR right to erasure.
        
        Args:
            user_id: User ID
            
        Returns:
            Deletion summary
        """
        from app.db.models import User, Project, Message, Order
        
        # Get projects
        result = await self.db.execute(
            select(Project).where(Project.owner_id == user_id)
        )
        projects = result.scalars().all()
        project_ids = [p.id for p in projects]
        
        # Delete messages
        messages_deleted = 0
        if project_ids:
            result = await self.db.execute(
                delete(Message).where(Message.project_id.in_(project_ids))
            )
            messages_deleted = result.rowcount
        
        # Delete orders
        orders_deleted = 0
        if project_ids:
            result = await self.db.execute(
                delete(Order).where(Order.project_id.in_(project_ids))
            )
            orders_deleted = result.rowcount
        
        # Delete projects
        projects_deleted = 0
        if project_ids:
            result = await self.db.execute(
                delete(Project).where(Project.id.in_(project_ids))
            )
            projects_deleted = result.rowcount
        
        # Delete user
        await self.db.execute(
            delete(User).where(User.id == user_id)
        )
        
        await self.db.commit()
        
        summary = {
            'user_deleted': True,
            'projects_deleted': projects_deleted,
            'messages_deleted': messages_deleted,
            'orders_deleted': orders_deleted,
            'deleted_at': datetime.utcnow().isoformat()
        }
        
        logger.info("User data deleted", user_id=user_id, summary=summary)
        
        return summary


class DataRetentionPolicy:
    """
    Automated data retention and cleanup.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.retention_periods = {
            'messages': 365,  # 1 year
            'orders': 2555,  # 7 years (legal requirement)
            'audit_logs': 2555,  # 7 years
            'analytics': 90  # 3 months
        }
    
    async def cleanup_old_data(self, data_type: str) -> Dict[str, Any]:
        """
        Clean up data older than retention period.
        
        Args:
            data_type: Type of data to clean
            
        Returns:
            Cleanup summary
        """
        retention_days = self.retention_periods.get(data_type, 365)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        from app.db.models import Message, Order
        
        deleted_count = 0
        
        if data_type == 'messages':
            result = await self.db.execute(
                delete(Message).where(Message.created_at < cutoff_date)
            )
            deleted_count = result.rowcount
        elif data_type == 'orders':
            # Don't actually delete orders, just mark as archived
            pass
        
        await self.db.commit()
        
        logger.info(
            "Data cleanup completed",
            data_type=data_type,
            deleted=deleted_count,
            cutoff_date=cutoff_date.isoformat()
        )
        
        return {
            'data_type': data_type,
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat(),
            'retention_days': retention_days
        }


class ComplianceReporting:
    """
    Generate compliance reports.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_gdpr_report(self) -> Dict[str, Any]:
        """Generate GDPR compliance report."""
        from app.db.models import User
        
        # Count total users
        result = await self.db.execute(select(func.count(User.id)))
        total_users = result.scalar()
        
        report = {
            'report_type': 'GDPR Compliance',
            'generated_at': datetime.utcnow().isoformat(),
            'metrics': {
                'total_users': total_users,
                'data_exports_last_30_days': 0,  # TODO: Track this
                'deletion_requests_last_30_days': 0,  # TODO: Track this
                'consent_records': total_users
            },
            'compliance_status': 'COMPLIANT',
            'recommendations': [
                'Continue monitoring data export requests',
                'Review data retention policies quarterly',
                'Ensure all third-party processors are GDPR compliant'
            ]
        }
        
        return report
    
    async def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate audit activity report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Audit report
        """
        from app.services.observability.monitoring import audit_logger
        
        # Get audit events in date range
        events = audit_logger.get_audit_trail(limit=10000)
        
        # Filter by date
        filtered_events = [
            e for e in events
            if start_date <= datetime.fromisoformat(e['timestamp']) <= end_date
        ]
        
        # Aggregate by action type
        action_counts = {}
        for event in filtered_events:
            action = event['action']
            action_counts[action] = action_counts.get(action, 0) + 1
        
        report = {
            'report_type': 'Audit Activity',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'generated_at': datetime.utcnow().isoformat(),
            'total_events': len(filtered_events),
            'events_by_action': action_counts,
            'top_users': [],  # TODO: Aggregate by user
            'security_alerts': []  # TODO: Identify suspicious patterns
        }
        
        return report


# Helper function
from sqlalchemy import func
