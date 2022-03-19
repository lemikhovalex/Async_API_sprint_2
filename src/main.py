import logging

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import films
from core import config
from core.logger import LOGGING
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    """
    Подключаемся к базам при старте сервера
    Подключиться можем при работающем event-loop
    Поэтому логика подключения происходит в асинхронной функции
    """
    # todo real db must be added so no try
    try:
        redis.redis = await aioredis.create_redis_pool(
            (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
        )
        elastic.es = AsyncElasticsearch(
            hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
        )
    except ConnectionRefusedError:
        pass


@app.on_event("shutdown")
async def shutdown():
    """
    Отключаемся от баз при выключении сервера
    """
    # todo real databases with no if
    if redis.redis is not None:
        await redis.redis.close()
    if elastic.es is not None:
        await elastic.es.close()


app.include_router(films.router, prefix="/api/v1/films", tags=["film"])
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
