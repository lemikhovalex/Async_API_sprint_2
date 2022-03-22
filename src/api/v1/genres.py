from pydantic import BaseModel
from uuid import UUID


class GenrePartial(BaseModel):
    uuid: UUID
    name: str
