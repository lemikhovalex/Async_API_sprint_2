import asyncio
import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import AsyncGenerator, List, Optional

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from multidict import CIMultiDictProxy

from .settings import TestSettings
from .test_data import constants

SETTINGS = TestSettings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def _es_connection() -> AsyncGenerator[AsyncElasticsearch, None]:
    """
    Создаёт файл и удаляет его, даже если сам тест упал в ошибку
    """
    url = f"http://{SETTINGS.es_host}:{SETTINGS.es_port}"
    es = AsyncElasticsearch(url)
    yield es

    await es.close()


@pytest_asyncio.fixture(scope="session")
async def filled_es(
    _es_connection: AsyncElasticsearch,
) -> AsyncGenerator[AsyncElasticsearch, None]:
    indecies = ["genres", "persons", "movies"]
    await asyncio.gather(
        *[
            _es_connection.indices.create(
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

    await async_bulk(client=_es_connection, actions=actions)

    await asyncio.gather(
        *[_es_connection.indices.refresh(index=idx) for idx in indecies]
    )

    yield _es_connection

    for idx in indecies:
        await _es_connection.indices.delete(
            index=idx,
            ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND],
        )
    await _es_connection.close()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest_asyncio.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def make_get_request(session):
    async def inner(method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = f"http://{SETTINGS.api_host}:{SETTINGS.api_port}/api/v1{method}"
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


def actions_for_es_bulk(index: str) -> List[dict]:

    with open(f"test_data/{index}.json", "r") as f:
        data = json.load(f)
    return [{"_index": index, "_id": datum["id"], "_source": datum} for datum in data]
