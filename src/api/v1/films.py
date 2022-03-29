from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_cache.decorator import cache

from api.v1 import FilmFullInfo, PartialFilmInfo, get_page_params
from core.config import REDIS_CACHE_EXPIRE
from services.films import FilmService, get_film_service

router = APIRouter()


@router.get("/search", response_model=List[PartialFilmInfo])
@cache(expire=REDIS_CACHE_EXPIRE)
async def film_search(
    query: Optional[str] = None,
    page: dict = Depends(get_page_params),
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
) -> List[PartialFilmInfo]:
    return await get_all_search(
        film_service=film_service,
        query=query,
        page=page,
        filter_genre=filter_genre,
    )


@router.get("", response_model=List[PartialFilmInfo])
@cache(expire=REDIS_CACHE_EXPIRE)
async def film_search_general(
    sort: Optional[str] = "imdb_rating",
    page: dict = Depends(get_page_params),
    film_service: FilmService = Depends(get_film_service),
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
) -> List[PartialFilmInfo]:
    return await get_all_search(
        film_service=film_service,
        sort=sort,
        page=page,
        filter_genre=filter_genre,
    )


@router.get("/{film_id}", response_model=FilmFullInfo)
@cache(expire=REDIS_CACHE_EXPIRE)
async def film_details(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> FilmFullInfo:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    return FilmFullInfo.parse_obj(film.dict())


async def get_all_search(
    film_service,
    page: dict,
    sort: Optional[str] = None,
    query: Optional[str] = None,
    filter_genre: Optional[UUID] = Query(None, alias="filter[genre]"),
) -> List[PartialFilmInfo]:
    out = await film_service.get_by_query(
        query=query,
        page_number=page["number"],
        page_size=page["size"],
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
