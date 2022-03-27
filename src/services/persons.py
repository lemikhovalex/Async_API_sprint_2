from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.person import Person

from .base import BaseService


class PersonService(BaseService):
    def _index_name(self):
        return "persons"

    def _result_class(self):
        return Person

    def _query_by_name_part(self, name_part):
        # TODO look for escape function or take it from php es client
        return {"match": {"name": {"query": name_part}}}


@lru_cache()
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
