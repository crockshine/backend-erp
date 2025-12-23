from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.reports.schemas import ReportsResponse
from src.reports.service import ReportsService
from src.database import get_db

router = APIRouter(prefix="/reports")


@router.get("/", response_model=ReportsResponse)
async def get_reports(
    db: AsyncSession = Depends(get_db),
    top_employees_limit: int = Query(3, ge=1, le=10, description="Количество лучших сотрудников"),
    top_products_limit: int = Query(10, ge=1, le=50, description="Количество самых продаваемых товаров")
):
    """
    Получить отчеты: лучшие сотрудники и самые продаваемые товары

    Returns:
        - top_employees: топ сотрудников по выручке (до 3)
        - top_products: топ продаваемых товаров (до 10)
    """
    top_employees = await ReportsService.get_top_employees(db, top_employees_limit)
    top_products = await ReportsService.get_top_products(db, top_products_limit)

    return ReportsResponse(
        top_employees=top_employees,
        top_products=top_products
    )

