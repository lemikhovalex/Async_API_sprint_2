from functools import lru_cache
from typing import Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from services.base import BaseESService
from services.paginators import ESQueryPaginator


class FilmService(BaseESService):
    def source(self) -> str:
        return "movies"

    def _result_class(self) -> Type[Film]:
        return Film

    def _query_by_genre_id(self, value: UUID, query: dict) -> dict:
        # TODO look for escape function or take it from php es client
        query["bool"]["must"].append(
            {
                "nested": {
                    "path": "genres",
                    "query": {"term": {"genres.id": {"value": value}}},
                }
            }
        )

        return query

    def _query_by_query(self, value: UUID, query: dict) -> dict:
        # TODO look for escape function or take it from php es client
        query["bool"]["must"].append(
            {
                "multi_match": {
                    "query": value,
                    "fields": ["*"],
                },
            }
        )
        return query

    def _query_by_person_id(self, value: UUID, query: dict) -> dict:
        # TODO look for escape function or take from php es client
        def _q_nested(role, person_id):
            return {
                "nested": {"path": role, "query": {"term": {"%s.id" % role: person_id}}}
            }

        roles = ("actors", "directors", "writers")

        to_app = [_q_nested(role, value) for role in roles]
        query["bool"]["should"].extend(to_app)
        return query


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic=elastic, paginator=ESQueryPaginator)
