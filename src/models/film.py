from typing import List, Optional

from .base import BaseModel
from .genre import BaseGenre
from .person import BasePerson


class Film(BaseModel):
    imdb_rating: Optional[float]
    genres: List[BaseGenre]
    title: str
    description: Optional[str]
    actors: List[BasePerson]
    writers: List[BasePerson]
    directors: List[BasePerson]
