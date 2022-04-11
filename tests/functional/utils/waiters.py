import asyncio
import logging

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from settings import TestSettings

logger = logging.getLogger(__name__)
SETTINGS = TestSettings()


async def wait_for_es():
    url = f"http://{SETTINGS.es_host}:{SETTINGS.es_port}"
    es = AsyncElasticsearch(url)
    while not (await es.ping()):
        await asyncio.sleep(1)
    await es.close()


async def wait_for_redis():
    redis = Redis(host=SETTINGS.redis_host, port=SETTINGS.redis_port)
    while not (await redis.ping()):
        await asyncio.sleep(1)
    await redis.close()
