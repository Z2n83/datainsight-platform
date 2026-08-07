"""
Pagination utility for list endpoints.
"""
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Common pagination query parameters."""
    page: int = 1
    page_size: int = 20
    keyword: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated API response."""
    list: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "PaginatedResponse":
        return cls(
            list=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=max(1, (total + page_size - 1) // page_size),
        )
