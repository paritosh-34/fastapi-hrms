from datetime import date
from fastapi import FastAPI,HTTPException
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="HR API",
    description="Employees, departments and leave for a small company.",
    version="0.1.0",
)

class Role(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR_ADMIN = "hr_admin"

class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

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


class EmployeeRead(BaseModel):
    """What the API returns. Note: no salary."""
    id: int
    name: str
    work_email: EmailStr
    role: Role
    job_title: str
    date_joined: date
    emp_status: EmploymentStatus
    department_id: int | None
    manager_id: int | None

EMPLOYEES: list[dict] = [
    {"id": 1, "name": "Maya Chen", "work_email": "maya@acme.test", "role": "hr_admin",
     "job_title": "Head of People", "date_joined": "2019-02-11", "salary": 120000,
     "emp_status": "active", "department_id": 2, "manager_id": None},
    {"id": 2, "name": "Arjun Rao", "work_email": "arjun@acme.test", "role": "manager",
     "job_title": "Engineering Manager", "date_joined": "2020-06-01", "salary": 140000,
     "emp_status": "active", "department_id": 1, "manager_id": None},
    {"id": 3, "name": "Priya Nair", "work_email": "priya@acme.test", "role": "employee",
     "job_title": "Senior Engineer", "date_joined": "2021-03-15", "salary": 118000,
     "emp_status": "active", "department_id": 1, "manager_id": 2},
    {"id": 4, "name": "Tomas Weber", "work_email": "tomas@acme.test", "role": "employee",
     "job_title": "Frontend Engineer", "date_joined": "2022-09-05", "salary": 98000,
     "emp_status": "active", "department_id": 1, "manager_id": 2},
    {"id": 5, "name": "Lena Park", "work_email": "lena@acme.test", "role": "employee",
     "job_title": "Product Designer", "date_joined": "2023-01-16", "salary": 92000,
     "emp_status": "on_leave", "department_id": 3, "manager_id": 1},
]

@app.get("/health", summary="Liveness check")
async def health() -> dict[str, str]:
    """Returns ok when the server is up."""
    return {"status": "ok"}

@app.get("/employees", summary="List employees")
async def list_employees(role: Role | None = None, limit: int = 50) -> list[dict]:
    """List employees, optionally filtered by role."""
    # rows = [e for e in EMPLOYEES if role is None or e["role"] == role]
    rows = []
    for e in EMPLOYEES:
        if role is None:
            rows.append(e)
        elif role == e["role"]:
            rows.append(e)

    return rows[:limit]

@app.get("/employees/{employee_id}", summary="Get one employee")
async def get_employee(employee_id: int) -> dict:
    """Fetch a single employee by numeric id."""
    for e in EMPLOYEES:
        if e["id"] == employee_id:
            return e
    raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

@app.post( 
    "/employees",
    response_model=EmployeeRead,
    status_code=201,
    summary="Create an employee",
)
async def create_employee(payload: EmployeeCreate) -> dict:
    """Create an employee. Returns the new record without salary."""
    if any(e["work_email"] == payload.work_email for e in EMPLOYEES):
        raise HTTPException(status_code=409, detail="Email already in use")
    new = {
        "id": max(e["id"] for e in EMPLOYEES) + 1,
        **payload.model_dump(),
        "emp_status": "active",
    }
    EMPLOYEES.append(new)
    return new