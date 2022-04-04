import pytest
from elasticsearch import AsyncElasticsearch


@pytest.mark.asyncio
async def test_amount_fw(filled_es: AsyncElasticsearch):
    resp = await filled_es.search(
        index="movies",
        size=50,
    )
    assert len(resp["hits"]["hits"]) == 6


@pytest.mark.asyncio
async def test_amount_persons(filled_es: AsyncElasticsearch):
    resp = await filled_es.search(
        index="persons",
        size=50,
    )
    assert len(resp["hits"]["hits"]) == 21


@pytest.mark.asyncio
async def test_amount_genres(filled_es: AsyncElasticsearch):
    resp = await filled_es.search(
        index="genres",
        size=50,
    )
    assert len(resp["hits"]["hits"]) == 3
