from typing import List, Optional

import orjson

from pydantic import BaseModel
from uuid import UUID

from .genre import IDNameGenre
from .person import IDNamePerson
from .utils import orjson_dumps


class Film(BaseModel):
    uuid: UUID
    imdb_rating: Optional[float]
    genre: List[IDNameGenre]
    title: str
    description: Optional[str]
    actors: List[IDNamePerson]
    writers: List[IDNamePerson]
    directors: List[IDNamePerson]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
