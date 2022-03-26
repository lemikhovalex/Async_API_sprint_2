from dataclasses import dataclass
from functools import lru_cache
from typing import Any, List, Optional, Tuple, Generator
from uuid import UUID, uuid1
from math import ceil

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, RequestError
from elasticsearch.exceptions import NotFoundError
from fastapi import Depends
from models.film import Film
from .base import BaseService
import logging

logger = logging.getLogger(__name__)
MAX_ES_SEARCH_FROM_SIZE = int(1e3)


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
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из
        # json
        film = ESFilm.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        return
        # await self.redis.set(
        #     film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS
        # )

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

        resp = await paginate_es_query(
            body=body, index=self._index_name(),
            pagination_shift=(page_number - 1) * page_size, size=page_size,
            es=self.elastic
        )
        # resp = await self.elastic.search(
        #     index=self._index_name(),
        #     body=body,
        # )
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


@dataclass
class InnerPagQueryData:
    body: dict
    accum_shift: int
    search_after: Any


async def paginate_es_query(
    body: dict,
    index: str,
    pagination_shift: int,
    size: int,
    es: AsyncElasticsearch
):
    search_after = None
    n = ceil(pagination_shift / MAX_ES_SEARCH_FROM_SIZE)
    # make shure that search after point to the beginning of page
    pag_process_data = InnerPagQueryData(
        body=body,
        accum_shift=0,
        search_after=None
    )
    for _ in range(n):
        await _process_inner_pag_query(
            es=es,
            pag_shift=pagination_shift,
            index=index,
            pag_process=pag_process_data,
        )
        logger.info(pag_process_data)

    pag_process_data.body["size"] = size
    
    logger.info(pag_process_data)
    logger.info(pag_process_data)
    return await es.search(
        index=index,
        body=pag_process_data.body,
    )


async def _process_inner_pag_query(
    es: AsyncElasticsearch,
    pag_shift: int,
    index: str,
    pag_process: InnerPagQueryData
):
    if pag_process.search_after is None:
        logger.info("no search after")
        pag_process.body["size"] = min(pag_shift, MAX_ES_SEARCH_FROM_SIZE)
        pag_process.body["from"] = 0
    else:
        logger.info("with search after")
        pag_process.body["size"] = min(
            MAX_ES_SEARCH_FROM_SIZE,
            pag_shift - pag_process.accum_shift
        )
    resp = await es.search(
        index=index,
        body=pag_process.body,
    )
    pag_process.accum_shift += pag_process.body["size"]
    pag_process.search_after = resp["hits"]["hits"][-1]["sort"]
    pag_process.body["search_after"] = pag_process.search_after
    if 'from' in pag_process.body:
        del pag_process.body['from']
