from datetime import date
from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Role(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR_ADMIN = "hr_admin"


class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


def _values(e: type[Enum]) -> list[str]:
    return [m.value for m in e]   # store "hr_admin", not "HR_ADMIN"


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(500))

    employees: Mapped[list["Employee"]] = relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    work_email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, native_enum=False, values_callable=_values), default=Role.EMPLOYEE
    )
    job_title: Mapped[str] = mapped_column(String(100))
    date_joined: Mapped[date]
    salary: Mapped[int]
    emp_status: Mapped[EmploymentStatus] = mapped_column(
        SAEnum(EmploymentStatus, native_enum=False, values_callable=_values),
        default=EmploymentStatus.ACTIVE,
    )
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))

    department: Mapped[Department | None] = relationship(back_populates="employees")
    # Self-referential: the "one" side. remote_side says which end is the parent.
    manager: Mapped["Employee | None"] = relationship(
        remote_side="Employee.id", back_populates="reports"
    )
    reports: Mapped[list["Employee"]] = relationship(back_populates="manager")