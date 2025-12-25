from pydantic import BaseModel, Field
from typing import Optional, List
from src.models import Season


class DiscountCreate(BaseModel):
    name: str
    percentage: float = Field(ge=0, le=100)
    categories: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    seasons: Optional[List[Season]] = None
    sizes: Optional[List[str]] = None  # Теперь это ID размеров, а не значения


class DiscountResponse(BaseModel):
    id: str
    name: str
    percentage: float
    categories: List[str]
    colors: List[str]
    seasons: List[str]
    sizes: List[dict]  # Список объектов {id, value}

    class Config:
        from_attributes = True

