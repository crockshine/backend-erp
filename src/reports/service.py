from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List
from src.models import Employee, Sale, ProductToSale, Product, ProductColor, ProductCategory, ProductSize, ShopRest
from src.reports.schemas import TopEmployeeResponse, TopProductResponse


class ReportsService:
    """Сервис для работы с отчетами"""

    @staticmethod
    async def get_top_employees(db: AsyncSession, limit: int = 3) -> List[TopEmployeeResponse]:
        """
        Получить топ сотрудников по выручке

        Args:
            db: сессия базы данных
            limit: количество сотрудников (по умолчанию 3)

        Returns:
            Список лучших сотрудников
        """
        # Подзапрос для подсчета общей выручки и количества проданных товаров по каждому сотруднику
        stmt = (
            select(
                Employee.id,
                Employee.name,
                Employee.lastname,
                Employee.patronymic,
                Employee.role,
                func.coalesce(func.sum(Sale.finalPrice), 0).label('total_revenue'),
                func.coalesce(func.sum(ProductToSale.count), 0).label('products_sold')
            )
            .outerjoin(Sale, Employee.id == Sale.employeeId)
            .outerjoin(ProductToSale, Sale.id == ProductToSale.saleId)
            .group_by(Employee.id, Employee.name, Employee.lastname, Employee.patronymic, Employee.role)
            .order_by(desc('total_revenue'))
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        employees = []
        for row in rows:
            employees.append(TopEmployeeResponse(
                id=row.id,
                name=row.name,
                lastname=row.lastname,
                patronymic=row.patronymic,
                role=row.role,
                total_revenue=float(row.total_revenue),
                products_sold=int(row.products_sold)
            ))

        return employees

    @staticmethod
    async def get_top_products(db: AsyncSession, limit: int = 10) -> List[TopProductResponse]:
        """
        Получить топ продаваемых товаров

        Args:
            db: сессия базы данных
            limit: количество товаров (по умолчанию 10)

        Returns:
            Список самых продаваемых товаров
        """
        # Подзапрос для подсчета проданных товаров
        stmt = (
            select(
                Product,
                ProductColor,
                ProductCategory,
                ProductSize,
                ShopRest,
                func.coalesce(func.sum(ProductToSale.count), 0).label('total_sold')
            )
            .outerjoin(ProductToSale, Product.id == ProductToSale.ProductId)
            .join(ProductColor, Product.colorId == ProductColor.id)
            .join(ProductCategory, Product.categoryId == ProductCategory.id)
            .join(ProductSize, Product.sizeId == ProductSize.id)
            .outerjoin(ShopRest, Product.id == ShopRest.productId)
            .group_by(Product.id, ProductColor.id, ProductCategory.id, ProductSize.id, ShopRest.id)
            .order_by(desc('total_sold'))
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        products = []
        for row in rows:
            product = row[0]
            color = row[1]
            category = row[2]
            size = row[3]
            shop_rest = row[4]
            total_sold = int(row[5])

            products.append(TopProductResponse(
                id=product.id,
                name=product.name,
                sizeValue=size.value if size else 0,
                price=product.price,
                season=product.season.value,
                colorId=product.colorId,
                categoryId=product.categoryId,
                colorName=color.name,
                categoryName=category.name,
                total_sold=total_sold,
                rest_count=shop_rest.restCount if shop_rest else 0
            ))

        return products

