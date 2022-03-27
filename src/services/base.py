from typing import List, Optional

from abc import ABC, abstractmethod
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, exceptions
from models.base import BaseModel

CACHE_EXPIRE_IN_SECONDS = 1


class BaseService(ABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by(self, page_number: int, page_size: int, sort: str = None, **kwargs) -> List[BaseModel]:
        """Random query fields goes in kwargs
        """
        if len(kwargs):
            method_name = '_query_by_{0}'.format('_'.join(sorted(kwargs.keys())))
            query = getattr(self, method_name)(**kwargs)
        else:
            query = {'match_all':{}}

        if sort is not None:
            sort = {sort.lstrip('-'): {'order': 'desc' if sort.startswith('-') else 'asc'}}

        result = await self.elastic.search(
            index=self._index_name(),
            query=query,
            from_=page_size*(page_number-1),
            size=page_size,
            sort=sort,
        )
        return [ self._result_class().parse_obj(doc['_source'])
            for doc in result['hits']['hits'] ]

    async def get_by_id(self, entity_id: str) -> Optional[BaseModel]:
        entity = await self._get_from_cache(entity_id)
        if entity:
            return entity
        # no entity in cache
        entity = await self._get_from_elastic(entity_id)
        if not entity:
            return None

        await self._put_to_cache(entity)

        return entity

    async def _get_from_elastic(self, entity_id: str) -> Optional[BaseModel]:
        try:
            doc = await self.elastic.get(
                index=self._index_name(),
                id=entity_id,
            )
        except exceptions.NotFoundError:
            return None
        return self._result_class().parse_obj(doc['_source'])

    async def _get_from_cache(self, entity_id: str) -> Optional[BaseModel]:
        data = await self.redis.get(entity_id)
        if not data:
            return None

        result = self._result_class().parse_raw(data)
        return result

    async def _put_to_cache(self, entity: BaseModel):
        await self.redis.set(
            str(entity.uuid), entity.json(), ex=CACHE_EXPIRE_IN_SECONDS
        )

    @abstractmethod
    def _index_name(self):
        pass

    @abstractmethod
    def _result_class(self):
        pass
