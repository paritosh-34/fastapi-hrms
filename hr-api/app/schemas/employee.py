from datetime import date

from app.models.employee import EmploymentStatus, Role
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeCreate(BaseModel):
    """Body for creating an employee."""

    name: str = Field(min_length=2, max_length=100)
    work_email: EmailStr
    role: Role = Role.EMPLOYEE
    job_title: str = Field(min_length=1, max_length=100)
    date_joined: date
    salary: int = Field(ge=0, description="Annual salary in whole currency units")
    department_id: int | None = None
    manager_id: int | None = None


class EmployeeUpdate(BaseModel):
    """Partial update: send only the fields you want to change."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    role: Role | None = None
    job_title: str | None = Field(default=None, min_length=1, max_length=100)
    salary: int | None = Field(default=None, ge=0)
    emp_status: EmploymentStatus | None = None
    department_id: int | None = None
    manager_id: int | None = None


class EmployeeRead(BaseModel):
    """What the API returns. No salary."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    work_email: EmailStr
    role: Role
    job_title: str
    date_joined: date
    emp_status: EmploymentStatus
    department_id: int | None
    manager_id: int | None
