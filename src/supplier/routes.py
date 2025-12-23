from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.database import get_db
from src.supplier.schemas import (
    SupplierCreate,
    SupplierResponse,
    OrderCreate,
    OrderResponse
)
from src.supplier.service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("/", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать поставщика"""
    try:
        print(f"[SUPPLIER_ROUTE] Received request: {supplier_data}")
        result = await SupplierService.create_supplier(db, supplier_data)
        print(f"[SUPPLIER_ROUTE] Success: {result}")
        return result
    except Exception as e:
        print(f"[SUPPLIER_ROUTE] ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers(db: AsyncSession = Depends(get_db)):
    """Получить список поставщиков"""
    return await SupplierService.get_all_suppliers(db)


@router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать заказ поставщику"""
    try:
        print(f"[ORDER_ROUTE] Received order request: {order_data}")
        result = await SupplierService.create_order(db, order_data)
        print(f"[ORDER_ROUTE] Order created successfully: {result}")
        return {"message": "Order created successfully"}
    except Exception as e:
        print(f"[ORDER_ROUTE] ERROR creating order: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/orders")
async def get_orders(
    search: Optional[str] = Query(None, description="Поиск по названию товара или ФИО поставщика"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список заказов с группировкой по поставщику и дате"""
    return await SupplierService.get_all_orders(db, search)


