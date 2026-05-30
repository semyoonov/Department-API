from fastapi import APIRouter, HTTPException, Response, status
from app.models import Department, Employee
from app.database.database import SessionLocal
from app.api.schemas import DepartmentCreate, DepartmentUpdate, EmployeeCreate
from sqlalchemy.orm import Session
from sqlalchemy import update

router = APIRouter()

#1 - create department
@router.post('/departments/')
async def create_department(body: DepartmentCreate):
    name = body.name.strip()
    if name == "" or len(name) > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name format.")

    with SessionLocal() as db:
        new_department = Department(
            name=name,
            parent_id=body.parent_id,
        )

        if body.parent_id:
            same_name_dept = db.query(Department).filter(Department.parent_id == body.parent_id, Department.name == name).first()
            if same_name_dept:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There's another department with the same name.")
            
            parent_id_dept = db.query(Department).filter(Department.id == body.parent_id).first()
            if not parent_id_dept:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There's no such a parent_id department.")


        db.add(new_department)
        db.commit()
        db.refresh(new_department)

        return {
            "id": new_department.id,
            "name": new_department.name,
            "parent_id": new_department.parent_id,
            "created_at": new_department.created_at
        }


#2 - create employee
@router.post('/departments/{id}/employees/')
async def create_employee(id : int, body: EmployeeCreate):
    full_name = body.full_name.strip()
    position = body.position.strip()

    if full_name == "" or len(full_name) > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid full_name format.")
    if position == "" or len(position) > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid position format.")

    with SessionLocal() as db:

        department = db.query(Department).filter(Department.id == id).first()
        if not department:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department doesn't exist.")

        new_employee = Employee(
            department_id=id,
            full_name=full_name,
            position=position,
            hired_at=body.hired_at
        )

        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)

        return {
            "id": new_employee.id,
            "department_id": new_employee.department_id,
            "full_name": new_employee.full_name,
            "position": new_employee.position,
            "hired_at": new_employee.hired_at,
            "created_at": new_employee.created_at
        }

#help func
async def get_recursive_department(dept : Department, depth : int, include_employees : bool, db : Session):

    if include_employees:
        employees = db.query(Employee).filter(Employee.department_id == dept.id).order_by(Employee.full_name).all()
        employees = [
                {
                    'id' : x.id, 
                    'department_id' : x.department_id, 
                    'full_name' : x.full_name, 
                    'position' : x.position, 
                    'hired_at' : x.hired_at, 
                    'created_at' : x.created_at
                } 
                for x in employees
            ]
    else:
        employees = []

    if depth <= 0:
        children = []
    else:
        children = []
        for x in db.query(Department).filter(Department.parent_id == dept.id).all():
            children.append(await get_recursive_department(x, depth - 1, include_employees, db))

    return {
        'department' : {'id' : dept.id, 'name' : dept.name, 'parent_id' : dept.parent_id, 'created_at' : dept.created_at},
        'employees' : employees,
        'children' : children
    }

#3 - get information about department
@router.get('/departments/{id}')
async def get_department(id : int, depth : int = 1, include_employees : bool = True):
    depth = min(depth, 5)
    with SessionLocal() as db:
        dept = db.query(Department).filter(Department.id == id).first()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department doesn't exist.")
        return await get_recursive_department(dept, depth, include_employees, db)


#4 - edit department
@router.patch('/departments/{id}')
async def move_department(id : int, body: DepartmentUpdate):
    if body.name is not None:
        name = body.name.strip()
        if name == "" or len(name) > 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name format.")

    with SessionLocal() as db:
        dept = db.query(Department).filter(Department.id == id).first()
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department doesn't exist.")
        
        if 'parent_id' in body.model_fields_set:
            if body.parent_id == dept.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Department.parent_id should be different from the Department.id")

            temp_parent_id = body.parent_id
            while temp_parent_id is not None:
                temp_parent_id = db.query(Department).filter(Department.id == temp_parent_id).first()
                
                if temp_parent_id is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department doesn't exist")
                if temp_parent_id.id == dept.id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cycle detected.")
                
                temp_parent_id = temp_parent_id.parent_id

            dept.parent_id = body.parent_id
        
        if body.name is not None:
            dept.name = body.name.strip()

        db.add(dept)
        db.commit()
        db.refresh(dept)

        return {
            "id": dept.id,
            "name": dept.name,
            "parent_id": dept.parent_id,
            "created_at": dept.created_at
        }

#5 - delete department
@router.delete('/departments/{id}')
async def delete_department(id : int, mode : str = 'cascade', reassign_to_department_id : int | None = None):
    with SessionLocal() as db:
        dept = db.get(Department, id)
        if not dept:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

        if mode not in ['cascade', 'reassign']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect delete mode.")
        
        if mode == 'reassign':

            if reassign_to_department_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reassign_to_department_id is required.")
            
            if not db.get(Department, reassign_to_department_id):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target department not found.")

            if id == reassign_to_department_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot reassign to the same department.")
            
            temp = reassign_to_department_id
            while temp is not None:
                if temp == id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reassign cycle found.")
                dept_ = db.get(Department, temp)
                temp = dept_.parent_id
            
            db.execute(
                update(Employee)
                .where(Employee.department_id == id)
                .values(department_id=reassign_to_department_id)
            )

            db.execute(
                update(Department)
                .where(Department.parent_id == id)
                .values(parent_id=reassign_to_department_id)
            )
        
        db.delete(dept)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
