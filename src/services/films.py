from functools import lru_cache

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from .base import BaseService


class FilmService(BaseService):

    def _index_name(self):
        return 'movies'

    def _result_class(self):
        return Film

    def _query_by_genre_id(self, genre_id):
        # TODO look for escape function or take it from php es client
        return {
            'nested': {
                'path': 'genres',
                'query': {
                    'term': {
                        'genres.id': genre_id
                    }
                }
            }
        }

    def _query_by_person_id(self, person_id):
        # TODO look for escape function or take from php es client
        def _q_nested(role, person_id):
            return {
                "nested": {
                    "path": role,
                    "query": {
                        "term": {
                            "%s.id"%role: {
                                "value": person_id
                            }
                        }
                    }
                }
            }

        roles = ('actors', 'directors', 'writers')

        return {"bool": {"should": [_q_nested(i, person_id) for i in roles]}}


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
