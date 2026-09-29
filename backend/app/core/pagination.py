from typing import Annotated, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
MAX_LIMIT = 100


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        return self.offset + len(self.items) < self.total


class PaginationParams:
    def __init__(
        self,
        limit: Annotated[int, Query(ge=1, le=MAX_LIMIT)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        self.limit = limit
        self.offset = offset


Pagination = Annotated[PaginationParams, ...]
