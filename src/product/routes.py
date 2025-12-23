from fastapi import APIRouter, Query, status, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.product.schemas import (
    CreateProductDto,
    UpdateProductDto,
    ProductResponse,
    FilterOptionsResponse,
    CreateSaleDto,
    SaleResponse,
    CreateCategoryDto,
    CategoryResponse,
    CreateColorDto,
    ColorResponse,
    CreateSizeDto,
    SizeResponse
)
from src.product.service import ProductService
from src.database import get_db

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(create_dto: CreateProductDto, db: AsyncSession = Depends(get_db)):
    """
    Создать новый продукт
    """
    product = await ProductService.create_product(db, create_dto)
    return product


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    category_ids: Optional[List[str]] = Query(None, description="Фильтр по категориям"),
    color_ids: Optional[List[str]] = Query(None, description="Фильтр по цветам"),
    sizes: Optional[List[int]] = Query(None, description="Фильтр по размерам"),
    seasons: Optional[List[str]] = Query(None, description="Фильтр по сезонам"),
    offset: int = Query(0, ge=0, description="Смещение"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит")
):
    """
    Поиск продуктов с фильтрами

    Возвращает продукты с информацией об остатках на складе
    """
    products = await ProductService.get_products_with_filters(
        db, search, category_ids, color_ids, sizes, seasons, offset, limit
    )
    return products


@router.get("/filters", response_model=FilterOptionsResponse)
async def get_filter_options(db: AsyncSession = Depends(get_db)):
    """
    Получить все доступные опции для фильтров

    Возвращает:
    - categories: список всех категорий
    - colors: список всех цветов
    - sizes: список всех размеров
    - seasons: список всех сезонов
    """
    options = await ProductService.get_filter_options(db)
    return options


@router.post("/sale", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_dto: CreateSaleDto,
    db: AsyncSession = Depends(get_db),
    employee_id: str = Query(..., description="ID сотрудника")
):
    """
    Создать продажу

    Списывает товары со склада и создает запись о продаже
    """
    sale = await ProductService.create_sale(db, sale_dto, employee_id)
    return sale


@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    """
    Удалить продукт
    """
    product = await ProductService.delete_product(db, product_id)
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, update_dto: UpdateProductDto, db: AsyncSession = Depends(get_db)):
    """
    Обновить продукт
    """
    product = await ProductService.update_product(db, product_id, update_dto)
    return product


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(create_dto: CreateCategoryDto, db: AsyncSession = Depends(get_db)):
    """
    Создать новую категорию
    """
    category = await ProductService.create_category(db, create_dto)
    return category


@router.delete("/categories/{category_id}", response_model=CategoryResponse)
async def delete_category(category_id: str, db: AsyncSession = Depends(get_db)):
    """
    Удалить категорию
    """
    category = await ProductService.delete_category(db, category_id)
    return category


@router.post("/colors", response_model=ColorResponse, status_code=status.HTTP_201_CREATED)
async def create_color(create_dto: CreateColorDto, db: AsyncSession = Depends(get_db)):
    """
    Создать новый цвет
    """
    color = await ProductService.create_color(db, create_dto)
    return color


@router.delete("/colors/{color_id}", response_model=ColorResponse)
async def delete_color(color_id: str, db: AsyncSession = Depends(get_db)):
    """
    Удалить цвет
    """
    color = await ProductService.delete_color(db, color_id)
    return color


@router.post("/sizes", response_model=SizeResponse, status_code=status.HTTP_201_CREATED)
async def create_size(create_dto: CreateSizeDto, db: AsyncSession = Depends(get_db)):
    """
    Создать новый размер
    """
    size = await ProductService.create_size(db, create_dto.value)
    return size


@router.delete("/sizes/{size_value}", response_model=SizeResponse)
async def delete_size(size_value: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить размер
    """
    size = await ProductService.delete_size(db, size_value)
    return size


@router.get("/sales")
async def get_sales(
    db: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0, description="Смещение"),
    limit: int = Query(100, ge=1, le=1000, description="Лимит")
):
    """
    Получить список всех продаж с информацией о сотрудниках и товарах
    """
    sales = await ProductService.get_sales(db, offset, limit)
    return sales


