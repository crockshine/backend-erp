from pydantic import BaseModel
from typing import List


class TopEmployeeResponse(BaseModel):
    """Данные по лучшему сотруднику"""
    id: str
    name: str
    lastname: str
    patronymic: str | None
    role: str
    total_revenue: float
    products_sold: int

    class Config:
        from_attributes = True


class TopProductResponse(BaseModel):
    """Данные по самому продаваемому товару"""
    id: str
    name: str
    sizeValue: int
    price: float
    season: str
    colorId: str
    categoryId: str
    colorName: str
    categoryName: str
    total_sold: int
    rest_count: int

    class Config:
        from_attributes = True


class ReportsResponse(BaseModel):
    """Общий ответ с отчетами"""
    top_employees: List[TopEmployeeResponse]
    top_products: List[TopProductResponse]

