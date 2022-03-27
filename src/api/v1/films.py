from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache

from api.v1 import FilmFullInfo, PartialFilmInfo
from core.config import REDIS_CACHE_EXPIRE
from services.films import FilmService, get_film_service

router = APIRouter()


@router.get("/{film_id}/", response_model=FilmFullInfo)
@cache(expire=REDIS_CACHE_EXPIRE)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> FilmFullInfo:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return FilmFullInfo.parse_obj(film.dict())


@router.get("", response_model=List[PartialFilmInfo])
@cache(expire=REDIS_CACHE_EXPIRE)
async def film_search_general(
    sort: Optional[str] = None,
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
) -> List[PartialFilmInfo]:
    return await get_all_search(
        film_service=film_service,
        sort=sort,
        page_size=page_size,
        page_number=page_number,
        filter_genre=filter_genre,
    )


@router.get("/search", response_model=List[PartialFilmInfo])
@cache(expire=REDIS_CACHE_EXPIRE)
async def film_search(
    query: Optional[str] = None,
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
) -> List[PartialFilmInfo]:

    return await get_all_search(
        film_service=film_service,
        query=query,
        page_size=page_size,
        page_number=page_number,
        filter_genre=filter_genre,
    )


async def get_all_search(
    film_service,
    sort: Optional[str] = None,
    query: Optional[str] = None,
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
) -> List[PartialFilmInfo]:
    out = await film_service.get_by_query(
        query=query,
        page_number=page_number,
        page_size=page_size,
        sort_by=sort,
        genre_filter=filter_genre,
    )
    return [
        PartialFilmInfo(
            uuid=es_film.uuid,
            title=es_film.title,
            imdb_rating=es_film.imdb_rating,
        )
        for es_film in out
    ]
