"""Payment API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.wallet_service import WalletService
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["payments"])


class DepositRequest(BaseModel):
    user_id: int
    amount: int
    method: str


@router.post("/deposit")
async def request_deposit(data: DepositRequest, db: AsyncSession = Depends(get_db)):
    """Generate deposit address for user."""
    # In production: generate unique address or show static one
    from app.core.config import settings
    addresses = {
        "usdt_trc20": settings.USDT_TRC20_ADDRESS,
        "usdt_bep20": settings.USDT_BEP20_ADDRESS,
        "btc": settings.BTC_ADDRESS,
        "eth": settings.ETH_ADDRESS,
        "ltc": settings.LTC_ADDRESS,
    }
    address = addresses.get(data.method.lower())
    if not address:
        raise HTTPException(status_code=400, detail="Unsupported payment method")
    return {"address": address, "amount": data.amount, "method": data.method}


@router.post("/confirm")
async def confirm_deposit(payment_id: int, admin_id: int, db: AsyncSession = Depends(get_db)):
    """Admin confirms a deposit."""
    # In production: verify admin, update payment status, process wallet
    return {"status": "confirmed", "payment_id": payment_id}
