"""
Seed demo data script for Qasyp App.
Creates 20 demo business profiles (10 Buyers + 10 Suppliers across 5 industries).

Usage:
    python scripts/seed_demo_data.py
    docker compose exec api python scripts/seed_demo_data.py
"""

import asyncio
import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def seed():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy import select, delete
    from app.core.config import settings
    from app.models.user import User
    from app.models.profile import BusinessProfile

    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    data_path = Path(__file__).parent.parent / "app" / "data" / "demo_profiles.json"
    with open(data_path) as f:
        profiles_data = json.load(f)

    async with session_factory() as session:
        # Delete existing demo data (idempotent)
        existing_users = await session.execute(
            select(User).where(User.email.like("demo-%@qasyp.demo"))
        )
        for user in existing_users.scalars():
            await session.execute(
                delete(BusinessProfile).where(BusinessProfile.user_id == user.id)
            )
        await session.execute(
            delete(User).where(User.email.like("demo-%@qasyp.demo"))
        )
        await session.commit()
        logger.info("Cleared existing demo data")

        created = 0
        for p in profiles_data:
            user = User(
                email=f"demo-{p['id']}@qasyp.demo",
                hashed_password="demo-no-login",
                role=p["role"].lower(),
                tier="free",
                is_active=True,
                profile_submitted=True,
            )
            session.add(user)
            await session.flush()

            profile = BusinessProfile(
                user_id=user.id,
                company_name=p["company_name"],
                bin=p["bin"],
                legal_entity_type=p["legal_entity_type"],
                vat_registered=p["vat_registered"],
                vat_certificate_number=p.get("vat_certificate_number"),
                industry_sector=p["industry_sector"],
                business_scope=p["business_scope"],
                role=p["role"],
                products_services=p.get("products_services"),
                volume_requirements=p.get("volume_requirements"),
                frequency=p.get("frequency"),
                quality_standards=p.get("quality_standards"),
                annual_revenue_range=p.get("annual_revenue_range"),
                growth_target=p.get("growth_target"),
                operating_regions=p.get("operating_regions"),
                willing_cross_border=p.get("willing_cross_border", False),
                preferred_partner_profile=p.get("preferred_partner_profile"),
                exclusion_criteria=p.get("exclusion_criteria"),
                demo=True,
                embedding_generated=False,
            )
            session.add(profile)
            created += 1

        await session.commit()
        logger.info(f"Created {created} demo profiles")

    # Dispatch embedding tasks
    try:
        from app.tasks.embedding_tasks import generate_embedding
        async with session_factory() as session:
            result = await session.execute(
                select(BusinessProfile).where(BusinessProfile.demo.is_(True))
            )
            dispatched = 0
            for profile in result.scalars():
                generate_embedding.delay(str(profile.id))
                dispatched += 1
        logger.info(f"Dispatched {dispatched} embedding tasks")
    except Exception as e:
        logger.warning(f"Could not dispatch embedding tasks: {e}")

    await engine.dispose()
    print(f"\n✓ Seeded {created} demo profiles successfully")
    print("  Run the Celery worker to process embeddings:")
    print("  docker compose exec celery_worker celery -A app.tasks.celery_app worker -l info")


if __name__ == "__main__":
    asyncio.run(seed())
