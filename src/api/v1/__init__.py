from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel


def get_page_params(
    size: int = Query(50, alias="page[size]"),
    number: int = Query(1, alias="page[number]"),
):
    return {"size": size, "number": number}


class GenrePartial(BaseModel):
    uuid: UUID
    name: str


class PersonPartial(BaseModel):
    uuid: UUID
    full_name: str


class PartialFilmInfo(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float] = None


class FilmFullInfo(PartialFilmInfo):
    description: Optional[str]
    genre: List[GenrePartial]
    actors: List[PersonPartial]
    writers: List[PersonPartial]
    directors: List[PersonPartial]

    class Config:
        fields = {"genre": "genres"}
