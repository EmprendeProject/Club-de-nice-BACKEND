import json
import logging
from typing import Any, Optional

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


def cache_get(key: str) -> Optional[Any]:
    """Devuelve el valor cacheado (deserializado de JSON) o None si no hay caché/Redis."""
    redis_client = get_redis()
    if redis_client is None:
        return None

    try:
        raw = redis_client.get(key)
    except Exception as exc:
        logger.warning("[cache.get] FAILED key=%s [%s] %s", key, type(exc).__name__, str(exc))
        return None

    if raw is None:
        return None

    try:
        return json.loads(raw)
    except ValueError:
        logger.warning("[cache.get] invalid JSON for key=%s", key)
        return None


def cache_set(key: str, value: Any, ttl_seconds: int) -> None:
    """Guarda `value` (serializado a JSON) en Redis con expiración. No-op si Redis no está disponible."""
    redis_client = get_redis()
    if redis_client is None:
        return

    try:
        redis_client.set(key, json.dumps(value), ex=ttl_seconds)
    except Exception as exc:
        logger.warning("[cache.set] FAILED key=%s [%s] %s", key, type(exc).__name__, str(exc))


def cache_delete(*keys: str) -> None:
    """Invalida una o más claves de caché. No-op si Redis no está disponible."""
    redis_client = get_redis()
    if redis_client is None or not keys:
        return

    try:
        redis_client.delete(*keys)
    except Exception as exc:
        logger.warning("[cache.delete] FAILED keys=%s [%s] %s", keys, type(exc).__name__, str(exc))


def cache_delete_pattern(pattern: str) -> None:
    """Invalida todas las claves que matcheen `pattern` (p.ej. "analytics:history:*")."""
    redis_client = get_redis()
    if redis_client is None:
        return

    try:
        keys = list(redis_client.scan_iter(match=pattern))
        if keys:
            redis_client.delete(*keys)
    except Exception as exc:
        logger.warning("[cache.delete_pattern] FAILED pattern=%s [%s] %s", pattern, type(exc).__name__, str(exc))
