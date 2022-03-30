from abc import ABC, abstractmethod
from typing import List, Optional, Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch, exceptions

from models.base import BaseModel

CACHE_EXPIRE_IN_SECONDS = 1


class BaseService(ABC):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by(
        self, page_number: int, page_size: int, sort: Optional[str] = None, **kwargs
    ) -> List[BaseModel]:
        """Random query fields goes in kwargs"""
        if len(kwargs):
            method_name = "_query_by_{0}".format("_".join(sorted(kwargs.keys())))
            query = getattr(self, method_name)(**kwargs)
        else:
            query = {"match_all": {}}
        sort_for_es = None
        if sort is not None:
            sort_for_es = {
                sort.lstrip("-"): {"order": "desc" if sort.startswith("-") else "asc"}
            }

        result = await self.elastic.search(
            index=self._index_name(),
            query=query,
            from_=page_size * (page_number - 1),
            size=page_size,
            sort=sort_for_es,
        )
        return [
            self._result_class().parse_obj(doc["_source"])
            for doc in result["hits"]["hits"]
        ]

    async def get_by_id(self, entity_id: UUID) -> Optional[BaseModel]:
        try:
            doc = await self.elastic.get(
                index=self._index_name(),
                id=str(entity_id),
            )
        except exceptions.NotFoundError:
            return None
        return self._result_class().parse_obj(doc["_source"])

    @abstractmethod
    def _index_name(self) -> str:
        pass

    @abstractmethod
    def _result_class(self) -> Type[BaseModel]:
        pass
