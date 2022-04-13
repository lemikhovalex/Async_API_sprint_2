from http import HTTPStatus

import pytest
from test_data import genres, movies
from utils import es_load, take_only_ints

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio
TEST_GENRES_PAFINATION_DATA = [
    (
        1,
        2,
        [
            {"uuid": "1f64e56c-b298-11ec-90b3-00155db24537", "name": "comedy"},
            {"uuid": "1f64e81e-b298-11ec-90b3-00155db24537", "name": "drama"},
        ],
    ),
    (
        2,
        2,
        [{"uuid": "1f64e918-b298-11ec-90b3-00155db24537", "name": "action"}],
    ),
]

TEST_FILMS_BY_GENRES_PAFINATION_DATA = [
    (
        1,
        2,
        [
            {
                "uuid": "1f652f72-b298-11ec-90b3-00155db24537",
                "title": "HP 3",
                "imdb_rating": 9.8,
            },
            {
                "uuid": "1f651c76-b298-11ec-90b3-00155db24537",
                "title": "HP 2",
                "imdb_rating": 9.9,
            },
        ],
    ),
    (
        2,
        2,
        [
            {
                "uuid": "1f657e5a-b298-11ec-90b3-00155db24537",
                "title": "SW 2",
                "imdb_rating": 9.9,
            }
        ],
    ),
]


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


async def test_genre_films(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    await es_load(es_client, "movies", movies.movies)

    response = await make_get_request(
        "genres/1f64e918-b298-11ec-90b3-00155db24537/films"
    )

    assert response.status == HTTPStatus.OK
    assert response.body == [
        {
            "uuid": "1f652f72-b298-11ec-90b3-00155db24537",
            "title": "HP 3",
            "imdb_rating": 9.8,
        },
        {
            "uuid": "1f651c76-b298-11ec-90b3-00155db24537",
            "title": "HP 2",
            "imdb_rating": 9.9,
        },
        {
            "uuid": "1f657e5a-b298-11ec-90b3-00155db24537",
            "title": "SW 2",
            "imdb_rating": 9.9,
        },
    ]


@pytest.mark.parametrize(
    "page_num,page_size,resp",
    TEST_GENRES_PAFINATION_DATA,
    ids=take_only_ints,
)
async def test_genres_pagination(
    page_num, page_size, resp, es_client, make_get_request
):
    await es_load(es_client, "genres", genres.genres)

    response = await make_get_request(
        "genres", {"page[size]": page_size, "page[number]": page_num}
    )

    assert response.status == HTTPStatus.OK
    assert response.body == resp


@pytest.mark.parametrize(
    "page_num,page_size,resp",
    TEST_FILMS_BY_GENRES_PAFINATION_DATA,
    ids=take_only_ints,
)
async def test_genre_films_pagination(
    page_num, page_size, resp, es_client, make_get_request
):
    await es_load(es_client, "genres", genres.genres)
    await es_load(es_client, "movies", movies.movies)

    response = await make_get_request(
        "genres/1f64e918-b298-11ec-90b3-00155db24537/films",
        {"page[size]": page_size, "page[number]": page_num},
    )

    assert response.status == HTTPStatus.OK
    assert response.body == resp
