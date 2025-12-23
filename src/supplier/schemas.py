from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SupplierBase(BaseModel):
    name: str
    contacts: str


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: str

    class Config:
        from_attributes = True


class OrderProductItem(BaseModel):
    productId: str
    count: int
    purchasePrice: float  # Цена закупки за штуку


class OrderCreate(BaseModel):
    supplierId: Optional[str] = None
    supplierName: Optional[str] = None
    supplierContacts: Optional[str] = None
    products: List[OrderProductItem]


class OrderProductResponse(BaseModel):
    id: str
    name: str
    size: int
    price: float  # Текущая цена продажи
    purchasePrice: float  # Цена закупки
    season: str
    colorName: str
    categoryName: str
    count: int

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: str
    supplierId: str
    supplierName: str
    supplierContacts: str
    createdAt: datetime
    products: List[OrderProductResponse]

    class Config:
        from_attributes = True

