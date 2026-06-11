import logging
import time

from fastapi import HTTPException, Request

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


def rate_limiter(max_requests: int, window_seconds: int, prefix: str):
    """
    Dependencia de FastAPI que limita requests por IP usando una ventana fija en Redis.

    Si Redis no está configurado o falla, no limita (degrada de forma transparente).

    Usage:
        @router.post("/login", dependencies=[Depends(rate_limiter(5, 60, "login"))])
    """
    def dependency(request: Request) -> None:
        redis_client = get_redis()
        if redis_client is None:
            return

        client_ip = request.client.host if request.client else "unknown"
        window = int(time.time()) // window_seconds
        key = f"ratelimit:{prefix}:{client_ip}:{window}"

        try:
            count = redis_client.incr(key)
            if count == 1:
                redis_client.expire(key, window_seconds)
        except Exception as exc:
            logger.warning("[rate_limit.%s] FAILED [%s] %s", prefix, type(exc).__name__, str(exc))
            return

        if count > max_requests:
            logger.warning("[rate_limit.%s] BLOCKED ip=%s count=%d", prefix, client_ip, count)
            raise HTTPException(status_code=429, detail="Demasiados intentos. Intenta de nuevo más tarde.")

    return dependency
