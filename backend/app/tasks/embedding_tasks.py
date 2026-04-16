import logging
from app.tasks.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.embedding_tasks.generate_embedding", queue="embeddings", bind=True, max_retries=3)
def generate_embedding(self, profile_id: str) -> dict:
    """Generate and upsert embedding for a BusinessProfile into Qdrant."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy import select

    async def _run():
        from app.models.profile import BusinessProfile
        from app.services.embedding_service import build_embedding_text, get_embedding

        engine = create_async_engine(settings.DATABASE_URL)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)

        async with session_factory() as session:
            result = await session.execute(select(BusinessProfile).where(BusinessProfile.id == profile_id))
            profile = result.scalar_one_or_none()
            if not profile:
                logger.error(f"Profile {profile_id} not found")
                return {"status": "not_found"}

            text = build_embedding_text(profile)
            vector = get_embedding(text)
            if not vector:
                logger.error(f"Empty embedding for profile {profile_id}")
                return {"status": "embedding_failed"}

            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import PointStruct

                client = QdrantClient(url=settings.QDRANT_URL)
                # Ensure collection exists
                try:
                    client.get_collection(settings.QDRANT_COLLECTION)
                except Exception:
                    from qdrant_client.models import VectorParams, Distance
                    client.create_collection(
                        collection_name=settings.QDRANT_COLLECTION,
                        vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE),
                    )

                point = PointStruct(
                    id=profile_id,
                    vector=vector,
                    payload={
                        "profile_id": str(profile.id),
                        "user_id": str(profile.user_id),
                        "role": profile.role,
                        "operating_regions": profile.operating_regions or [],
                        "willing_cross_border": profile.willing_cross_border or False,
                        "annual_revenue_range": profile.annual_revenue_range,
                        "embedding_model_version": settings.EMBEDDING_MODEL_VERSION,
                        "demo": profile.demo,
                        "company_name": profile.company_name,
                        "industry_sector": profile.industry_sector,
                    },
                )
                client.upsert(collection_name=settings.QDRANT_COLLECTION, points=[point])
                logger.info(f"Upserted embedding for profile {profile_id}")

                profile.embedding_generated = True
                await session.commit()
                return {"status": "ok", "profile_id": profile_id}
            except Exception as e:
                logger.error(f"Qdrant upsert failed for {profile_id}: {e}")
                try:
                    self.retry(exc=e, countdown=60)
                except Exception:
                    pass
                return {"status": "error", "error": str(e)}

        await engine.dispose()

    return asyncio.run(_run())
