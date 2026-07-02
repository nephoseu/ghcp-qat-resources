from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Category, Comment, Ticket, User
from app.db.session import get_db

router = APIRouter()


class TicketCreate(BaseModel):
    title: str
    description: str
    severity: str = "medium"
    category_id: int


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    category_id: int

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    body: str


class CommentOut(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: datetime

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str


def _get_owned_ticket(ticket_id: int, current_user: User, db: Session) -> Ticket:
    """Fetch a ticket and enforce owner-only access (404 if missing, 403 if not yours)."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")
    return ticket


def _get_accessible_ticket(ticket_id: int, current_user: User, db: Session) -> Ticket:
    """Fetch a ticket accessible to its owner or an admin (404 if missing, 403 otherwise)."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not your ticket")
    return ticket


@router.get("/", response_model=list[TicketOut])
def list_tickets(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Oldest-first, paginated: preserves TaskDesk Classic ordering for backwards compatibility.
    return (
        db.query(Ticket)
        .filter(Ticket.user_id == current_user.id)
        .order_by(Ticket.created_at.asc(), Ticket.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/search", response_model=list[TicketOut])
def search_tickets(
    q: Optional[str] = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Ticket)
        .filter(Ticket.user_id == current_user.id, Ticket.title.ilike(f"%{q}%"))
        .all()
    )


@router.post("/", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    body: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.severity not in Ticket.SEVERITY_CHOICES:
        raise HTTPException(status_code=400, detail=f"severity must be one of {Ticket.SEVERITY_CHOICES}")
    category = db.query(Category).filter(Category.id == body.category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    ticket = Ticket(
        user_id=current_user.id,
        category_id=body.category_id,
        title=body.title,
        description=body.description,
        severity=body.severity,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_owned_ticket(ticket_id, current_user, db)
    db.delete(ticket)
    db.commit()


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_ticket_status(
    ticket_id: int,
    body: StatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_owned_ticket(ticket_id, current_user, db)
    if body.status not in Ticket.STATUS_CHOICES:
        raise HTTPException(status_code=400, detail=f"status must be one of {Ticket.STATUS_CHOICES}")
    if (ticket.status, body.status) not in Ticket.ALLOWED_STATUS_TRANSITIONS:
        raise HTTPException(
            status_code=409,
            detail=f"cannot transition from {ticket.status!r} to {body.status!r}",
        )
    if body.status == "resolved":
        has_comment = db.query(Comment).filter(Comment.ticket_id == ticket.id).first() is not None
        if not has_comment:
            raise HTTPException(
                status_code=409,
                detail="resolving a ticket requires at least one comment (resolution note)",
            )
    ticket.status = body.status
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    ticket_id: int,
    body: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_accessible_ticket(ticket_id, current_user, db)
    comment = Comment(ticket_id=ticket.id, author_id=current_user.id, body=body.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{ticket_id}/comments", response_model=list[CommentOut])
def list_comments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = _get_accessible_ticket(ticket_id, current_user, db)
    return (
        db.query(Comment)
        .filter(Comment.ticket_id == ticket.id)
        .order_by(Comment.created_at.asc())
        .all()
    )
