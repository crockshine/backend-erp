from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import (
    Discount, CategoryToDiscount, ColorToDiscount,
    SeasonToDiscount, SizeToDiscount, ProductCategory, ProductColor
)
from src.discount.schemas import DiscountCreate, DiscountResponse
from typing import List


async def create_discount(db: AsyncSession, discount_data: DiscountCreate) -> DiscountResponse:
    """Создать новую скидку"""
    # Создаем скидку
    discount = Discount(
        name=discount_data.name,
        percentage=discount_data.percentage
    )
    db.add(discount)
    await db.flush()

    # Связываем категории
    if discount_data.categories:
        for category_id in discount_data.categories:
            category_discount = CategoryToDiscount(
                categoryId=category_id,
                discountId=discount.id
            )
            db.add(category_discount)

    # Связываем цвета
    if discount_data.colors:
        for color_id in discount_data.colors:
            color_discount = ColorToDiscount(
                colorId=color_id,
                discountId=discount.id
            )
            db.add(color_discount)

    # Связываем сезоны
    if discount_data.seasons:
        for season in discount_data.seasons:
            season_discount = SeasonToDiscount(
                season=season,
                discountId=discount.id
            )
            db.add(season_discount)

    # Связываем размеры
    if discount_data.sizes:
        for size_id in discount_data.sizes:
            size_discount = SizeToDiscount(
                sizeId=size_id,
                discountId=discount.id
            )
            db.add(size_discount)

    await db.commit()
    await db.refresh(discount)

    return await get_discount_response(db, discount)


async def get_all_discounts(db: AsyncSession) -> List[DiscountResponse]:
    """Получить все скидки"""
    result = await db.execute(select(Discount))
    discounts = result.scalars().all()

    responses = []
    for discount in discounts:
        responses.append(await get_discount_response(db, discount))

    return responses


async def delete_discount(db: AsyncSession, discount_id: str):
    """Удалить скидку"""
    result = await db.execute(select(Discount).where(Discount.id == discount_id))
    discount = result.scalar_one_or_none()

    if not discount:
        raise ValueError("Скидка не найдена")

    await db.delete(discount)
    await db.commit()


async def get_discount_response(db: AsyncSession, discount: Discount) -> DiscountResponse:
    """Преобразовать скидку в ответ"""
    # Получаем связанные категории
    category_result = await db.execute(
        select(ProductCategory)
        .join(CategoryToDiscount)
        .where(CategoryToDiscount.discountId == discount.id)
    )
    categories = [cat.name for cat in category_result.scalars().all()]

    # Получаем связанные цвета
    color_result = await db.execute(
        select(ProductColor)
        .join(ColorToDiscount)
        .where(ColorToDiscount.discountId == discount.id)
    )
    colors = [color.name for color in color_result.scalars().all()]

    # Получаем связанные сезоны
    season_result = await db.execute(
        select(SeasonToDiscount.season)
        .where(SeasonToDiscount.discountId == discount.id)
    )
    seasons = [season.value for season in season_result.scalars().all()]

    # Получаем связанные размеры через ProductSize
    from src.models import ProductSize
    size_result = await db.execute(
        select(ProductSize)
        .join(SizeToDiscount)
        .where(SizeToDiscount.discountId == discount.id)
    )
    sizes = [{"id": size.id, "value": size.value} for size in size_result.scalars().all()]

    return DiscountResponse(
        id=discount.id,
        name=discount.name,
        percentage=discount.percentage,
        categories=categories,
        colors=colors,
        seasons=seasons,
        sizes=sizes
    )

