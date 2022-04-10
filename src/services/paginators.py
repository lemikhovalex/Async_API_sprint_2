from abc import ABC, abstractmethod
from math import ceil
from typing import Optional

from elasticsearch import AsyncElasticsearch

from core.config import MAX_ES_SEARCH_FROM_SIZE


class BasePaginator(ABC):
    @abstractmethod
    def __init__(
        self,
        query: dict,
        sort: list,
        es: AsyncElasticsearch,
        index: str,
        page_size: int,
        **kwargs
    ):
        pass

    @abstractmethod
    async def get_page(self, page_number: int) -> dict:
        pass


class ESQueryPaginator(BasePaginator):
    def __init__(
        self,
        query: dict,
        sort: list,
        es: AsyncElasticsearch,
        index: str,
        page_size: int,
        **kwargs
    ):
        self.query = query
        self.sort = sort
        self.es = es
        self.index = index
        self.page_size = page_size
        self.accum_shift = 0
        self.search_after = None
        self.pit = None
        self.search_add_args = kwargs

    async def get_page(self, page_number: int) -> dict:
        self.page_number = page_number
        self.search_from = (self.page_number - 1) * self.page_size
        n = ceil(self.search_from / MAX_ES_SEARCH_FROM_SIZE)
        self.pit = await self.es.open_point_in_time(index=self.index, keep_alive="1m")
        self.pit = self.pit["id"]
        # make shure that search after point to the beginning of page
        for _ in range(n):
            await self._process_inner_pag_query()

        out = await self._search_after()
        await self.es.close_point_in_time(id=self.pit)
        self.pit = None
        return out

    async def _process_inner_pag_query(self) -> None:
        if self.search_after is None:
            resp = await self._initial_query()
        else:
            size = min(MAX_ES_SEARCH_FROM_SIZE, self.search_from - self.accum_shift)
            resp = await self._search_after(size=size)

        self.accum_shift += len(resp["hits"]["hits"])
        self.search_after = resp["hits"]["hits"][-1]["sort"]

    async def _search_after(self, size: Optional[int] = None):
        return await self.es.search(
            query=self.query,
            sort=self.sort,
            search_after=self.search_after,
            size=size or self.page_size,
            pit={"id": self.pit, "keep_alive": "1m"},
            **self.search_add_args
        )

    async def _initial_query(self):
        return await self.es.search(
            query=self.query,
            sort=self.sort,
            from_=0,
            size=min(self.search_from, MAX_ES_SEARCH_FROM_SIZE),
            pit={"id": self.pit, "keep_alive": "1m"},
            **self.search_add_args
        )
