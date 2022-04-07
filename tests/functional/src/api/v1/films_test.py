import json

import pytest
from utils import es_load


@pytest.mark.asyncio
async def test_film_by_id(es_client, make_get_request):
    with open("test_data/movies.json", "r") as f:
        movies = json.load(f)
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
