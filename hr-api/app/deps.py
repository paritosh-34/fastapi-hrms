from collections.abc import AsyncIterator
from typing import Annotated, Literal

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.models.employee import EmploymentStatus, Role


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


class EmployeeFilters:
    def __init__(
        self,
        department_id: int | None = None,
        role: Role | None = None,
        emp_status: EmploymentStatus | None = None,
        q: Annotated[str | None, Query(description="Search name or work email", max_length=100)] = None,
        sort_by: Literal["name", "date_joined", "salary"] = "name",
        order: Literal["asc", "desc"] = "asc",
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> None:
        self.department_id = department_id
        self.role = role
        self.emp_status = emp_status
        self.q = q
        self.sort_by = sort_by
        self.order = order
        self.limit = limit
        self.offset = offset


Filters = Annotated[EmployeeFilters, Depends()]