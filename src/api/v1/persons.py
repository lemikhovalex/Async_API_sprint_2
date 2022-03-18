from typing import List

from pydantic import BaseModel


class PersonPartial(BaseModel):
    uuid: str
    full_name: str
