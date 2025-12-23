from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.discount.schemas import DiscountCreate, DiscountResponse
from src.discount.service import create_discount, get_all_discounts, delete_discount
from typing import List

router = APIRouter(prefix="/discounts", tags=["discounts"])


@router.post("/", response_model=DiscountResponse)
async def create_discount_route(
    discount_data: DiscountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую скидку"""
    try:
        return await create_discount(db, discount_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании скидки: {str(e)}")


@router.get("/", response_model=List[DiscountResponse])
async def get_discounts_route(
    db: AsyncSession = Depends(get_db)
):
    """Получить все скидки"""
    try:
        return await get_all_discounts(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении скидок: {str(e)}")


@router.delete("/{discount_id}")
async def delete_discount_route(
    discount_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Удалить скидку"""
    try:
        await delete_discount(db, discount_id)
        return {"message": "Скидка успешно удалена"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении скидки: {str(e)}")

