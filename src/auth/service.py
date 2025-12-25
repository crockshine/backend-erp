from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Employee
from src.auth.schemas import LoginDto, CreateEmployeeDto, UpdateEmployeeDto

# Используем argon2 вместо bcrypt - современный алгоритм без ограничений на длину
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Хэширование пароля через argon2 (без ограничений на длину)"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля через argon2"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def login(db: AsyncSession, login_dto: LoginDto):
        result = await db.execute(
            select(Employee).where(Employee.email == login_dto.email)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сотрудник не найден"
            )

        if not AuthService.verify_password(login_dto.password, employee.password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сотрудник не найден"
            )

        return employee

    @staticmethod
    async def create_employee(db: AsyncSession, create_dto: CreateEmployeeDto):
        """Создание нового сотрудника"""
        result = await db.execute(
            select(Employee).where(Employee.email == create_dto.email)
        )
        existing_employee = result.scalar_one_or_none()

        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Сотрудник с такой почтой уже существует"
            )

        hashed_password = AuthService.hash_password(create_dto.password)

        employee = Employee(
            role=create_dto.role,
            name=create_dto.name,
            lastname=create_dto.lastname,
            patronymic=create_dto.patronymic,
            email=create_dto.email,
            password=hashed_password
        )

        db.add(employee)
        await db.commit()
        await db.refresh(employee)

        return employee

    @staticmethod
    async def get_all_employees(db: AsyncSession):
        """Получить всех сотрудников"""
        result = await db.execute(select(Employee))
        employees = result.scalars().all()
        return employees

    @staticmethod
    async def update_employee(db: AsyncSession, employee_id: str, update_dto: UpdateEmployeeDto):
        """Обновить сотрудника"""
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сотрудник не найден"
            )

        update_data = update_dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(employee, key, value)

        await db.commit()
        await db.refresh(employee)

        return employee

    @staticmethod
    async def delete_employee(db: AsyncSession, employee_id: str):
        """Удалить сотрудника"""
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сотрудник не найден"
            )

        await db.delete(employee)
        await db.commit()

        return employee

