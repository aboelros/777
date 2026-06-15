from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_auth_db, get_db
from app.core.security import get_password_hash, require_role
from app.db.models import User, UserRole, Order, Message, MessageDirection

router = APIRouter(dependencies=[Depends(require_role("admin"))])


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=100)


class UserListItem(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/users", response_model=List[UserListItem])
async def list_users(
    q: Optional[str] = Query(None, description="Search by email or name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_auth_db),
) -> Any:
    query = select(User)
    if q:
        like = f"%{q.lower()}%"
        query = query.where((User.email.ilike(like)) | (User.name.ilike(like)))
    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/users", response_model=UserListItem, status_code=status.HTTP_201_CREATED)
async def create_user(payload: AdminUserCreate, db: AsyncSession = Depends(get_auth_db)) -> Any:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        name=payload.name,
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserListItem)
async def update_user(user_id: UUID, payload: AdminUserUpdate, db: AsyncSession = Depends(get_auth_db)) -> Any:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(user_id: UUID, payload: ResetPasswordRequest, db: AsyncSession = Depends(get_auth_db)) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = get_password_hash(payload.new_password)
    await db.commit()
    return None


class UsageSummaryResponse(BaseModel):
    from_date: datetime
    to_date: datetime
    total_messages: int
    outbound_messages: int
    inbound_messages: int
    total_orders: int


@router.get("/usage/summary", response_model=UsageSummaryResponse)
async def usage_summary(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
) -> Any:
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    messages_result = await db.execute(
        select(Message).where(Message.created_at >= start).where(Message.created_at <= end)
    )
    messages = messages_result.scalars().all()
    total_messages = len(messages)
    inbound = sum(1 for m in messages if m.direction == MessageDirection.INBOUND)
    outbound = sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND)

    orders_result = await db.execute(
        select(Order).where(Order.order_date >= start).where(Order.order_date <= end)
    )
    orders = orders_result.scalars().all()

    return UsageSummaryResponse(
        from_date=start,
        to_date=end,
        total_messages=total_messages,
        outbound_messages=outbound,
        inbound_messages=inbound,
        total_orders=len(orders),
    )


class HealthResponse(BaseModel):
    database: str
    redis: str
    time: float


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> Any:
    _ = await db.execute(select(Order).limit(1))
    return HealthResponse(database="ok", redis="unknown", time=datetime.utcnow().timestamp())
