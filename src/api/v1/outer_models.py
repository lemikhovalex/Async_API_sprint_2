from typing import List

from pydantic import BaseModel


class Person(BaseModel):
    uuid: str
    full_name: str


class Genre(BaseModel):
    uuid: str
    name: str


class FilmFullInfo(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
    description: str
    genre: List[Genre]
    actors: List[Person]
    writers: List[Person]
    directors: List[Person]
