from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from services.films import FilmService, get_film_service
from services.persons import PersonService, get_person_service

from api.v1 import FilmFullInfo, PersonPartial

router = APIRouter()

@router.get('/search', response_model=List[PersonPartial])
async def persons(
    query: str,
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    person_service: PersonService = Depends(get_person_service)
) -> List[PersonPartial]:
    persons = await person_service.get_by(
        name_part=query,
        page_number=page_number,
        page_size=page_size,
    )
    return [ PersonPartial(**person.dict()) for person in persons ]

@router.get('/{person_id}', response_model=PersonPartial)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonPartial:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='person not found'
        )
    return PersonPartial(**person.dict())

@router.get('/', response_model=List[PersonPartial])
async def persons(
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    person_service: PersonService = Depends(get_person_service)
) -> List[PersonPartial]:
    persons = await person_service.get_by(
        page_number=page_number,
        page_size=page_size,
    )
    return [ PersonPartial(**person.dict()) for person in persons ]

@router.get('/{person_id}/films', response_model=List[FilmFullInfo])
async def person_films(
    person_id: str,
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmFullInfo]:
    films = await film_service.get_by(
        person_id=person_id,
        page_number=page_number,
        page_size=page_size,
    )
    return [ FilmFullInfo(**film.dict()) for film in films ]
