from functools import lru_cache
from typing import Type

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.person import Person
from services.base import BaseESService, ESServieNamePartQueryMixin
from services.paginators import ESQueryPaginator


class PersonService(BaseESService, ESServieNamePartQueryMixin):
    def source(self) -> str:
        return "persons"

    def _result_class(self) -> Type[Person]:
        return Person


@lru_cache()
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic=elastic, paginator=ESQueryPaginator)
