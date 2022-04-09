from functools import lru_cache
from typing import List, Optional, Type
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.film import Film
from services.base import BaseService
from services.paginators import ESQueryPaginator


class FilmService(BaseService):
    def _index_name(self) -> str:
        return "movies"

    def _result_class(self) -> Type[Film]:
        return Film

    def _query_by_genre_id(self, genre_id: UUID) -> dict:
        # TODO look for escape function or take it from php es client
        return {
            "nested": {"path": "genres", "query": {"term": {"genres.id": genre_id}}}
        }

    def _query_by_person_id(self, person_id: UUID) -> dict:
        # TODO look for escape function or take from php es client
        def _q_nested(role, person_id):
            return {
                "nested": {"path": role, "query": {"term": {"%s.id" % role: person_id}}}
            }

        roles = ("actors", "directors", "writers")

        return {"bool": {"should": [_q_nested(i, person_id) for i in roles]}}

    async def get_by_query(
        self,
        query: Optional[str] = None,
        page_size: int = 50,
        page_number: int = 1,
        sort_by: Optional[str] = "imdb_rating",
        genre_filter: Optional[UUID] = None,
        unique_sort_fields: Optional[List[str]] = None,
    ) -> List[Film]:
        if unique_sort_fields is None:
            unique_sort_fields = ["id"]

        _sort = [
            {
                "_score": {},
            },
        ]

        _query = {
            "bool": {"must": [], "should": []},
        }
        if query is not None:
            _query["bool"]["must"].append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"],
                    },
                }
            )
        if genre_filter is not None:
            _query["bool"]["must"].append(
                {
                    "nested": {
                        "path": "genres",
                        "query": {"term": {"genres.id": {"value": genre_filter}}},
                    }
                }
            )

        order = "desc"
        if sort_by is not None:
            if sort_by.startswith("-"):
                order = "asc"
                sort_by = sort_by[1:]
            _sort.insert(0, {sort_by: {"order": order}})

        _sort.extend([{_sf: {}} for _sf in unique_sort_fields])

        paginator = ESQueryPaginator(
            query=_query,
            sort=_sort,
            es=self.elastic,
            index=self._index_name(),
            page_number=page_number,
            page_size=page_size,
        )
        resp = await paginator.paginate_query()
        results_src = [datum["_source"] for datum in resp["hits"]["hits"]]
        return [Film(**src) for src in results_src]


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
