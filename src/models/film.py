from typing import List, Optional


from .base import BaseModel
from .genre import IDNameGenre
from .person import IDNamePerson


class Film(BaseModel):
    imdb_rating: Optional[float]
    genres: List[IDNameGenre]
    title: str
    description: Optional[str]
    actors: List[IDNamePerson]
    writers: List[IDNamePerson]
    directors: List[IDNamePerson]
