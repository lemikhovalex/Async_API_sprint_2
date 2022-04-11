import pytest
from test_data import movies, persons
from utils import es_load


@pytest.mark.asyncio
async def test_persons_multitask(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    response = await make_get_request(
        "persons/search",
        params={"query": "Multitask", "page[number]": 1, "page[size]": 5},
    )
    assert response.status == 200
    assert response.body == [
        {
            "uuid": "1f64ea08-b298-11ec-90b3-00155db24537",
            "full_name": "Multitask person 0",
        },
        {
            "uuid": "1f64ed64-b298-11ec-90b3-00155db24537",
            "full_name": "Multitask person 1",
        },
        {
            "uuid": "1f64eecc-b298-11ec-90b3-00155db24537",
            "full_name": "Multitask person 2",
        },
    ]


@pytest.mark.asyncio
async def test_persons_multitask_pagination(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    response = await make_get_request(
        "persons/search",
        params={"query": "Multitask", "page[number]": 2, "page[size]": 2},
    )
    assert response.status == 200
    assert response.body == [
        {
            "uuid": "1f64eecc-b298-11ec-90b3-00155db24537",
            "full_name": "Multitask person 2",
        },
    ]


@pytest.mark.asyncio
async def test_persons_not_existing_name(es_client, make_get_request):
    await es_load(es_client, "persons", persons.persons)
    response = await make_get_request(
        "persons/search",
        params={"query": "not_existing_name", "page[number]": 1, "page[size]": 8},
    )
    assert response.status == 200
    assert response.body == []


@pytest.mark.asyncio
async def test_films_with_genre_1(es_client, make_get_request):
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "films/search",
        params={
            "query": "HP",
            "page[number]": 1,
            "page[size]": 8,
            "filter[genre]": "1f64e918-b298-11ec-90b3-00155db24537",
        },
    )
    assert response.status == 200
    assert response.body == [
        {
            "uuid": "1f651c76-b298-11ec-90b3-00155db24537",
            "title": "HP 2",
            "imdb_rating": 9.9,
        },
        {
            "uuid": "1f652f72-b298-11ec-90b3-00155db24537",
            "title": "HP 3",
            "imdb_rating": 9.8,
        },
    ]


@pytest.mark.asyncio
async def test_films_with_genre_2(es_client, make_get_request):
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "films/search",
        params={
            "query": "HP",
            "page[number]": 1,
            "page[size]": 8,
            "filter[genre]": "1f64e56c-b298-11ec-90b3-00155db24537",
        },
    )
    assert response.status == 200
    assert response.body == [
        {
            "uuid": "1f650754-b298-11ec-90b3-00155db24537",
            "title": "HP 1",
            "imdb_rating": 10.0,
        },
        {
            "uuid": "1f652f72-b298-11ec-90b3-00155db24537",
            "title": "HP 3",
            "imdb_rating": 9.8,
        },
        {
            "uuid": "1f6546ba-b298-11ec-90b3-00155db24537",
            "title": "HP 4",
            "imdb_rating": 9.7,
        },
    ]


@pytest.mark.asyncio
async def test_films_with_genre_2_with_pagination(es_client, make_get_request):
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "films/search",
        params={
            "query": "HP",
            "page[number]": 2,
            "page[size]": 2,
            "filter[genre]": "1f64e56c-b298-11ec-90b3-00155db24537",
        },
    )
    assert response.status == 200
    assert response.body == [
        {
            "uuid": "1f6546ba-b298-11ec-90b3-00155db24537",
            "title": "HP 4",
            "imdb_rating": 9.7,
        },
    ]


@pytest.mark.asyncio
async def test_films_not_existing(es_client, make_get_request):
    await es_load(es_client, "movies", movies.movies)
    response = await make_get_request(
        "films/search",
        params={"query": "Not existing film", "page[number]": 1, "page[size]": 8},
    )
    assert response.status == 200
    assert response.body == []
