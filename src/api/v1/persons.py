from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.persons import PersonService, get_person_service

router = APIRouter()


class PersonPartial(BaseModel):
    uuid: UUID
    full_name: str


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
