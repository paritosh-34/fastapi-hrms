# Pydantic request/response shapes, re-exported so callers can write
# `from app.schemas import EmployeeRead` instead of the full module path.
from app.schemas.common import Page
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate

__all__ = [
    "DepartmentCreate",
    "DepartmentRead",
    "DepartmentUpdate",
    "EmployeeCreate",
    "EmployeeRead",
    "EmployeeUpdate",
    "Page",
]
