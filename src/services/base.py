from abc import ABC, abstractmethod
from typing import List, Optional, Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch, exceptions

from models.base import BaseModel
from services.paginators import BasePaginator

CACHE_EXPIRE_IN_SECONDS = 1


class BaseTableService(ABC):
    @abstractmethod
    async def get_by(self):
        pass

    @abstractmethod
    async def get_by_id(self):
        pass

    @abstractmethod
    def source() -> str:
        pass

    @abstractmethod
    def _result_class() -> Type[BaseModel]:
        pass


class BaseESService(BaseTableService, ABC):
    elastic: AsyncElasticsearch
    paginator: Type[BasePaginator]

    def __init__(self, elastic: AsyncElasticsearch, paginator: Type[BasePaginator]):
        self.elastic = elastic
        self.paginator = paginator

    async def get_by(
        self, page_number: int, page_size: int, sort_by: Optional[str] = None, **kwargs
    ):

        _sort = _sort = [{"_score": {}}]
        order = "desc"
        if sort_by is not None:
            if sort_by.startswith("-"):
                order = "asc"
                sort_by = sort_by[1:]
            _sort.insert(0, {sort_by: {"order": order}})
        _query = {
            "bool": {"must": [], "should": []},
        }
        _sort.append({"id": {}})
        if len(kwargs) > 0:
            for method, value in kwargs.items():
                method_name = "_query_by_{m}".format(m=method)
                _query = getattr(self, method_name)(value=value, query=_query)
        else:
            _query = {"match_all": {}}
        paginator = self.paginator(
            query=_query,
            sort=_sort,
            es=self.elastic,
            index=self.source(),
            page_number=page_number,
            page_size=page_size,
        )
        resp = await paginator.paginate_query()
        results_src = [datum["_source"] for datum in resp["hits"]["hits"]]
        return [self._result_class().parse_obj(src) for src in results_src]

    async def get_by_id(self, entity_id: UUID) -> Optional[BaseModel]:
        try:
            doc = await self.elastic.get(
                index=self.source(),
                id=str(entity_id),
            )
        except exceptions.NotFoundError:
            return None
        return self._result_class().parse_obj(doc["_source"])


class ESServieNamePartQueryMixin(ABC):
    def _query_by_name_part(self, value: UUID, query: dict) -> dict:
        # TODO look for escape function or take it from php es client
        query["bool"]["must"].append({"match": {"name": {"query": value}}})
        return query


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
