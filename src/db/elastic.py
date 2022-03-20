from typing import Optional

from core.config import ELASTIC_HOST, ELASTIC_PORT
from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = AsyncElasticsearch(
    host=ELASTIC_HOST, port=ELASTIC_PORT
)


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es
