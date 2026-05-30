from datetime import datetime, date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from app.database.database import Base

class Department(Base):
    __tablename__ = "Departments"
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(nullable=False)
    parent_id : Mapped[int | None] = mapped_column(ForeignKey('Departments.id', ondelete='CASCADE'))
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())

class Employee(Base):
    __tablename__ = "Employees"
    id : Mapped[int] = mapped_column(primary_key=True)
    department_id : Mapped[int] = mapped_column(ForeignKey('Departments.id', ondelete='CASCADE'))
    full_name : Mapped[str] = mapped_column(nullable=False)
    position : Mapped[str] = mapped_column(nullable=False)
    hired_at : Mapped[date | None] = mapped_column(nullable=True)
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())