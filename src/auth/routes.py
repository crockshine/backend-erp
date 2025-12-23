from fastapi import APIRouter, status, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import (
    LoginDto,
    CreateEmployeeDto,
    UpdateEmployeeDto,
    EmployeeResponse
)
from src.auth.service import AuthService
from src.database import get_db

router = APIRouter()


@router.post("/login", response_model=EmployeeResponse, status_code=status.HTTP_200_OK)
async def login(login_dto: LoginDto, db: AsyncSession = Depends(get_db)):
    """
    Авторизация сотрудника

    - **email**: Email сотрудника
    - **password**: Пароль
    """
    employee = await AuthService.login(db, login_dto)
    return employee


@router.post("/create-employee", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(create_dto: CreateEmployeeDto, db: AsyncSession = Depends(get_db)):
    """
    Создать нового сотрудника (только для ADMIN)

    - **role**: Роль (ADMIN или SELLER)
    - **name**: Имя
    - **lastname**: Фамилия
    - **patronymic**: Отчество (необязательно)
    - **email**: Email
    - **password**: Пароль
    """
    employee = await AuthService.create_employee(db, create_dto)
    return employee


@router.get("/employees", response_model=List[EmployeeResponse])
async def get_all_employees(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех сотрудников
    """
    employees = await AuthService.get_all_employees(db)
    return employees


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: str, update_dto: UpdateEmployeeDto, db: AsyncSession = Depends(get_db)):
    """
    Обновить данные сотрудника

    - **employee_id**: ID сотрудника
    """
    employee = await AuthService.update_employee(db, employee_id, update_dto)
    return employee


@router.delete("/employees/{employee_id}", response_model=EmployeeResponse)
async def delete_employee(employee_id: str, db: AsyncSession = Depends(get_db)):
    """
    Удалить сотрудника

    - **employee_id**: ID сотрудника
    """
    employee = await AuthService.delete_employee(db, employee_id)
    return employee

