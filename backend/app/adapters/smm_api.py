"""SMM Panel API adapter — standard SMM panel API v2."""
import httpx
from typing import Dict, Any, Optional
from app.adapters.base import BaseProviderAdapter


class SMMApiAdapter(BaseProviderAdapter):
    """Adapter for standard SMM Panel API."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    async def _request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send POST request to SMM API."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.api_url}/api/v2",
                data={"key": self.api_key, **data},
            )
            response.raise_for_status()
            return response.json()

    async def get_balance(self) -> float:
        result = await self._request({"action": "balance"})
        return float(result.get("balance", 0))

    async def add_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        result = await self._request({
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        })
        return result

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        result = await self._request({"action": "status", "order": order_id})
        return result

    async def get_services(self) -> list:
        result = await self._request({"action": "services"})
        return result if isinstance(result, list) else []

    async def refill(self, order_id: str) -> bool:
        result = await self._request({"action": "refill", "order": order_id})
        return "refill" in result
