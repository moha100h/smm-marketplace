"""Services & Panels API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.panel import Panel, Category, SubCategory, Service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/services", tags=["services"])


class ServiceItem(BaseModel):
    id: int
    name: str
    name_en: Optional[str]
    price: int
    min_quantity: int
    max_quantity: int
    description: Optional[str]
    delivery_time: Optional[str]

    class Config:
        from_attributes = True


class CategoryItem(BaseModel):
    id: int
    name: str
    name_en: Optional[str]
    services: List[ServiceItem] = []

    class Config:
        from_attributes = True


class PanelItem(BaseModel):
    id: int
    name: str
    name_en: Optional[str]
    slug: str
    categories: List[CategoryItem] = []

    class Config:
        from_attributes = True


@router.get("/panels", response_model=List[PanelItem])
async def get_panels(db: AsyncSession = Depends(get_db)):
    """Get all active panels with categories and services."""
    stmt = (
        select(Panel)
        .where(Panel.is_active == True)
        .order_by(Panel.sort_order)
    )
    result = await db.execute(stmt)
    panels = result.scalars().all()
    return panels


@router.get("/panels/{panel_slug}")
async def get_panel(panel_slug: str, db: AsyncSession = Depends(get_db)):
    """Get single panel with full hierarchy."""
    stmt = select(Panel).where(Panel.slug == panel_slug, Panel.is_active == True)
    result = await db.execute(stmt)
    panel = result.scalar_one_or_none()
    if not panel:
        return {"error": "Panel not found"}
    return panel
