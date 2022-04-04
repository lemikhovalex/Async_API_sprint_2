from typing import List
from uuid import UUID

from pydantic import BaseModel


class BasePerson(BaseModel):
    id: UUID
    name: str


class Person(BasePerson):
    roles: List[str]


class Genre(BaseModel):
    id: UUID
    name: str


class FilmWork(BaseModel):
    id: UUID
    imdb_rating: float
    title: str
    description: str
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    genres: List[Genre]
    actors: List[BasePerson]
    directors: List[BasePerson]
    writers: List[BasePerson]
