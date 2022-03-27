from functools import lru_cache
from math import ceil
from typing import List, Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from fastapi import Depends

from core.config import MAX_ES_SEARCH_FROM_SIZE
from db.elastic import get_elastic
from models.film import Film

from .base import BaseService


class FilmService(BaseService):
    def _index_name(self):
        return "movies"

    def _result_class(self):
        return Film

    def _query_by_genre_id(self, genre_id):
        # TODO look for escape function or take it from php es client
        return {
            "nested": {"path": "genres", "query": {"term": {"genres.id": genre_id}}}
        }

    def _query_by_person_id(self, person_id):
        # TODO look for escape function or take from php es client
        def _q_nested(role, person_id):
            return {
                "nested": {"path": role, "query": {"term": {"%s.id" % role: person_id}}}
            }

        roles = ("actors", "directors", "writers")

        return {"bool": {"should": [_q_nested(i, person_id) for i in roles]}}

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может
    # отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        out = None
        try:
            doc = await self.elastic.get(index=self._index_name(), id=film_id)
            out = Film(**doc["_source"])
        except NotFoundError:
            pass
        return out

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

        body = {
            "sort": [
                {
                    "_score": {},
                },
            ],
            "query": {
                "bool": {"must": [], "should": []},
            },
        }
        if query is not None:
            body["query"]["bool"]["must"].append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"],
                    },
                }
            )

        if genre_filter is not None:
            body["query"]["bool"]["must"].append(
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
            body["sort"].insert(0, {sort_by: {"order": order}})

        body["sort"].extend([{_sf: {}} for _sf in unique_sort_fields])

        paginator = QueryPaginator(
            body=body,
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


class QueryPaginator:
    def __init__(
        self,
        body: dict,
        es: AsyncElasticsearch,
        index: str,
        page_number: int,
        page_size: int,
    ):
        self.es = es
        self.body = body
        self.index = index
        self.page_size = page_size
        self.search_from = (page_number - 1) * page_size
        self.accum_shift = 0
        self.search_after = None
        self.pit = None

    async def paginate_query(self):
        n = ceil(self.search_from / MAX_ES_SEARCH_FROM_SIZE)
        self.pit = await self.es.open_point_in_time(index=self.index, keep_alive="1m")
        self.pit = self.pit["id"]
        # make shure that search after point to the beginning of page
        for _ in range(n):
            await self._process_inner_pag_query()

        self.body["size"] = self.page_size

        out = await self.es.search(
            body=self.body, pit={"id": self.pit, "keep_alive": "1m"}
        )
        await self.es.close_point_in_time(id=self.pit)
        self.pit = None
        return out

    async def _process_inner_pag_query(self):
        if self.search_after is None:
            self.body["size"] = min(self.search_from, MAX_ES_SEARCH_FROM_SIZE)
            self.body["from"] = 0
        else:
            self.body["size"] = min(
                MAX_ES_SEARCH_FROM_SIZE, self.search_from - self.accum_shift
            )
        resp = await self.es.search(
            body=self.body, pit={"id": self.pit, "keep_alive": "1m"}
        )
        self.accum_shift += len(resp["hits"]["hits"])
        self.search_after = resp["hits"]["hits"][-1]["sort"]
        self.body["search_after"] = self.search_after
        if "from" in self.body:
            del self.body["from"]
