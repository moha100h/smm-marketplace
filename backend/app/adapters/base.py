"""Base SMM Provider Adapter — Interface for all providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseProviderAdapter(ABC):
    """Abstract base class for SMM providers.
    New providers should inherit from this and implement methods.
    """

    @abstractmethod
    async def get_balance(self) -> float:
        """Get provider account balance."""
        pass

    @abstractmethod
    async def get_services(self) -> List[Dict[str, Any]]:
        """Fetch available services from provider."""
        pass

    @abstractmethod
    async def add_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """Place a new order."""
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Check status of an order."""
        pass

    @abstractmethod
    async def refill_order(self, order_id: str) -> bool:
        """Request refill for an order."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        pass
