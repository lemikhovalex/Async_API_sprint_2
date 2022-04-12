from http import HTTPStatus

import pytest
from test_data import movies, persons
from utils import es_load, filter_uuid

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


async def test_person_by_id_absent(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    response = await make_get_request("persons/1f64ea08-0000-11ec-90b3-00155db24537")
    assert response.status == HTTPStatus.NOT_FOUND


async def test_person_by_id(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    response = await make_get_request("persons/1f64ea08-b298-11ec-90b3-00155db24537")
    assert response.status == HTTPStatus.OK
    assert response.body == {
        "uuid": "1f64ea08-b298-11ec-90b3-00155db24537",
        "full_name": "Multitask person 0",
    }


async def test_persons(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    response = await make_get_request("persons")
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 21


async def test_persons_empty(es_client, make_get_request):
    response = await make_get_request("persons")
    assert response.status == HTTPStatus.OK
    assert response.body == []


async def test_persons_pagination(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    response = await make_get_request("persons", {"page[size]": 20, "page[number]": 1})
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 20
    response = await make_get_request("persons", {"page[size]": 20, "page[number]": 2})
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 1


async def test_persons_films(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "persons/1f64ea08-b298-11ec-90b3-00155db24537/films"
    )
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 6
    assert filter_uuid(response.body) == set(
        [
            "1f650754-b298-11ec-90b3-00155db24537",
            "1f651c76-b298-11ec-90b3-00155db24537",
            "1f652f72-b298-11ec-90b3-00155db24537",
            "1f6546ba-b298-11ec-90b3-00155db24537",
            "1f656672-b298-11ec-90b3-00155db24537",
            "1f657e5a-b298-11ec-90b3-00155db24537",
        ]
    )


async def test_genre_films_pagination(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "persons/1f64ea08-b298-11ec-90b3-00155db24537/films",
        {"page[size]": 3, "page[number]": 1},
    )
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 3
    response = await make_get_request(
        "persons/1f64ea08-b298-11ec-90b3-00155db24537/films",
        {"page[size]": 3, "page[number]": 2},
    )
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 3
    response = await make_get_request(
        "persons/1f64ea08-b298-11ec-90b3-00155db24537/films",
        {"page[size]": 3, "page[number]": 3},
    )
    assert response.status == HTTPStatus.OK
    assert isinstance(response.body, list)
    assert len(response.body) == 0
