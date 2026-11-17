from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Standard envelope for every list endpoint."""

    items: list[T]
    total: int = Field(description="Rows matching the filters, ignoring limit/offset")
    limit: int
    offset: int
