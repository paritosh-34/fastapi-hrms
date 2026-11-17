from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    department_name: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=1, max_length=500)


class DepartmentUpdate(BaseModel):
    department_name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_name: str
    description: str
