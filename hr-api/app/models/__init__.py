# Importing every model here registers it on Base.metadata.
from app.models.base import Base
from app.models.department import Department
from app.models.employee import Employee, EmploymentStatus, Role

__all__ = ["Base", "Department", "Employee", "EmploymentStatus", "Role"]
