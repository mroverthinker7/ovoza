from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os
from config import DB_URL
from .models import Base, User, Admin, Group, Request, Review

# Keep config.py unchanged. Local default remains SQLite; production can provide
# DATABASE_URL (for example Render PostgreSQL) as an environment variable.
DATABASE_URL = os.getenv("DATABASE_URL", DB_URL)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgres://"): ]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgresql://"): ]

engine = create_async_engine(DATABASE_URL, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def upsert_user(tg_id: int, language: str | None = None):
    async with Session() as s:
        user = await s.scalar(select(User).where(User.telegram_id == tg_id))
        if not user:
            user = User(telegram_id=tg_id, language=language or "uz")
            s.add(user)
        elif language:
            user.language = language
        await s.commit()

async def get_user_lang(tg_id: int) -> str:
    async with Session() as s:
        user = await s.scalar(select(User).where(User.telegram_id == tg_id))
        return user.language if user else "uz"

async def get_user_by_tg(tg_id: int):
    async with Session() as s:
        return await s.scalar(select(User).where(User.telegram_id == tg_id))

async def is_db_admin(tg_id: int) -> bool:
    async with Session() as s:
        return await s.scalar(select(Admin.id).where(Admin.telegram_id == tg_id)) is not None

async def add_admin(tg_id: int):
    async with Session() as s:
        exists = await s.scalar(select(Admin.id).where(Admin.telegram_id == tg_id))
        if not exists:
            s.add(Admin(telegram_id=tg_id))
            await s.commit()

async def count_groups() -> int:
    async with Session() as s:
        return int(await s.scalar(select(func.count(Group.id))) or 0)

async def create_request(user_tg_id: int, group_id: int):
    async with Session() as s:
        user = await s.scalar(select(User).where(User.telegram_id == user_tg_id))
        if not user:
            user = User(telegram_id=user_tg_id, language="uz")
            s.add(user)
            await s.flush()
        active = await s.scalar(select(Request).where(Request.user_id == user.id, Request.group_id == group_id, Request.status == "pending"))
        if active:
            return active, False
        req = Request(user_id=user.id, group_id=group_id, status="pending")
        s.add(req)
        await s.commit()
        await s.refresh(req)
        return req, True

async def get_pending_requests():
    async with Session() as s:
        stmt = select(Request).where(Request.status == "pending").order_by(Request.created_at.asc())
        return list((await s.scalars(stmt)).all())

async def complete_request(request_id: int):
    async with Session() as s:
        req = await s.get(Request, request_id)
        if not req or req.status != "pending":
            return None
        req.status = "completed"
        req.completed_at = datetime.utcnow()
        await s.commit()
        await s.refresh(req)
        return req

async def create_review(request_id: int, rating: int, comment: str | None = None):
    async with Session() as s:
        req = await s.scalar(select(Request).where(Request.id == request_id))
        if not req or req.status != "completed":
            return None
        existing = await s.scalar(select(Review).where(Review.request_id == request_id))
        if existing:
            return None
        review = Review(request_id=request_id, user_id=req.user_id, group_id=req.group_id, rating=rating, comment=comment)
        s.add(review)
        group = await s.get(Group, req.group_id)
        if group:
            old_count = int(group.reviews_count or 0)
            old_rating = float(group.rating or 0.0)
            group.reviews_count = old_count + 1
            group.rating = ((old_rating * old_count) + rating) / group.reviews_count if group.reviews_count else float(rating)
        await s.commit()
        return review
