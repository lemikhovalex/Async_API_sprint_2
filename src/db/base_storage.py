from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field


class QueryOptions(BaseModel):
    must: list
    should: list


class QueryParam(BaseModel):
    bool_: QueryOptions = Field(QueryOptions(must=[], should=[]), alias="bool")


class SortFieldOption(BaseModel):
    order: str = "desc"


class SortField(BaseModel):
    field: SortFieldOption


class SortParam(BaseModel):
    fields: List[SortField]


class BaseStorage(ABC):
    @abstractmethod
    async def get_by_id(self, index: str, id):
        pass

    @abstractmethod
    async def get_with_search(self, query: SortParam, sort: SortParam, **kwargs):
        pass
