from pydantic import BaseModel
from uuid import UUID


class PersonPartial(BaseModel):
    uuid: UUID
    full_name: str
