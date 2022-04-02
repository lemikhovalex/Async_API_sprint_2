import asyncio
import json
from codecs import ignore_errors
from http import HTTPStatus
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from test_data import constants

from .settings import TestSettings

SETTINGS = TestSettings()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="session")
async def es_connection() -> AsyncGenerator[AsyncElasticsearch, None]:
    """
    Создаёт файл и удаляет его, даже если сам тест упал в ошибку
    """
    url = f"http://{SETTINGS.es_host}:{SETTINGS.es_port}"
    es = AsyncElasticsearch(url)
    yield es

    await es.close()


@pytest_asyncio.fixture(scope="session")
async def filled_es(
    es_connection: AsyncElasticsearch,
) -> AsyncGenerator[AsyncElasticsearch, None]:
    await asyncio.gather(
        *[
            fill_es_index(es=es_connection, index=idx)
            for idx in [
                "genres",
                "persons",
                "movies",
            ]
        ]
    )

    yield es_connection


async def fill_es_index(es: AsyncElasticsearch, index: str):
    await es.indices.create(
        index=index,
        settings=constants.settings,
        mappings=getattr(constants, f"mappings_{index}"),
        ignore=HTTPStatus.BAD_REQUEST,
    )
    with open(f"test_data/{index}.json", "r") as f:
        data = json.load(f)
    actions = [
        {"_index": index, "_id": datum["id"], "_source": datum} for datum in data
    ]
    await async_bulk(client=es, actions=actions)
    await asyncio.sleep(5)
    return
