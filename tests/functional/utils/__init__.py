from typing import List

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk


async def es_load(
    es_client: AsyncElasticsearch, index: str, data: List[dict]
) -> List[dict]:
    await async_bulk(
        es_client,
        actions=[
            {"_index": index, "_id": item["id"], "_source": item} for item in data
        ],
    )
    await es_client.indices.refresh(index=index)
