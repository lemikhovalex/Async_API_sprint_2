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
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
    await asyncio.gather(
        *[
            es_connection.indices.create(
                index=idx,
                settings=constants.settings,
                mappings=getattr(constants, f"mappings_{idx}"),
                ignore=HTTPStatus.BAD_REQUEST,
            )
            for idx in indecies
        ]
    )
    actions = []
    for idx in indecies:
        actions.extend(actions_for_es_bulk(idx))

    await async_bulk(client=es_connection, actions=actions)

    await asyncio.gather(
        *[es_connection.indices.refresh(index=idx) for idx in indecies]
    )

    yield es_connection

    for idx in indecies:
        await es_connection.indices.delete(
            index=idx,
            ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND],
        )
    await es_connection.close()


def actions_for_es_bulk(index: str) -> List[dict]:

    with open(f"test_data/{index}.json", "r") as f:
        data = json.load(f)
    return [{"_index": index, "_id": datum["id"], "_source": datum} for datum in data]
