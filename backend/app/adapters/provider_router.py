"""Provider router — selects best provider for an order."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.provider import Provider, ProviderStatus, ServiceProviderMapping
from app.adapters.smm_api import SMMApiAdapter


class ProviderRouter:
    """Routes orders to the best available provider."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_providers_for_service(self, service_id: int) -> List[ServiceProviderMapping]:
        """Get all active provider mappings for a service, ordered by priority."""
        stmt = (
            select(ServiceProviderMapping)
            .join(Provider, Provider.id == ServiceProviderMapping.provider_id)
            .where(
                ServiceProviderMapping.service_id == service_id,
                ServiceProviderMapping.is_active == True,
                Provider.status == ProviderStatus.ACTIVE,
            )
            .order_by(ServiceProviderMapping.priority.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def route_order(self, service_id: int) -> Optional[ServiceProviderMapping]:
        """Select the best provider for a service."""
        mappings = await self.get_providers_for_service(service_id)
        return mappings[0] if mappings else None

    async def get_adapter(self, mapping: ServiceProviderMapping) -> SMMApiAdapter:
        """Create an adapter for a provider mapping."""
        provider = await self.session.get(Provider, mapping.provider_id)
        return SMMApiAdapter(provider.api_url, provider.api_key)
