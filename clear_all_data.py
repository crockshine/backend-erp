"""Script to delete all data from all tables"""
import asyncio
from sqlalchemy import delete
from src.database import async_session_maker
from src.models import (
    ProductToSale,
    ProductToDiscount,
    CategoryToDiscount,
    ColorToDiscount,
    SeasonToDiscount,
    SizeToDiscount,
    OrderToSupplier,
    ShopRest,
    Sale,
    Product,
    ProductCategory,
    ProductColor,
    ProductSize,
    Employee,
    Supplier,
    Discount
)


async def clear_all_data():
    """Delete all data from all tables in correct order"""
    async with async_session_maker() as session:
        try:
            print("🗑️  Начинаем удаление всех данных из таблиц...")

            # Удаляем сначала связующие таблицы (many-to-many и детали)
            tables_to_clear = [
                ("ProductToSale", ProductToSale),
                ("ProductToDiscount", ProductToDiscount),
                ("CategoryToDiscount", CategoryToDiscount),
                ("ColorToDiscount", ColorToDiscount),
                ("SeasonToDiscount", SeasonToDiscount),
                ("SizeToDiscount", SizeToDiscount),
                ("OrderToSupplier", OrderToSupplier),
                ("ShopRest", ShopRest),
                ("Sale", Sale),
                ("Product", Product),
                ("ProductCategory", ProductCategory),
                ("ProductColor", ProductColor),
                ("ProductSize", ProductSize),
                ("Employee", Employee),
                ("Supplier", Supplier),
                ("Discount", Discount),
            ]

            for table_name, model in tables_to_clear:
                await session.execute(delete(model))
                print(f"  ✓ Таблица {table_name} очищена")

            await session.commit()
            print("✅ Все данные успешно удалены из всех таблиц!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при удалении данных: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(clear_all_data())

