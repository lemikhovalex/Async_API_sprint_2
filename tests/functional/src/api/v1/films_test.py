import copy
import json
from http import HTTPStatus
from operator import attrgetter

import pytest
from pydantic import BaseModel
from test_data.movies import movies
from utils import es_load


class PartialFilm(BaseModel):
    imdb_rating: float
    title: str
    uuid: str

    class Config:
        fields = {"uuid": "id"}


# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio


TEST_FILMS_PAFINATION_DATA = [
    (
        1,
        3,
        [
            {
                "uuid": "1f650754-b298-11ec-90b3-00155db24537",
                "title": "HP 1",
                "imdb_rating": 10.0,
            },
            {
                "uuid": "1f656672-b298-11ec-90b3-00155db24537",
                "title": "SW 1",
                "imdb_rating": 10.0,
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
        3,
        [
            {
                "uuid": "1f657e5a-b298-11ec-90b3-00155db24537",
                "title": "SW 2",
                "imdb_rating": 9.9,
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
        ],
    ),
]


async def test_film_by_id_absent(es_client, make_get_request):
    await es_load(es_client, "movies", movies)

    response = await make_get_request("films/1f6546ba-0000-11ec-90b3-00155db24537")

    assert response.status == HTTPStatus.NOT_FOUND


async def test_film_by_id(es_client, make_get_request):
    await es_load(es_client, "movies", movies)

    response = await make_get_request("films/1f6546ba-b298-11ec-90b3-00155db24537")

    assert response.status == HTTPStatus.OK
    assert response.body == {
        "uuid": "1f6546ba-b298-11ec-90b3-00155db24537",
        "imdb_rating": 9.7,
        "title": "HP 4",
        "description": "description for HP",
        "genres": [
            {"uuid": "1f64e56c-b298-11ec-90b3-00155db24537", "name": "comedy"},
            {"uuid": "1f64e81e-b298-11ec-90b3-00155db24537", "name": "drama"},
        ],
        "actors": [
            {"uuid": "1f64f02a-b298-11ec-90b3-00155db24537", "full_name": "HP_actor_0"},
            {"uuid": "1f64f138-b298-11ec-90b3-00155db24537", "full_name": "HP_actor_1"},
            {"uuid": "1f64f228-b298-11ec-90b3-00155db24537", "full_name": "HP_actor_2"},
            {
                "uuid": "1f64ea08-b298-11ec-90b3-00155db24537",
                "full_name": "Multitask person 0",
            },
            {
                "uuid": "1f64ed64-b298-11ec-90b3-00155db24537",
                "full_name": "Multitask person 1",
            },
        ],
        "directors": [
            {
                "uuid": "1f64f674-b298-11ec-90b3-00155db24537",
                "full_name": "HP_director_0",
            },
            {
                "uuid": "1f64f746-b298-11ec-90b3-00155db24537",
                "full_name": "HP_director_1",
            },
            {
                "uuid": "1f64f822-b298-11ec-90b3-00155db24537",
                "full_name": "HP_director_2",
            },
            {
                "uuid": "1f64eecc-b298-11ec-90b3-00155db24537",
                "full_name": "Multitask person 2",
            },
            {
                "uuid": "1f64ea08-b298-11ec-90b3-00155db24537",
                "full_name": "Multitask person 0",
            },
        ],
        "writers": [
            {
                "uuid": "1f64f32c-b298-11ec-90b3-00155db24537",
                "full_name": "HP_writer_0",
            },
            {
                "uuid": "1f64f412-b298-11ec-90b3-00155db24537",
                "full_name": "HP_writer_1",
            },
            {
                "uuid": "1f64f520-b298-11ec-90b3-00155db24537",
                "full_name": "HP_writer_2",
            },
            {
                "uuid": "1f64ed64-b298-11ec-90b3-00155db24537",
                "full_name": "Multitask person 1",
            },
            {
                "uuid": "1f64eecc-b298-11ec-90b3-00155db24537",
                "full_name": "Multitask person 2",
            },
        ],
    }


def pagination_test_id_gen(x):
    if isinstance(x, int):
        return x


@pytest.mark.parametrize(
    "page_num,page_size,resp", TEST_FILMS_PAFINATION_DATA, ids=pagination_test_id_gen
)
async def test_films_pagination(page_num, page_size, resp, es_client, make_get_request):
    await es_load(es_client, "movies", movies)

    films_resp = await make_get_request(
        "films",
        params={
            "sort": "imdb_rating",
            "page[size]": page_size,
            "page[number]": page_num,
        },
    )

    assert films_resp.status == HTTPStatus.OK
    assert films_resp.body == resp


async def test_films_check_all_films(es_client, make_get_request):
    await es_load(es_client, "movies", movies)
    _MOVIES = copy.deepcopy(movies)
    _MOVIES = [PartialFilm(**m) for m in _MOVIES]
    _MOVIES = sorted(_MOVIES, key=attrgetter("uuid"))
    _MOVIES = sorted(_MOVIES, key=attrgetter("imdb_rating"), reverse=True)
    _MOVIES = [json.loads(f.json()) for f in _MOVIES]

    resp_all_films = await make_get_request(
        "films", params={"sort": "imdb_rating", "page[size]": 1000, "page[number]": 1}
    )

    assert resp_all_films.status == HTTPStatus.OK
    assert isinstance(resp_all_films.body, list)
    assert len(resp_all_films.body) == 6
    assert resp_all_films.body == _MOVIES


async def test_films_check_no_films(es_client, make_get_request):
    await es_load(es_client, "movies", [])

    response = await make_get_request(
        "films/?sort=imdb_rating&page[size]=1000&page[number]=1",
    )

    assert response.status == HTTPStatus.OK
    assert response.body == []
