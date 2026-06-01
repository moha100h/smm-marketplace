"""Order API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.repositories.order_repo import OrderRepository
from app.services.order_service import OrderService
from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderCreate(BaseModel):
    user_id: int
    service_id: int
    quantity: int
    price_per_1000: int
    form_data: str


class OrderResponse(BaseModel):
    id: int
    status: str
    quantity: int
    total_cost: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=OrderResponse)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    service = OrderService(db)
    order = await service.create_order(
        user_id=data.user_id,
        service_id=data.service_id,
        quantity=data.quantity,
        price_per_1000=data.price_per_1000,
        form_data=data.form_data,
    )
    return order


@router.get("/user/{tg_id}")
async def get_user_orders(tg_id: int, skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    repo = OrderRepository(db)
    orders = await repo.get_user_orders(tg_id, skip, limit)
    return orders
