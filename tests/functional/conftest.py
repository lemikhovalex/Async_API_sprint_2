import asyncio
import os
import sys
from dataclasses import dataclass
from http import HTTPStatus
from typing import AsyncGenerator, Optional

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .settings import TestSettings
from .test_data import constants

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

SETTINGS = TestSettings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    """
    Создаёт файл и удаляет его, даже если сам тест упал в ошибку
    """
    url = f"http://{SETTINGS.es_host}:{SETTINGS.es_port}"
    es = AsyncElasticsearch(url)
    indecies = ["genres", "persons", "movies"]
    await asyncio.gather(
        *[
            es.indices.create(
                index=idx,
                settings=constants.settings,
                mappings=getattr(constants, f"mappings_{idx}"),
                ignore=HTTPStatus.BAD_REQUEST,
            )
            for idx in indecies
        ]
    )

    yield es

    await asyncio.gather(
        *[
            es.indices.delete(
                index=idx,
                ignore=[HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND],
            )
            for idx in indecies
        ]
    )

    await es.close()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest_asyncio.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession(headers={"Cache-Control": "no-cache, no-store"})
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
