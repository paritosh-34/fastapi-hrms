from app.deps import EmployeeFilters
from app.models.employee import Employee
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_employee(db: AsyncSession, employee_id: int) -> Employee | None:
    result = await db.scalars(select(Employee).where(Employee.id == employee_id))
    return result.one_or_none()


def apply_filters(stmt: Select, f: EmployeeFilters) -> Select:
    if f.department_id is not None:
        stmt = stmt.where(Employee.department_id == f.department_id)
    if f.role is not None:
        stmt = stmt.where(Employee.role == f.role)
    if f.emp_status is not None:
        stmt = stmt.where(Employee.emp_status == f.emp_status)
    if f.q:
        like = f"%{f.q}%"
        stmt = stmt.where(
            or_(Employee.name.ilike(like), Employee.work_email.ilike(like))
        )
    return stmt


async def page_of_employees(
    db: AsyncSession, f: EmployeeFilters, base: Select | None = None
) -> dict:
    base = apply_filters(base if base is not None else select(Employee), f)
    total = await db.scalar(select(func.count()).select_from(base.subquery()))
    sort_col = {
        "name": Employee.name,
        "date_joined": Employee.date_joined,
        "salary": Employee.salary,
    }[f.sort_by]
    ordering = sort_col.asc() if f.order == "asc" else sort_col.desc()
    stmt = base.order_by(ordering, Employee.id).offset(f.offset).limit(f.limit)
    items = (await db.scalars(stmt)).all()
    return {"items": items, "total": total or 0, "limit": f.limit, "offset": f.offset}
