"""Base adapter interface for SMM providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseProviderAdapter(ABC):
    """Abstract base class for SMM panel API adapters."""

    @abstractmethod
    async def get_balance(self) -> float:
        """Get provider account balance."""
        pass

    @abstractmethod
    async def add_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """Place a new order."""
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status and remaining quantity."""
        pass

    @abstractmethod
    async def get_services(self) -> list:
        """Get list of available services."""
        pass

    @abstractmethod
    async def refill(self, order_id: str) -> bool:
        """Request refill for an order."""
        pass
