from functools import lru_cache

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.person import Person
from .base import BaseService


class PersonService(BaseService):

    def _index_name(self):
        return 'persons'

    def _result_class(self):
        return Person

    def _query_by_name_part(self, name_part):
        # TODO look for escape function or take it from php es client
        return {
            'multi_match': {
                'query': name_part,
                'fields': ['name'],
            },
        }


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
