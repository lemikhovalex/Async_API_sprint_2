from typing import List

from pydantic import BaseModel


class GenrePartial(BaseModel):
    uuid: str
    name: str
