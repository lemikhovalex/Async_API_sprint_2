from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class GenrePartial(BaseModel):
    uuid: UUID
    name: str


class PersonPartial(BaseModel):
    uuid: UUID
    full_name: str


class FilmFullInfo(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: Optional[str]
    genres: List[GenrePartial]
    actors: List[PersonPartial]
    writers: List[PersonPartial]
    directors: List[PersonPartial]
