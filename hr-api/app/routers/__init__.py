# One module per resource; each exposes `router`, which main.py mounts
# with app.include_router(...).
from app.routers import departments, employees, health

__all__ = ["departments", "employees", "health"]
