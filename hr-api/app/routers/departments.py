from app.deps import DbSession, Filters
from app.models.department import Department
from app.schemas.common import Page
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.schemas.employee import EmployeeRead
from app.services import employees as svc
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/departments", tags=["departments"])


async def _get_or_404(db: AsyncSession, department_id: int) -> Department:
    result = await db.scalars(select(Department).where(Department.id == department_id))
    dept = result.one_or_none()
    if dept is None:
        raise HTTPException(
            status_code=404, detail=f"Department {department_id} not found"
        )
    return dept


@router.get("", response_model=list[DepartmentRead], summary="List departments")
async def list_departments(db: DbSession):
    """List all departments ordered by department_name."""
    result = await db.scalars(select(Department).order_by(Department.department_name))
    return result.all()


@router.post(
    "", response_model=DepartmentRead, status_code=201, summary="Create a department"
)
async def create_department(payload: DepartmentCreate, db: DbSession):
    """Create a department. Names are unique."""
    dup = await db.scalars(
        select(Department).where(Department.department_name == payload.department_name)
    )
    if dup.one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Department name already in use")
    dept = Department(**payload.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.get(
    "/{department_id}", response_model=DepartmentRead, summary="Get one department"
)
async def get_department(department_id: int, db: DbSession):
    """Fetch a single department by numeric id."""
    return await _get_or_404(db, department_id)


@router.patch(
    "/{department_id}", response_model=DepartmentRead, summary="Update a department"
)
async def update_department(
    department_id: int, payload: DepartmentUpdate, db: DbSession
):
    """Change only the fields that are present in the request body."""
    dept = await _get_or_404(db, department_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dept, field, value)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.get(
    "/{department_id}/employees",
    response_model=Page[EmployeeRead],
    summary="List employees in a department",
)
async def list_department_employees(department_id: int, db: DbSession, f: Filters):
    """Everyone in one department, with the same filters as /employees."""
    await _get_or_404(db, department_id)
    f.department_id = department_id  # path wins over the query string
    return await svc.page_of_employees(db, f)
