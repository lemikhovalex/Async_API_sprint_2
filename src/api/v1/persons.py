from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from services.persons import PersonService, get_person_service

from api.v1 import FilmFullInfo, PersonPartial

router = APIRouter()

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
