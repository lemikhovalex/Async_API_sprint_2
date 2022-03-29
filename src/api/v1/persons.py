from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache

from api.v1 import PartialFilmInfo, PersonPartial, get_page_params
from core.config import REDIS_CACHE_EXPIRE
from services.films import FilmService, get_film_service
from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get("/search", response_model=List[PersonPartial])
@cache(expire=REDIS_CACHE_EXPIRE)
async def persons_search(
    query: str,
    page: dict = Depends(get_page_params),
    person_service: PersonService = Depends(get_person_service),
) -> List[PersonPartial]:
    persons = await person_service.get_by(
        name_part=query,
        page_number=page["number"],
        page_size=page["size"],
    )
    return [PersonPartial(**person.dict()) for person in persons]


@router.get("/{person_id}", response_model=PersonPartial)
@cache(expire=REDIS_CACHE_EXPIRE)
async def person_details(
    person_id: UUID, person_service: PersonService = Depends(get_person_service)
) -> PersonPartial:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return PersonPartial(**person.dict())


@router.get("", response_model=List[PersonPartial])
@cache(expire=REDIS_CACHE_EXPIRE)
async def persons(
    page: dict = Depends(get_page_params),
    person_service: PersonService = Depends(get_person_service),
) -> List[PersonPartial]:
    persons = await person_service.get_by(
        page_number=page["number"],
        page_size=page["size"],
    )
    return [PersonPartial(**person.dict()) for person in persons]


@router.get("/{person_id}/films", response_model=List[PartialFilmInfo])
@cache(expire=REDIS_CACHE_EXPIRE)
async def person_films(
    person_id: str,
    page: dict = Depends(get_page_params),
    film_service: FilmService = Depends(get_film_service),
) -> List[PartialFilmInfo]:
    films = await film_service.get_by(
        person_id=person_id,
        page_number=page["number"],
        page_size=page["size"],
        sort="-imdb_rating",
    )
    return [PartialFilmInfo(**film.dict()) for film in films]
