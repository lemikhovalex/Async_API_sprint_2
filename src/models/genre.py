from .base import BaseModel


class IDNameGenre(BaseModel):
    name: str


class Genre(IDNameGenre):
    description: str
