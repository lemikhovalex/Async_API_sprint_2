from typing import List, Optional

import orjson

# Используем pydantic для упрощения работы при перегонке данных из
# json в объекты
from pydantic import BaseModel, Field

from .genre import ESGenre
from .utils import orjson_dumps


class PartialPerson(BaseModel):
    uuid: str
    full_name: str


class ESFilm(BaseModel):
    id: str = Field(alias="film_work_id")
    imdb_rating: Optional[float]
    genre: List[ESGenre] = Field(alias="genre_name")
    title: str
    description: Optional[str]
    # TODO confirm ES index change
    # director: List[str] = Field(alias="directors")
    # actors_names: List[str]
    # writers_names: List[str]
    actors: List[PartialPerson]
    writers: List[PartialPerson]
    directors: List[PartialPerson]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
