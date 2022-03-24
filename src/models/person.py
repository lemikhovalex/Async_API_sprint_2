from typing import List

from .base import BaseModel


class IDNamePerson(BaseModel):
    full_name: str

    class Config:
        fields = {'uuid': 'id'}


class Person(IDNamePerson):
    pass
    # role: str
    # film_ids: List[str]
