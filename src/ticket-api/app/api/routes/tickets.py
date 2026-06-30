from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.service import SearchService
from app.db.models import Ticket, User
from app.db.session import get_db

router = APIRouter()

_search_service = SearchService()


class TicketCreate(BaseModel):
    title: str
    description: str
    severity: str = "medium"


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str

    class Config:
        from_attributes = True


@router.get("/", response_model=list[TicketOut])
def list_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Ticket)
        .filter(Ticket.user_id == current_user.id)
        .order_by(Ticket.created_at.desc())
        .all()
    )


@router.get("/search", response_model=list[TicketOut])
def search_tickets(
    q: Optional[str] = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).all()
    return _search_service.search(q, tickets)


@router.post("/", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    body: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.severity not in Ticket.SEVERITY_CHOICES:
        raise HTTPException(status_code=400, detail=f"severity must be one of {Ticket.SEVERITY_CHOICES}")
    ticket = Ticket(
        user_id=current_user.id,
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
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your ticket")
    db.delete(ticket)
    db.commit()
