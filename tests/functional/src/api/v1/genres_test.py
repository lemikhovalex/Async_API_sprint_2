import pytest
from test_data import genres
from utils import es_load


@pytest.mark.asyncio
async def test_genre_by_id(es_client, make_get_request):
    await es_load(es_client, "genres", genres.genres)
    response = await make_get_request("/genres/1f64e918-b298-11ec-90b3-00155db24537")
    assert response.status == 200
    assert response.body == {
        "uuid": "1f64e918-b298-11ec-90b3-00155db24537",
        "name": "action",
    }
    response = await make_get_request("/genres/1f64e918-b298-11ec-90b3-00155db24539")
    assert response.status == 404
