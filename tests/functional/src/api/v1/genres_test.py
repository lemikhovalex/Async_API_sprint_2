from http import HTTPStatus

import pytest
from test_data import genres, movies
from utils import es_load, filter_uuid

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


async def test_genre_by_id_absent(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    response = await make_get_request("genres/1f64e918-0000-11ec-90b3-00155db24537")
    assert response.status == HTTPStatus.NOT_FOUND


async def test_genre_by_id(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    response = await make_get_request("genres/1f64e918-b298-11ec-90b3-00155db24537")
    assert response.status == HTTPStatus.OK
    assert response.body == {
        "uuid": "1f64e918-b298-11ec-90b3-00155db24537",
        "name": "action",
    }


async def test_genres(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    response = await make_get_request("genres")
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 3


async def test_genres_empty(es_client, make_get_request):
    response = await make_get_request("genres")
    assert response.status == HTTPStatus.OK
    assert response.body == []


async def test_genres_pagination(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    response = await make_get_request("genres", {"page[size]": 2, "page[number]": 1})
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 2
    response = await make_get_request("genres", {"page[size]": 2, "page[number]": 2})
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 1


async def test_genre_films(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "genres/1f64e918-b298-11ec-90b3-00155db24537/films"
    )
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 3
    assert filter_uuid(response.body) == set(
        [
            "1f651c76-b298-11ec-90b3-00155db24537",
            "1f652f72-b298-11ec-90b3-00155db24537",
            "1f657e5a-b298-11ec-90b3-00155db24537",
        ]
    )


async def test_genre_films_pagination(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "genres/1f64e918-b298-11ec-90b3-00155db24537/films",
        {"page[size]": 2, "page[number]": 1},
    )
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 2
    response = await make_get_request(
        "genres/1f64e918-b298-11ec-90b3-00155db24537/films",
        {"page[size]": 2, "page[number]": 2},
    )
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 1
