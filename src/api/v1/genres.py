from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from services.genres import GenreService, get_genre_service
from api.v1 import GenrePartial

router = APIRouter()

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

@router.get('/', response_model=List[GenrePartial])
async def genres(
    page_size: int = Query(50, alias="page[size]"),
    page_number: int = Query(1, alias="page[number]"),
    genre_service: GenreService = Depends(get_genre_service)
) -> List[GenrePartial]:
    genres = await genre_service.get_by(
        page_number=page_number,
        page_size=page_size,
    )
    return [ GenrePartial(**genre.dict()) for genre in genres ]
