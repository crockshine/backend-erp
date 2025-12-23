from pydantic import BaseModel
from typing import List


class TopEmployeeResponse(BaseModel):
    """Схема ответа для топ сотрудника"""
    id: str
    name: str
    lastname: str
    patronymic: str | None
    totalRevenue: float  # Общая выручка
    totalSales: int  # Товаров продано


class TopProductResponse(BaseModel):
    """Схема ответа для топ товара"""
    id: str
    name: str
    size: int
    colorId: str
    colorName: str
    categoryId: str
    categoryName: str
    price: float
    season: str
    availableCount: int
    totalSold: int  # Количество проданных

