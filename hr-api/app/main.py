from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base, engine, get_db
from app.models import Department, Employee, Role
from app.schemas import (
    DepartmentCreate, DepartmentRead, DepartmentUpdate,
    EmployeeCreate, EmployeeRead, EmployeeUpdate,
)

from typing import Literal

from fastapi import Query
from sqlalchemy import Select, func, or_

from app.models import EmploymentStatus
from app.schemas import Page

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables on startup (Alembic migrations come much later)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="HR API",
    description="Employees, departments and leave for a small company.",
    version="0.1.0",
    lifespan=lifespan,
)

# One alias, reused everywhere: "a request-scoped session"
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_employee_or_404(db: AsyncSession, employee_id: int) -> Employee:
    result = await db.scalars(select(Employee).where(Employee.id == employee_id))
    emp = result.one_or_none()
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return emp


async def get_department_or_404(db: AsyncSession, department_id: int) -> Department:
    result = await db.scalars(select(Department).where(Department.id == department_id))
    dept = result.one_or_none()
    if dept is None:
        raise HTTPException(status_code=404, detail=f"Department {department_id} not found")
    return dept


@app.get("/health", summary="Liveness check")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# ---------- employees ----------

@app.get("/employees", response_model=Page[EmployeeRead], summary="List employees")
async def list_employees(db: DbSession, f: Filters):
    """Search, filter, sort and paginate employees."""
    return await page_of_employees(db, f, select(Employee))


@app.get(
    "/employees/{employee_id}/reports",
    response_model=Page[EmployeeRead],
    summary="List an employee's direct reports",
)
async def list_reports(employee_id: int, db: DbSession, f: Filters):
    """Employees whose manager is the given employee."""
    await get_employee_or_404(db, employee_id)       # 404 if the manager is unknown
    base = select(Employee).where(Employee.manager_id == employee_id)
    return await page_of_employees(db, f, base)


@app.get("/employees/{employee_id}", response_model=EmployeeRead, summary="Get one employee")
async def get_employee(employee_id: int, db: DbSession):
    """Fetch a single employee by numeric id."""
    return await get_employee_or_404(db, employee_id)


@app.post("/employees", response_model=EmployeeRead, status_code=201, summary="Create an employee")
async def create_employee(payload: EmployeeCreate, db: DbSession):
    """Create an employee. Returns the new record without salary."""
    dup = await db.scalars(select(Employee).where(Employee.work_email == payload.work_email))
    if dup.one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Email already in use")
    emp = Employee(**payload.model_dump())
    db.add(emp)
    await db.commit()
    await db.refresh(emp)        # loads the generated id and defaults
    return emp


@app.patch("/employees/{employee_id}", response_model=EmployeeRead, summary="Update an employee")
async def update_employee(employee_id: int, payload: EmployeeUpdate, db: DbSession):
    """Change only the fields that are present in the request body."""
    emp = await get_employee_or_404(db, employee_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(emp, field, value)
    await db.commit()
    await db.refresh(emp)
    return emp


@app.delete("/employees/{employee_id}", status_code=204, summary="Delete an employee")
async def delete_employee(employee_id: int, db: DbSession) -> None:
    """Delete an employee. Anyone they managed is left with no manager."""
    emp = await get_employee_or_404(db, employee_id)
    await db.execute(
        update(Employee).where(Employee.manager_id == employee_id).values(manager_id=None)
    )
    await db.delete(emp)
    await db.commit()


# ---------- departments ----------

@app.get("/departments", response_model=list[DepartmentRead], summary="List departments")
async def list_departments(db: DbSession):
    """List all departments ordered by department_name."""
    result = await db.scalars(select(Department).order_by(Department.department_name))
    return result.all()


@app.post("/departments", response_model=DepartmentRead, status_code=201, summary="Create a department")
async def create_department(payload: DepartmentCreate, db: DbSession):
    """Create a department. Names are unique."""
    dup = await db.scalars(select(Department).where(Department.department_name == payload.department_name))
    if dup.one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Department name already in use")
    dept = Department(**payload.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@app.get("/departments/{department_id}", response_model=DepartmentRead, summary="Get one department")
async def get_department(department_id: int, db: DbSession):
    """Fetch a single department by numeric id."""
    return await get_department_or_404(db, department_id)


@app.patch("/departments/{department_id}", response_model=DepartmentRead, summary="Update a department")
async def update_department(department_id: int, payload: DepartmentUpdate, db: DbSession):
    """Change only the fields that are present in the request body."""
    dept = await get_department_or_404(db, department_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dept, field, value)
    await db.commit()
    await db.refresh(dept)
    return dept


@app.get(
    "/departments/{department_id}/employees",
    response_model=Page[EmployeeRead],
    summary="List employees in a department",
)
async def list_department_employees(department_id: int, db: DbSession, f: Filters):
    """Everyone in one department, with the same filters as /employees."""
    await get_department_or_404(db, department_id)
    f.department_id = department_id                   # path wins over the query string
    return await page_of_employees(db, f, select(Employee))


# ---------- employee page filters ----------

def apply_filters(stmt: Select, f: EmployeeFilters) -> Select:
    if f.department_id is not None:
        stmt = stmt.where(Employee.department_id == f.department_id)
    if f.role is not None:
        stmt = stmt.where(Employee.role == f.role)
    if f.emp_status is not None:
        stmt = stmt.where(Employee.emp_status == f.emp_status)
    if f.q:
        like = f"%{f.q}%"
        stmt = stmt.where(or_(Employee.name.ilike(like), Employee.work_email.ilike(like)))
    return stmt


async def page_of_employees(db: AsyncSession, f: EmployeeFilters, base: Select) -> dict:
    base = apply_filters(base, f)
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    sort_col = {"name": Employee.name, "date_joined": Employee.date_joined, "salary": Employee.salary}[f.sort_by]
    ordering = sort_col.asc() if f.order == "asc" else sort_col.desc()
    stmt = base.order_by(ordering, Employee.id).offset(f.offset).limit(f.limit)
    items = (await db.scalars(stmt)).all()
    return {"items": items, "total": total or 0, "limit": f.limit, "offset": f.offset}
