# Используем pydantic для упрощения работы при перегонке данных из
# json в объекты

from pydantic import BaseModel

from .utils import orjson_dumps, orjson_loads


class IDNameGenre(BaseModel):
    uuid: str
    name: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson_loads
        json_dumps = orjson_dumps


class ESGenre(IDNameGenre):
    description: str
