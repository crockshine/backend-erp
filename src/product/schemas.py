from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CreateProductDto(BaseModel):
    name: str = Field(..., min_length=1, description="Название продукта")
    size: int = Field(..., description="Размер")
    price: float = Field(default=0, description="Цена (устанавливается при закупке)")
    season: str = Field(..., description="Сезон (FALL, WINTER, SPRING, SUMMER)")
    colorId: str = Field(..., description="ID цвета")
    categoryId: str = Field(..., description="ID категории")


class UpdateProductDto(BaseModel):
    name: Optional[str] = None
    size: Optional[int] = None
    price: Optional[float] = None
    season: Optional[str] = None
    colorId: Optional[str] = None
    categoryId: Optional[str] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    size: int
    price: float
    season: str
    colorId: str
    categoryId: str
    colorName: Optional[str] = None
    categoryName: Optional[str] = None
    availableCount: Optional[int] = 0

    class Config:
        from_attributes = True


class FilterOptionsResponse(BaseModel):
    categories: List[dict]
    colors: List[dict]
    sizes: List[int]
    seasons: List[str]


class SaleItemDto(BaseModel):
    productId: str
    count: int = Field(..., gt=0, description="Количество товара")


class CreateSaleDto(BaseModel):
    items: List[SaleItemDto] = Field(..., min_length=1, description="Товары для продажи")


class SaleResponse(BaseModel):
    id: str
    finalPrice: float
    employeeId: str
    createdAt: datetime

    class Config:
        from_attributes = True


class CreateCategoryDto(BaseModel):
    name: str = Field(..., min_length=1, description="Название категории")


class CategoryResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class CreateColorDto(BaseModel):
    name: str = Field(..., min_length=1, description="Название цвета")


class ColorResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class CreateSizeDto(BaseModel):
    value: int = Field(..., description="Значение размера")


class SizeResponse(BaseModel):
    id: str
    value: int

    class Config:
        from_attributes = True

