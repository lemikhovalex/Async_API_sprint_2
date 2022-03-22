from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.genres import GenreService, get_genre_service

router = APIRouter()


class GenrePartial(BaseModel):
    uuid: UUID
    name: str


@router.get('/{genre_id}', response_model=GenrePartial)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> GenrePartial:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found'
        )
    return GenrePartial(**genre.dict())
