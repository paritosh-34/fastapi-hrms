from app.deps import DbSession, Filters
from app.models.employee import Employee
from app.schemas.common import Page
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services import employees as svc
from fastapi import APIRouter, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/employees", tags=["employees"])


async def _get_or_404(db: AsyncSession, employee_id: int) -> Employee:
    emp = await svc.get_employee(db, employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return emp


@router.get("", response_model=Page[EmployeeRead], summary="List employees")
async def list_employees(db: DbSession, f: Filters):
    """Search, filter, sort and paginate employees."""
    return await svc.page_of_employees(db, f)


@router.post(
    "", response_model=EmployeeRead, status_code=201, summary="Create an employee"
)
async def create_employee(payload: EmployeeCreate, db: DbSession):
    """Create an employee. Returns the new record without salary."""
    dup = await db.scalars(
        select(Employee).where(Employee.work_email == payload.work_email)
    )
    if dup.one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Email already in use")
    emp = Employee(**payload.model_dump())
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.get("/{employee_id}", response_model=EmployeeRead, summary="Get one employee")
async def get_employee(employee_id: int, db: DbSession):
    """Fetch a single employee by numeric id."""
    return await _get_or_404(db, employee_id)


@router.patch(
    "/{employee_id}", response_model=EmployeeRead, summary="Update an employee"
)
async def update_employee(employee_id: int, payload: EmployeeUpdate, db: DbSession):
    """Change only the fields that are present in the request body."""
    emp = await _get_or_404(db, employee_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.delete("/{employee_id}", status_code=204, summary="Delete an employee")
async def delete_employee(employee_id: int, db: DbSession) -> None:
    """Delete an employee. Anyone they managed is left with no manager."""
    emp = await _get_or_404(db, employee_id)
    await db.execute(
        update(Employee)
        .where(Employee.manager_id == employee_id)
        .values(manager_id=None)
    )
    await db.delete(emp)
    await db.commit()


@router.get(
    "/{employee_id}/reports",
    response_model=Page[EmployeeRead],
    summary="List an employee's direct reports",
)
async def list_reports(employee_id: int, db: DbSession, f: Filters):
    """Employees whose manager is the given employee."""
    await _get_or_404(db, employee_id)
    base = select(Employee).where(Employee.manager_id == employee_id)
    return await svc.page_of_employees(db, f, base)
