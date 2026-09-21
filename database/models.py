from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    language: Mapped[str] = mapped_column(String(2), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    requests: Mapped[list["Request"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_uz: Mapped[str] = mapped_column(String(200))
    name_ru: Mapped[str] = mapped_column(String(200))
    description_uz: Mapped[str] = mapped_column(Text)
    description_ru: Mapped[str] = mapped_column(Text)
    region_uz: Mapped[str] = mapped_column(String(100))
    region_ru: Mapped[str] = mapped_column(String(100))
    price_from: Mapped[int] = mapped_column(Integer)
    price_to: Mapped[int] = mapped_column(Integer)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    members_count: Mapped[int] = mapped_column(Integer, default=1)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    phone: Mapped[str] = mapped_column(String(50), default="—")
    telegram: Mapped[str] = mapped_column(String(100), default="—")
    photo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requests: Mapped[list["Request"]] = relationship(back_populates="group", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="group", cascade="all, delete-orphan")
    services: Mapped[list["Service"]] = relationship(back_populates="group", cascade="all, delete-orphan", lazy="selectin")

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    name_uz: Mapped[str] = mapped_column(String(100))
    name_ru: Mapped[str] = mapped_column(String(100))
    group: Mapped[Group] = relationship(back_populates="services")

class Request(Base):
    __tablename__ = "requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user: Mapped[User] = relationship(back_populates="requests")
    group: Mapped[Group] = relationship(back_populates="requests")
    review: Mapped["Review | None"] = relationship(back_populates="request", uselist=False, cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id", ondelete="CASCADE"), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    request: Mapped[Request] = relationship(back_populates="review")
    user: Mapped[User] = relationship(back_populates="reviews")
    group: Mapped[Group] = relationship(back_populates="reviews")
    __table_args__ = (UniqueConstraint("request_id", name="uq_review_request"),)
