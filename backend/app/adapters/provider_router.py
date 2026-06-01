"""Smart Provider Router & Failover System."""
from typing import Dict, Any, List, Optional
from app.adapters.base import BaseProviderAdapter
from app.adapters.smm_api import SMMApiAdapter
from app.models.provider import Provider, ServiceProviderMapping
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ProviderRouter:
    """Routes orders to best available provider with failover support."""

    def __init__(self):
        self._adapters: Dict[int, BaseProviderAdapter] = {}

    def get_adapter(self, provider: Provider) -> BaseProviderAdapter:
        if provider.id not in self._adapters:
            self._adapters[provider.id] = SMMApiAdapter(
                api_url=provider.api_url,
                api_key=provider.api_key,
            )
        return self._adapters[provider.id]

    async def route_order(
        self,
        service_id: int,
        mappings: List[ServiceProviderMapping],
        providers: List[Provider],
        link: str,
        quantity: int,
    ) -> Dict[str, Any]:
        """Try providers in priority order with failover."""
        # Sort by priority (lower number = higher priority)
        sorted_providers = sorted(providers, key=lambda p: p.priority)

        for provider in sorted_providers:
            if provider.status.value != "active":
                continue

            mapping = next((m for m in mappings if m.provider_id == provider.id), None)
            if not mapping or not mapping.is_active:
                continue

            try:
                adapter = self.get_adapter(provider)
                result = await adapter.add_order(
                    service_id=mapping.provider_service_id,
                    link=link,
                    quantity=quantity,
                )

                if "error" not in result:
                    return {
                        "success": True,
                        "provider_id": provider.id,
                        "provider_order_ref": result.get("order"),
                        "result": result,
                    }
                else:
                    logger.warning(f"Provider {provider.id} failed: {result['error']}")
            except Exception as e:
                logger.error(f"Provider {provider.id} exception: {e}")

        return {"success": False, "error": "All providers failed"}


# Global router instance
provider_router = ProviderRouter()
