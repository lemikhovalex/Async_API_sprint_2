from typing import List, Optional

import orjson

# Используем pydantic для упрощения работы при перегонке данных из
# json в объекты
from pydantic import BaseModel, Field

from .genre import IDNameGenre
from .person import IDNamePerson
from .utils import orjson_dumps


class ESFilm(BaseModel):
    uuid: str
    imdb_rating: Optional[float]
    genre: List[IDNameGenre]
    title: str
    description: Optional[str]
    # TODO confirm ES index change
    # director: List[str] = Field(alias="directors")
    # actors_names: List[str]
    # writers_names: List[str]
    actors: List[IDNamePerson]
    writers: List[IDNamePerson]
    directors: List[IDNamePerson]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
