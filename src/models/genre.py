# Используем pydantic для упрощения работы при перегонке данных из
# json в объекты

from ast import Str

from pydantic import BaseModel

from .utils import orjson_dumps, orjson_loads


class ESGenre(BaseModel):
    id: Str
    full_name: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson_loads
        json_dumps = orjson_dumps
