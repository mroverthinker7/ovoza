from sqlalchemy import select
from database.db import Session
from database.models import Group, Service
from services.catalog import SERVICES, DISTRICTS

# The database stores the exact localized catalog names, including emoji.
# Keep the mapping exact so service filters match records created by the admin wizard.
SERVICE_MAP = {key: uz for key, uz, _ in SERVICES}
REGION_MAP = {key: uz for key, uz, _ in DISTRICTS}

async def find_groups(filters: dict):
    async with Session() as s:
        stmt = (
            select(Group)
            .join(Service, isouter=True)
            .distinct()
            .where(
                Group.price_to >= filters.get("min_price", 0),
                Group.price_from <= filters.get("max_price", 10**12),
                Group.rating >= filters.get("rating", 0),
            )
        )

        region_key = filters.get("region")
        if region_key:
            region = REGION_MAP.get(region_key, region_key)
            stmt = stmt.where(Group.region_uz == region)

        service_key = filters.get("service")
        if service_key:
            service = SERVICE_MAP.get(service_key, service_key)
            stmt = stmt.where(Service.name_uz == service)

        stmt = stmt.order_by(Group.rating.desc(), Group.reviews_count.desc(), Group.id.desc())
        result = await s.scalars(stmt)
        return list(result.unique().all())
