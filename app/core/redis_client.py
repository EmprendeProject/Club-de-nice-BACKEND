import logging
from functools import lru_cache
from typing import Optional

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_redis() -> Optional[redis.Redis]:
    """
    Cliente Redis singleton. Devuelve None si REDIS_URL no está configurada
    o si la conexión falla — todo lo que dependa de Redis (caché, rate limiting)
    debe degradar de forma transparente cuando esto pasa.
    """
    settings = get_settings()
    if not settings.is_redis_configured():
        logger.warning("Redis NOT configured — caché y rate limiting deshabilitados")
        return None

    try:
        client = redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=2)
        client.ping()
        return client
    except Exception as exc:
        logger.warning("[redis_client.get_redis] connection FAILED [%s] %s", type(exc).__name__, str(exc))
        return None
