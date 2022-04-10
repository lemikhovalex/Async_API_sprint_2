from abc import ABC, abstractmethod
from typing import Optional, Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch, exceptions

from models.base import BaseModel
from services.paginators import BasePaginator

CACHE_EXPIRE_IN_SECONDS = 1


class BaseService(ABC):
    elastic: AsyncElasticsearch
    paginator: Type[BasePaginator]

    def __init__(self, elastic: AsyncElasticsearch, paginator: Type[BasePaginator]):
        self.elastic = elastic
        self.paginator = paginator

    async def get_by(
        self, page_number: int, page_size: int, sort: Optional[str] = None, **kwargs
    ):

        _sort = _sort = [{"_score": {}}]
        order = "desc"
        if sort is not None:
            if sort.startswith("-"):
                order = "asc"
                sort = sort[1:]
            _sort.insert(0, {sort: {"order": order}})
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
            index=self._index_name(),
            page_number=page_number,
            page_size=page_size,
        )
        resp = await paginator.paginate_query()
        results_src = [datum["_source"] for datum in resp["hits"]["hits"]]
        return [self._result_class().parse_obj(src) for src in results_src]

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
