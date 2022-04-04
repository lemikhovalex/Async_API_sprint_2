import pytest


@pytest.mark.asyncio
async def test_genre_by_id(filled_es, make_get_request):
    response = await make_get_request("/genres/1f64e918-b298-11ec-90b3-00155db24537")
    assert response.status == 200
    assert response.body == {
        "uuid": "1f64e918-b298-11ec-90b3-00155db24537",
        "name": "action",
    }
    response = await make_get_request("/genres/1f64e918-b298-11ec-90b3-00155db24539")
    assert response.status == 404
