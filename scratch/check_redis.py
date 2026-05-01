import asyncio
import redis.asyncio as aioredis
from app.core.config import settings

async def check_otp():
    url = settings.REDIS_URL
    print(f"Connecting to {url}")
    r = aioredis.from_url(url, decode_responses=True)
    keys = await r.keys("otp:*")
    print(f"OTP Keys found: {keys}")
    for k in keys:
        val = await r.get(k)
        ttl = await r.ttl(k)
        print(f"Key: {k}, Value: {val}, TTL: {ttl}s")

if __name__ == "__main__":
    asyncio.run(check_otp())
