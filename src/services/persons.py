from functools import lru_cache
from typing import Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.person import Person
from services.base import BaseService
from services.paginators import ESQueryPaginator


class PersonService(BaseService):
    def _index_name(self) -> str:
        return "persons"

    def _result_class(self) -> Type[Person]:
        return Person

    def _query_by_name_part(self, value: UUID, query: dict) -> dict:
        # TODO look for escape function or take it from php es client
        query["bool"]["must"].append({"match": {"name": {"query": value}}})
        return query


@lru_cache()
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic=elastic, paginator=ESQueryPaginator)
