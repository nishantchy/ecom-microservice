from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from app.configs.config import settings
import redis.asyncio as redis

async def init_rate_limiter():
    redis_url = settings.REDIS_URL
    redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)

rate_limit = RateLimiter 