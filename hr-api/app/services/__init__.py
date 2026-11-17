# Query logic shared by routers. Each module is imported as a namespace,
# e.g. `from app.services import employees as svc`.
from app.services import employees

__all__ = ["employees"]
