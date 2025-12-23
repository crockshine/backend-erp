from fastapi import HTTPException, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct
from sqlalchemy.orm import selectinload
from src.models import (
    Product, ProductCategory, ProductColor, ProductSize, ShopRest,
    Sale, ProductToSale, Season, Discount, CategoryToDiscount,
    ColorToDiscount, SeasonToDiscount, SizeToDiscount
)
from src.product.schemas import (
    CreateProductDto, UpdateProductDto, CreateSaleDto,
    CreateCategoryDto, CreateColorDto
)
from datetime import datetime


class ProductService:
    @staticmethod
    async def calculate_product_discount(db: AsyncSession, product: Product) -> float:
        """Рассчитать общую скидку для продукта (сумма всех применимых скидок)"""
        total_discount = 0.0

        # Получаем все скидки
        discounts_result = await db.execute(
            select(Discount).options(
                selectinload(Discount.category_discounts),
                selectinload(Discount.color_discounts),
                selectinload(Discount.season_discounts),
                selectinload(Discount.size_discounts)
            )
        )
        discounts = discounts_result.scalars().all()

        for discount in discounts:
            # Проверяем, применима ли скидка к продукту
            applies = True

            # Если у скидки есть категории, проверяем соответствие
            if discount.category_discounts:
                category_ids = [cd.categoryId for cd in discount.category_discounts]
                if product.categoryId not in category_ids:
                    applies = False

            # Если у скидки есть цвета, проверяем соответствие
            if applies and discount.color_discounts:
                color_ids = [cd.colorId for cd in discount.color_discounts]
                if product.colorId not in color_ids:
                    applies = False

            # Если у скидки есть сезоны, проверяем соответствие
            if applies and discount.season_discounts:
                seasons = [sd.season for sd in discount.season_discounts]
                if product.season not in seasons:
                    applies = False

            # Если у скидки есть размеры, проверяем соответствие
            if applies and discount.size_discounts:
                sizes = [sd.size for sd in discount.size_discounts]
                if product.size not in sizes:
                    applies = False

            # Если скидка применима, добавляем процент
            if applies:
                total_discount += discount.percentage

        # Ограничиваем скидку до 100%
        return min(total_discount, 100.0)

    @staticmethod
    async def create_product(db: AsyncSession, create_dto: CreateProductDto):
        """Создать новый продукт"""
        product = Product(
            name=create_dto.name,
            size=create_dto.size,
            price=create_dto.price,
            season=Season[create_dto.season],
            colorId=create_dto.colorId,
            categoryId=create_dto.categoryId
        )

        db.add(product)
        await db.commit()
        await db.refresh(product)

        return product

    @staticmethod
    async def get_products_with_filters(
        db: AsyncSession,
        search: Optional[str] = None,
        category_ids: Optional[List[str]] = None,
        color_ids: Optional[List[str]] = None,
        sizes: Optional[List[int]] = None,
        seasons: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 100
    ):
        """Получить продукты с фильтрами и остатками"""
        query = select(Product).options(
            selectinload(Product.color),
            selectinload(Product.category),
            selectinload(Product.shop_rest)
        )

        # Поиск по названию
        if search:
            query = query.where(Product.name.ilike(f"%{search}%"))

        # Фильтр по категориям
        if category_ids:
            query = query.where(Product.categoryId.in_(category_ids))

        # Фильтр по цветам
        if color_ids:
            query = query.where(Product.colorId.in_(color_ids))

        # Фильтр по размерам
        if sizes:
            query = query.where(Product.size.in_(sizes))

        # Фильтр по сезонам
        if seasons:
            season_enums = [Season[s] for s in seasons if s in Season.__members__]
            if season_enums:
                query = query.where(Product.season.in_(season_enums))

        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        products = result.scalars().all()

        # Формируем ответ с дополнительными данными и применяем скидки
        products_data = []
        for product in products:
            # Вычисляем скидку
            discount_percentage = await ProductService.calculate_product_discount(db, product)

            # Применяем скидку к цене
            original_price = product.price
            discounted_price = original_price * (1 - discount_percentage / 100)
            # Гарантируем, что цена не будет отрицательной
            final_price = max(0, discounted_price)

            product_dict = {
                "id": product.id,
                "name": product.name,
                "size": product.size,
                "price": round(final_price, 2),  # Цена со скидкой
                "originalPrice": round(original_price, 2),  # Оригинальная цена
                "discount": round(discount_percentage, 2),  # Процент скидки
                "season": product.season.value,
                "colorId": product.colorId,
                "categoryId": product.categoryId,
                "colorName": product.color.name if product.color else None,
                "categoryName": product.category.name if product.category else None,
                "availableCount": product.shop_rest.restCount if product.shop_rest else 0
            }
            products_data.append(product_dict)

        return products_data

    @staticmethod
    async def get_filter_options(db: AsyncSession):
        """Получить все опции для фильтров"""
        # Получаем все категории
        categories_result = await db.execute(select(ProductCategory))
        categories = categories_result.scalars().all()
        categories_data = [{"id": c.id, "name": c.name} for c in categories]

        # Получаем все цвета
        colors_result = await db.execute(select(ProductColor))
        colors = colors_result.scalars().all()
        colors_data = [{"id": c.id, "name": c.name} for c in colors]

        # Получаем все размеры из таблицы ProductSize
        sizes_result = await db.execute(select(ProductSize))
        sizes_objects = sizes_result.scalars().all()
        sizes = sorted([s.value for s in sizes_objects])

        # Если таблица пустая, получаем размеры из Product
        if not sizes:
            distinct_sizes_result = await db.execute(select(distinct(Product.size)))
            sizes = sorted([s for s in distinct_sizes_result.scalars().all()])

        # Получаем все сезоны
        seasons = [season.value for season in Season]

        return {
            "categories": categories_data,
            "colors": colors_data,
            "sizes": sizes,
            "seasons": seasons
        }

    @staticmethod
    async def create_sale(db: AsyncSession, sale_dto: CreateSaleDto, employee_id: str):
        """Создать продажу и списать товары"""
        print(f"[CREATE_SALE] Начало создания продажи для сотрудника {employee_id}")
        print(f"[CREATE_SALE] Количество товаров: {len(sale_dto.items)}")

        total_price = 0.0

        # Проверяем наличие товаров и считаем итоговую цену
        for item in sale_dto.items:
            print(f"[CREATE_SALE] Проверка товара {item.productId}, количество: {item.count}")
            # Получаем продукт с остатками
            product_result = await db.execute(
                select(Product).options(selectinload(Product.shop_rest))
                .where(Product.id == item.productId)
            )
            product = product_result.scalar_one_or_none()

            if not product:
                print(f"[CREATE_SALE] Ошибка: продукт {item.productId} не найден")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Продукт {item.productId} не найден"
                )

            if not product.shop_rest:
                print(f"[CREATE_SALE] Ошибка: товар '{product.name}' отсутствует на складе")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Товар '{product.name}' отсутствует на складе"
                )

            if product.shop_rest.restCount < item.count:
                print(f"[CREATE_SALE] Ошибка: недостаточно товара '{product.name}'. Доступно: {product.shop_rest.restCount}, запрошено: {item.count}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно товара '{product.name}'. Доступно: {product.shop_rest.restCount}"
                )

            total_price += product.price * item.count
            print(f"[CREATE_SALE] Товар '{product.name}' проверен, цена: {product.price}, количество: {item.count}")

        print(f"[CREATE_SALE] Итоговая цена: {total_price}")

        # Создаем продажу
        try:
            sale = Sale(
                finalPrice=total_price,
                employeeId=employee_id,
                createdAt=datetime.utcnow()
            )
            db.add(sale)
            await db.flush()
            print(f"[CREATE_SALE] Продажа создана с ID: {sale.id}")
        except Exception as e:
            print(f"[CREATE_SALE] Ошибка при создании продажи: {e}")
            raise

        # Создаем связи и списываем товары
        for item in sale_dto.items:
            try:
                # Создаем связь ProductToSale
                product_to_sale = ProductToSale(
                    saleId=sale.id,
                    ProductId=item.productId,
                    count=item.count
                )
                db.add(product_to_sale)
                print(f"[CREATE_SALE] Создана связь ProductToSale для товара {item.productId}")

                # Списываем товар
                product_result = await db.execute(
                    select(Product).options(selectinload(Product.shop_rest))
                    .where(Product.id == item.productId)
                )
                product = product_result.scalar_one()
                product.shop_rest.restCount -= item.count
                print(f"[CREATE_SALE] Списано {item.count} единиц товара '{product.name}', осталось: {product.shop_rest.restCount}")
            except Exception as e:
                print(f"[CREATE_SALE] Ошибка при обработке товара {item.productId}: {e}")
                raise

        try:
            await db.commit()
            await db.refresh(sale)
            print(f"[CREATE_SALE] Продажа успешно создана и сохранена")
        except Exception as e:
            print(f"[CREATE_SALE] Ошибка при коммите: {e}")
            raise

        return sale

    @staticmethod
    async def update_product(db: AsyncSession, product_id: str, update_dto: UpdateProductDto):
        """Обновить продукт"""
        try:
            print(f"[PRODUCT_SERVICE] Updating product {product_id} with data: {update_dto.model_dump(exclude_unset=True)}")

            result = await db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = result.scalar_one_or_none()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Продукт не найден"
                )

            update_data = update_dto.model_dump(exclude_unset=True)
            print(f"[PRODUCT_SERVICE] Update data: {update_data}")

            # Конвертируем season в enum если он есть
            if "season" in update_data and update_data["season"]:
                try:
                    update_data["season"] = Season[update_data["season"]]
                    print(f"[PRODUCT_SERVICE] Season converted to enum: {update_data['season']}")
                except KeyError as e:
                    print(f"[PRODUCT_SERVICE] ERROR: Invalid season value: {update_data['season']}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Недопустимое значение сезона: {update_data['season']}"
                    )

            for key, value in update_data.items():
                print(f"[PRODUCT_SERVICE] Setting {key} = {value}")
                setattr(product, key, value)

            await db.commit()
            await db.refresh(product)

            print(f"[PRODUCT_SERVICE] Product updated successfully: {product.id}")
            return product

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            print(f"[PRODUCT_SERVICE] ERROR updating product: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении продукта: {str(e)}"
            )

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: str):
        """Удалить продукт"""
        try:
            result = await db.execute(
                select(Product).where(Product.id == product_id)
            )
            product = result.scalar_one_or_none()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Продукт не найден"
                )

            await db.delete(product)
            await db.commit()

            return product
        except Exception as e:
            await db.rollback()
            print(f"[PRODUCT_SERVICE] Ошибка удаления продукта: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении продукта: {str(e)}"
            )

    @staticmethod
    async def create_category(db: AsyncSession, create_dto: CreateCategoryDto):
        """Создать новую категорию"""
        # Проверяем, не существует ли уже категория с таким именем (case-insensitive)
        normalized_name = create_dto.name.strip().lower()
        existing = await db.execute(
            select(ProductCategory)
        )
        all_categories = existing.scalars().all()

        for category in all_categories:
            if category.name.strip().lower() == normalized_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Категория с таким названием уже существует"
                )

        category = ProductCategory(name=create_dto.name.strip())
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: str):
        """Удалить категорию с каскадным удалением продуктов"""
        result = await db.execute(
            select(ProductCategory).where(ProductCategory.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )

        # Проверяем, есть ли продукты с этой категорией
        products_with_category = await db.execute(
            select(Product).where(Product.categoryId == category_id)
        )
        products = products_with_category.scalars().all()

        # Если есть продукты - удаляем их каскадно
        if products:
            for product in products:
                await db.delete(product)

        await db.delete(category)
        await db.commit()
        return category

    @staticmethod
    async def create_color(db: AsyncSession, create_dto: CreateColorDto):
        """Создать новый цвет"""
        # Проверяем, не существует ли уже цвет с таким именем (case-insensitive)
        normalized_name = create_dto.name.strip().lower()
        existing = await db.execute(
            select(ProductColor)
        )
        all_colors = existing.scalars().all()

        for color in all_colors:
            if color.name.strip().lower() == normalized_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Цвет с таким названием уже существует"
                )

        color = ProductColor(name=create_dto.name.strip())
        db.add(color)
        await db.commit()
        await db.refresh(color)
        return color
        return color

    @staticmethod
    async def delete_color(db: AsyncSession, color_id: str):
        """Удалить цвет с каскадным удалением продуктов"""
        result = await db.execute(
            select(ProductColor).where(ProductColor.id == color_id)
        )
        color = result.scalar_one_or_none()

        if not color:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Цвет не найден"
            )

        # Проверяем, есть ли продукты с этим цветом
        products_with_color = await db.execute(
            select(Product).where(Product.colorId == color_id)
        )
        products = products_with_color.scalars().all()

        # Если есть продукты - удаляем их каскадно
        if products:
            for product in products:
                await db.delete(product)

        await db.delete(color)
        await db.commit()
        return color

    @staticmethod
    async def create_size(db: AsyncSession, size_value: int):
        """Создать новый размер"""
        # Проверяем, не существует ли уже размер с таким значением
        existing = await db.execute(
            select(ProductSize).where(ProductSize.value == size_value)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер с таким значением уже существует"
            )

        size = ProductSize(value=size_value)
        db.add(size)
        await db.commit()
        await db.refresh(size)
        return size

    @staticmethod
    async def delete_size(db: AsyncSession, size_value: int):
        """Удалить размер"""
        result = await db.execute(
            select(ProductSize).where(ProductSize.value == size_value)
        )
        size = result.scalar_one_or_none()

        if not size:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Размер не найден"
            )

        # Проверяем, есть ли продукты с этим размером
        products_with_size = await db.execute(
            select(Product).where(Product.size == size_value)
        )
        products = products_with_size.scalars().all()

        # Если есть продукты - удаляем их каскадно
        if products:
            for product in products:
                await db.delete(product)

        await db.delete(size)
        await db.commit()
        return size

    @staticmethod
    async def get_sales(db: AsyncSession, offset: int = 0, limit: int = 100):
        """Получить список продаж с информацией о сотрудниках и товарах"""
        from src.models import Employee

        # Получаем продажи с сотрудниками и товарами
        query = select(Sale).options(
            selectinload(Sale.employee),
            selectinload(Sale.product_sales).selectinload(ProductToSale.product).selectinload(Product.color),
            selectinload(Sale.product_sales).selectinload(ProductToSale.product).selectinload(Product.category)
        ).order_by(Sale.createdAt.desc()).offset(offset).limit(limit)

        result = await db.execute(query)
        sales = result.scalars().all()

        # Формируем ответ
        sales_data = []
        for sale in sales:
            # Информация о сотруднике
            employee_info = {
                "id": sale.employee.id,
                "name": sale.employee.name,
                "lastname": sale.employee.lastname,
                "patronymic": sale.employee.patronymic,
                "role": sale.employee.role.value
            }

            # Список проданных товаров
            products_list = []
            for product_sale in sale.product_sales:
                product = product_sale.product
                product_info = {
                    "id": product.id,
                    "name": product.name,
                    "size": product.size,
                    "price": product.price,
                    "count": product_sale.count,
                    "colorName": product.color.name if product.color else None,
                    "categoryName": product.category.name if product.category else None,
                    "season": product.season.value
                }
                products_list.append(product_info)

            sale_dict = {
                "id": sale.id,
                "finalPrice": sale.finalPrice,
                "createdAt": sale.createdAt.isoformat(),
                "employee": employee_info,
                "products": products_list
            }
            sales_data.append(sale_dict)

        return sales_data


