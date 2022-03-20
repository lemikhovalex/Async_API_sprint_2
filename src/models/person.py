# Используем pydantic для упрощения работы при перегонке данных из
# json в объекты

from typing import List

from pydantic import BaseModel
from uuid import UUID

from .utils import orjson_dumps, orjson_loads


class IDNamePerson(BaseModel):
    uuid: UUID
    full_name: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson_loads
        json_dumps = orjson_dumps


class ESPerson(IDNamePerson):
    role: str
    film_ids: List[str]
