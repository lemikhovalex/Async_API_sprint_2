import copy
import json
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


@pytest.mark.asyncio
async def test_film_by_id(es_client, make_get_request):
    await es_load(es_client, "movies", movies)
    response = await make_get_request("/films/1f6546ba-b298-11ec-90b3-00155db24537")
    assert response.status == 200
    assert response.body == {
        "uuid": "1f6546ba-b298-11ec-90b3-00155db24537",
        "imdb_rating": 9.7,
        "title": "HP",
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


@pytest.mark.asyncio
async def test_films_pagination(es_client, make_get_request):
    await es_load(es_client, "movies", movies)
    resp_all_films = await make_get_request(
        "/films", params={"sort": "imdb_rating", "page[size]": 6, "page[number]": 1}
    )
    assert resp_all_films.status == 200
    all_ids = {film["uuid"] for film in resp_all_films.body}

    resps_films_by_parts = []
    n_parts = 2
    for _i in range(n_parts):
        resp = await make_get_request(
            f"/films/?sort=imdb_rating&page[size]=3&page[number]={_i+1}"
        )
        assert resp.status == 200
        resps_films_by_parts.append([film["uuid"] for film in resp.body])

    for part in range(n_parts):
        for r in resps_films_by_parts[part]:
            assert r in all_ids

    for part in range(n_parts):
        for second_p in range(part, n_parts):
            bool(set(resps_films_by_parts[part]) & set(resps_films_by_parts[second_p]))


@pytest.mark.asyncio
async def test_films_check_all_films(es_client, make_get_request):

    await es_load(es_client, "movies", movies)
    resp_all_films = await make_get_request(
        "/films/?sort=imdb_rating&page[size]=1000&page[number]=1"
    )
    assert resp_all_films.status == 200
    assert isinstance(resp_all_films.body, list)
    assert len(resp_all_films.body) == 6
    _MOVIES = copy.deepcopy(movies)
    _MOVIES = [PartialFilm(**m) for m in _MOVIES]
    _MOVIES = sorted(_MOVIES, key=attrgetter("uuid"))
    _MOVIES = sorted(_MOVIES, key=attrgetter("imdb_rating"), reverse=True)
    _MOVIES = [json.loads(f.json()) for f in _MOVIES]
    assert resp_all_films.body == _MOVIES


@pytest.mark.asyncio
async def test_films_check_no_films(es_client, make_get_request):
    await es_load(es_client, "movies", [])
    response = await make_get_request(
        "/films/?sort=imdb_rating&page[size]=1000&page[number]=1",
    )
    assert response.status == 200
    assert response.body == []
