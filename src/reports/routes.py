from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from models import Employee, ProductToSale, Product, Color, ProductCategory
from .schemas import TopEmployeeResponse, TopProductResponse
from typing import List

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/top-employees", response_model=List[TopEmployeeResponse])
async def get_top_employees(
    limit: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить топ сотрудников по выручке
    """
    try:
        # Запрос для получения топ сотрудников
        query = (
            select(
                Employee.id,
                Employee.name,
                Employee.lastname,
                Employee.patronymic,
                func.sum(ProductToSale.count * Product.price).label('totalRevenue'),
                func.sum(ProductToSale.count).label('totalSales')
            )
            .join(ProductToSale, ProductToSale.EmployeeId == Employee.id)
            .join(Product, ProductToSale.ProductId == Product.id)
            .group_by(Employee.id, Employee.name, Employee.lastname, Employee.patronymic)
            .order_by(desc('totalRevenue'))
            .limit(limit)
        )

        result = await db.execute(query)
        employees = result.all()

        # Формируем ответ
        return [
            TopEmployeeResponse(
                id=str(emp.id),
                name=emp.name,
                lastname=emp.lastname,
                patronymic=emp.patronymic,
                totalRevenue=float(emp.totalRevenue or 0),
                totalSales=int(emp.totalSales or 0)
            )
            for emp in employees
        ]
    except Exception as e:
        print(f"[REPORTS] Ошибка при получении топ сотрудников: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("/top-products", response_model=List[TopProductResponse])
async def get_top_products(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить топ товаров по количеству продаж
    """
    try:
        # Запрос для получения топ товаров
        query = (
            select(
                Product.id,
                Product.name,
                Product.size,
                Product.colorId,
                Color.name.label('colorName'),
                Product.categoryId,
                ProductCategory.name.label('categoryName'),
                Product.price,
                Product.season,
                Product.availableCount,
                func.sum(ProductToSale.count).label('totalSold')
            )
            .join(ProductToSale, ProductToSale.ProductId == Product.id)
            .join(Color, Product.colorId == Color.id)
            .join(ProductCategory, Product.categoryId == ProductCategory.id)
            .group_by(
                Product.id,
                Product.name,
                Product.size,
                Product.colorId,
                Color.name,
                Product.categoryId,
                ProductCategory.name,
                Product.price,
                Product.season,
                Product.availableCount
            )
            .order_by(desc('totalSold'))
            .limit(limit)
        )

        result = await db.execute(query)
        products = result.all()

        # Формируем ответ
        return [
            TopProductResponse(
                id=str(prod.id),
                name=prod.name,
                size=prod.size,
                colorId=str(prod.colorId),
                colorName=prod.colorName,
                categoryId=str(prod.categoryId),
                categoryName=prod.categoryName,
                price=float(prod.price),
                season=prod.season,
                availableCount=prod.availableCount,
                totalSold=int(prod.totalSold or 0)
            )
            for prod in products
        ]
    except Exception as e:
        print(f"[REPORTS] Ошибка при получении топ товаров: {e}")
        import traceback
        traceback.print_exc()
        return []

