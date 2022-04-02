import asyncio
import json
from http import HTTPStatus
from typing import AsyncGenerator, List

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
    indecies = ["genres", "persons", "movies"]
    actions = []
    for idx in indecies:
        await es_connection.indices.create(
            index=idx,
            settings=constants.settings,
            mappings=getattr(constants, f"mappings_{idx}"),
            ignore=HTTPStatus.BAD_REQUEST,
        )
        actions.extend(actions_for_es_bulk(idx))
    await asyncio.sleep(5)
    await async_bulk(client=es_connection, actions=actions)

    yield es_connection

    for idx in indecies:
        es_connection.indices.delete(
            index=idx,
            ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND],
        )


def actions_for_es_bulk(index: str) -> List[dict]:

    with open(f"test_data/{index}.json", "r") as f:
        data = json.load(f)
    return [{"_index": index, "_id": datum["id"], "_source": datum} for datum in data]
