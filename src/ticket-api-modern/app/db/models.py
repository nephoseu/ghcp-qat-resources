from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_admin = Column(Boolean, default=False)

    tickets = relationship("Ticket", back_populates="owner", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    sla_hours = Column(Integer, nullable=False, default=48)

    tickets = relationship("Ticket", back_populates="category")


class Ticket(Base):
    __tablename__ = "tickets"

    SEVERITY_CHOICES = ("critical", "high", "medium", "low")
    STATUS_CHOICES = ("open", "in_progress", "resolved", "closed")

    # (from_status, to_status) pairs a PATCH /tickets/{id}/status may perform.
    # Anything not listed here is a 409. Resolving additionally requires >=1 comment.
    ALLOWED_STATUS_TRANSITIONS = {
        ("open", "in_progress"),
        ("in_progress", "resolved"),
        ("resolved", "closed"),
        ("in_progress", "open"),
        ("resolved", "in_progress"),
    }

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="tickets")
    category = relationship("Category", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User")
