import logging
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(settings.EMBEDDING_MODEL_VERSION)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL_VERSION}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            _model = None
    return _model


def get_embedding(text: str) -> List[float]:
    """Generate embedding vector for text. Returns empty list on failure."""
    if not text or not text.strip():
        logger.warning("Empty text passed to get_embedding")
        return []
    try:
        model = _get_model()
        if model is None:
            raise RuntimeError("Embedding model not available")
        vector = model.encode(text, normalize_embeddings=True)
        char_count = len(text)
        logger.info(f"Generated embedding for {char_count} chars, model={settings.EMBEDDING_MODEL_VERSION}")
        return vector.tolist()
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []


def build_embedding_text(profile) -> str:
    """Concatenate profile fields for embedding per profile-schema.md strategy."""
    parts = [
        profile.business_scope or "",
        " ".join(profile.products_services or []),
        profile.industry_sector or "",
        " ".join(profile.quality_standards or []),
        profile.preferred_partner_profile or "",
        profile.growth_target or "",
    ]
    return " ".join(p for p in parts if p.strip())
