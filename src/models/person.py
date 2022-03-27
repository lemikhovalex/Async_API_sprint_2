from typing import List

from .base import BaseModel


class IDNamePerson(BaseModel):
    full_name: str

    class Config:
        fields = {"uuid": "id", "full_name": "name"}


class Person(IDNamePerson):
    roles: List[str]
