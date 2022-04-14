from http import HTTPStatus

import pytest
from utils import filter_int

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

TEST_SEARCH_FILMS_PAGINATION_DATA = [
    (
        1,
        2,
        [
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
        ],
    ),
    (
        2,
        2,
        [
            {
                "uuid": "1f6546ba-b298-11ec-90b3-00155db24537",
                "title": "HP 4",
                "imdb_rating": 9.7,
            }
        ],
    ),
]


async def test_persons_multitask(make_get_request):
    response = await make_get_request(
        "persons/search",
        params={"query": "Multitask", "page[number]": 1, "page[size]": 5},
    )

    assert response.status == HTTPStatus.OK
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


async def test_persons_multitask_pagination(make_get_request):
    response = await make_get_request(
        "persons/search",
        params={"query": "Multitask", "page[number]": 2, "page[size]": 2},
    )

    assert response.status == HTTPStatus.OK
    assert response.body == [
        {
            "uuid": "1f64eecc-b298-11ec-90b3-00155db24537",
            "full_name": "Multitask person 2",
        },
    ]


async def test_persons_not_existing_name(make_get_request):
    response = await make_get_request(
        "persons/search",
        params={"query": "not_existing_name", "page[number]": 1, "page[size]": 8},
    )

    assert response.status == HTTPStatus.OK
    assert response.body == []


async def test_films_with_genre_1(make_get_request):
    response = await make_get_request(
        "films/search",
        params={
            "query": "HP",
            "page[number]": 1,
            "page[size]": 8,
            "filter[genre]": "1f64e918-b298-11ec-90b3-00155db24537",
        },
    )

    assert response.status == HTTPStatus.OK
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


async def test_films_with_genre_2(make_get_request):
    response = await make_get_request(
        "films/search",
        params={
            "query": "HP",
            "page[number]": 1,
            "page[size]": 8,
            "filter[genre]": "1f64e56c-b298-11ec-90b3-00155db24537",
        },
    )

    assert response.status == HTTPStatus.OK
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


@pytest.mark.parametrize(
    "page_num,page_size,expected_resp",
    TEST_SEARCH_FILMS_PAGINATION_DATA,
    ids=filter_int,
)
async def test_films_with_genre_2_with_pagination(
    page_num, page_size, expected_resp, make_get_request
):
    response = await make_get_request(
        "films/search",
        params={
            "query": "HP",
            "page[number]": page_num,
            "page[size]": page_size,
            "filter[genre]": "1f64e56c-b298-11ec-90b3-00155db24537",
        },
    )

    assert response.status == HTTPStatus.OK
    assert response.body == expected_resp


async def test_films_not_existing(make_get_request):
    response = await make_get_request(
        "films/search",
        params={"query": "Not existing film", "page[number]": 1, "page[size]": 8},
    )

    assert response.status == HTTPStatus.OK
    assert response.body == []
