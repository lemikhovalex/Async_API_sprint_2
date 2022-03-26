from dataclasses import dataclass
from functools import lru_cache
from typing import Any, List, Optional
from uuid import UUID
from math import ceil

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from fastapi import Depends
from models.film import Film
from .base import BaseService

MAX_ES_SEARCH_FROM_SIZE = int(10)


class FilmService(BaseService):

    def _index_name(self):
        return 'movies'

    def _result_class(self):
        return Film

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может
    # отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще
                # нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        out = None
        try:
            doc = await self.elastic.get(index=self._index_name(), id=film_id)
            out = Film(**doc["_source"])
        except NotFoundError:
            pass
        return out

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        return None

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        return

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
        # TODO try get from redis
        # TODO what is key and val for redis? query params or query body
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
                        "query": {
                            "term": {
                                "genres.id": {
                                    "value": genre_filter
                                }
                            }
                        }
                    }
                }
            )

        if sort_by is not None:
            order = "desc"
            if sort_by.startswith("-"):
                order = "asc"
                sort_by = sort_by[1:]
            body["sort"][0][sort_by] = {"order": order}
        else:
            body["sort"][0]["imdb_rating"] = {"order": "asc"}
        body['sort'].extend(
            [
                {_sf: {}} for _sf in unique_sort_fields
            ]
            
        )
        paginator = QueryPaginator(
            body=body, 
            es=self.elastic,
            index=self._index_name(),
            page_number=page_number,
            page_size=page_size
        )
        resp = await paginator.paginate_query()
        results_src = [datum["_source"] for datum in resp["hits"]["hits"]]
        return [
            Film(**src)
            for src in results_src
        ]


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)


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

    async def paginate_query(self):
        n = ceil(self.search_from / MAX_ES_SEARCH_FROM_SIZE)
        # make shure that search after point to the beginning of page
        for _ in range(n):
            await self._process_inner_pag_query()

        self.body["size"] = self.page_size
        
        return await self.es.search(
            index=self.index,
            body=self.body,
        )

    async def _process_inner_pag_query(self):
        if self.search_after is None:
            self.body["size"] = min(self.search_from, MAX_ES_SEARCH_FROM_SIZE)
            self.body["from"] = 0
        else:
            self.body["size"] = min(
                MAX_ES_SEARCH_FROM_SIZE,
                self.search_from - self.accum_shift
            )
        resp = await self.es.search(
            index=self.index,
            body=self.body,
        )
        self.accum_shift += len(resp["hits"]["hits"])
        self.search_after = resp["hits"]["hits"][-1]["sort"]
        self.body["search_after"] = self.search_after
        if 'from' in self.body:
            del self.body['from']
