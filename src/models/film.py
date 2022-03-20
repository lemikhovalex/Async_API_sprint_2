from typing import List, Optional

import orjson

# Используем pydantic для упрощения работы при перегонке данных из
# json в объекты
from pydantic import BaseModel, Field
from uuid import UUID

from .genre import IDNameGenre
from .person import IDNamePerson
from .utils import orjson_dumps


class ESFilm(BaseModel):
    uuid: UUID
    imdb_rating: Optional[float]
    genre: List[IDNameGenre]
    title: str
    description: Optional[str]
    actors: List[IDNamePerson]
    writers: List[IDNamePerson]
    directors: List[IDNamePerson]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
