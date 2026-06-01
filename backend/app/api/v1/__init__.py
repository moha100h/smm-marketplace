"""API v1 router aggregation."""
from fastapi import APIRouter
from app.api.v1.users import router as users_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.services import router as services_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(services_router)
