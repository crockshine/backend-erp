"""Seed script to create only administrator user"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker
from src.models import Employee, EmployeeRole
from src.auth.service import AuthService


async def seed_admin():
    async with async_session_maker() as session:
        admin = Employee(
            role=EmployeeRole.ADMIN,
            name="Админ",
            lastname="Администратор",
            patronymic=None,
            email="admin@admin.com",
            password=AuthService.hash_password("admin123")
        )
        session.add(admin)
        await session.commit()
        print("✓ Администратор создан (email: admin@admin.com, password: admin123)")


if __name__ == "__main__":
    asyncio.run(seed_admin())

