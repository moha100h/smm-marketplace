"""User API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.repositories.user_repo import UserRepository
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: int
    tg_id: int
    username: str | None
    full_name: str | None
    wallet_balance: int
    loyalty_level: str
    total_orders: int
    total_spent: int

    class Config:
        from_attributes = True


@router.get("/me/{tg_id}", response_model=UserResponse)
async def get_user(tg_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_tg_id(tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me/{tg_id}/wallet")
async def get_wallet(tg_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_tg_id(tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": user.wallet_balance, "level": user.loyalty_level.value}
