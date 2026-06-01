"""Standard SMM Panel API Adapter (Most common API format)."""
import httpx
from typing import Dict, Any, List, Optional
from app.adapters.base import BaseProviderAdapter
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SMMApiAdapter(BaseProviderAdapter):
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"key": self.api_key, **data}
        try:
            response = await self.client.post(self.api_url, data=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"SMM API request failed: {e}")
            return {"error": str(e)}

    async def get_balance(self) -> float:
        result = await self._request({"action": "balance"})
        return float(result.get("balance", 0))

    async def get_services(self) -> List[Dict[str, Any]]:
        result = await self._request({"action": "services"})
        if isinstance(result, list):
            return result
        return []

    async def add_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        return await self._request({
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        })

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        return await self._request({"action": "status", "order": order_id})

    async def refill_order(self, order_id: str) -> bool:
        result = await self._request({"action": "refill", "order": order_id})
        return "refill" in result or result.get("status") == "success"

    async def cancel_order(self, order_id: str) -> bool:
        result = await self._request({"action": "cancel", "order": order_id})
        return result.get("status") == "success" or "cancelled" in str(result).lower()
