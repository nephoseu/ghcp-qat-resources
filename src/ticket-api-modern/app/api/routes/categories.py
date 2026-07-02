from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.models import Category, User
from app.db.session import get_db

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    sla_hours: int = 48


class CategoryOut(BaseModel):
    id: int
    name: str
    sla_hours: int

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CategoryOut])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Category).order_by(Category.name).all()


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(Category).filter(Category.name == body.name).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(name=body.name, sla_hours=body.sla_hours)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
