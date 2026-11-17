import asyncio
from datetime import date

from app.core.db import SessionLocal, engine
from app.models import Base, Department, Employee, EmploymentStatus, Role

DEPARTMENTS = [
    Department(id=1, department_name="Engineering", description="Builds the product"),
    Department(
        id=2, department_name="People Ops", description="Hiring, leave and payroll"
    ),
    Department(id=3, department_name="Design", description="Product and brand design"),
]

# Managers come first so the self-referencing manager_id always has a target.
EMPLOYEES = [
    Employee(
        id=1,
        name="Maya Chen",
        work_email="maya@acme.test",
        role=Role.HR_ADMIN,
        job_title="Head of People",
        date_joined=date(2019, 2, 11),
        salary=120000,
        department_id=2,
        manager_id=None,
    ),
    Employee(
        id=2,
        name="Arjun Rao",
        work_email="arjun@acme.test",
        role=Role.MANAGER,
        job_title="Engineering Manager",
        date_joined=date(2020, 6, 1),
        salary=140000,
        department_id=1,
        manager_id=None,
    ),
    Employee(
        id=3,
        name="Priya Nair",
        work_email="priya@acme.test",
        role=Role.EMPLOYEE,
        job_title="Senior Engineer",
        date_joined=date(2021, 3, 15),
        salary=118000,
        department_id=1,
        manager_id=2,
    ),
    Employee(
        id=4,
        name="Tomas Weber",
        work_email="tomas@acme.test",
        role=Role.EMPLOYEE,
        job_title="Frontend Engineer",
        date_joined=date(2022, 9, 5),
        salary=98000,
        department_id=1,
        manager_id=2,
    ),
    Employee(
        id=5,
        name="Lena Park",
        work_email="lena@acme.test",
        role=Role.EMPLOYEE,
        job_title="Product Designer",
        date_joined=date(2023, 1, 16),
        salary=92000,
        emp_status=EmploymentStatus.ON_LEAVE,
        department_id=3,
        manager_id=1,
    ),
]


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        db.add_all(DEPARTMENTS)
        await db.flush()  # departments exist before employees point at them
        db.add_all(EMPLOYEES)
        await db.commit()
    print(f"Seeded {len(DEPARTMENTS)} departments and {len(EMPLOYEES)} employees.")


if __name__ == "__main__":
    asyncio.run(main())
