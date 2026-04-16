from app.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.embedding_tasks.generate_embedding", queue="embeddings")
def generate_embedding(profile_id: str) -> dict:
    """Generate and store embedding for a business profile. Implemented by E3 subagent."""
    logger.info(f"generate_embedding task called for profile_id={profile_id}")
    return {"profile_id": profile_id, "status": "pending"}
