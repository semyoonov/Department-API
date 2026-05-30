from pydantic import BaseModel
from datetime import date


class DepartmentCreate(BaseModel):
    name: str
    parent_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None


class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    hired_at: date | None = None