from functools import lru_cache
from typing import List, Optional
from uuid import UUID, uuid1

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, RequestError
from elasticsearch.exceptions import NotFoundError
from fastapi import Depends
from models.film import Film
from models.genre import Genre
from .base import BaseService


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
        await self.redis.set(
            film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def get_by_query(
        self,
        query: Optional[str] = None,
        page_size: int = 50,
        page_number: int = 1,
        sort_by: Optional[str] = "imdb_rating",
        genre_filter: Optional[UUID] = "comedy",
    ) -> List[Film]:
        # TODO try get from redis
        # TODO what is key and val for redis? query params or query body
        body = {
            "size": page_size,
            "from": page_size * (page_number - 1),
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
            body["sort"][0]["imdb_rating"] = {"order": "desc"}
        resp = await self.elastic.search(
            index=self._index_name(),
            body=body,
        )
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
