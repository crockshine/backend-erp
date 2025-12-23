from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime

from src.models import Supplier, OrderToSupplier, Product, ShopRest
from .schemas import SupplierCreate, OrderCreate, OrderProductItem


class SupplierService:
    @staticmethod
    async def get_all_suppliers(db: AsyncSession) -> List[Supplier]:
        """Получить всех поставщиков"""
        result = await db.execute(select(Supplier))
        return result.scalars().all()

    @staticmethod
    async def create_supplier(db: AsyncSession, supplier_data: SupplierCreate) -> Supplier:
        """Создать нового поставщика"""
        try:
            print(f"[SUPPLIER_SERVICE] Creating supplier: name={supplier_data.name}, contacts={supplier_data.contacts}")
            supplier = Supplier(
                name=supplier_data.name,
                contacts=supplier_data.contacts
            )
            db.add(supplier)
            print(f"[SUPPLIER_SERVICE] Supplier added to session")
            await db.commit()
            print(f"[SUPPLIER_SERVICE] Commit successful")
            await db.refresh(supplier)
            print(f"[SUPPLIER_SERVICE] Supplier created with id={supplier.id}")
            return supplier
        except Exception as e:
            print(f"[SUPPLIER_SERVICE] ERROR: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise

    @staticmethod
    async def get_supplier_by_id(db: AsyncSession, supplier_id: str) -> Optional[Supplier]:
        """Получить поставщика по ID"""
        result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_order(db: AsyncSession, order_data: OrderCreate) -> OrderToSupplier:
        """Создать заказ у поставщика"""
        try:
            print(f"[SUPPLIER_SERVICE] Creating order with data: {order_data}")

            # Если указан существующий поставщик
            if order_data.supplierId:
                print(f"[SUPPLIER_SERVICE] Looking for supplier: {order_data.supplierId}")
                supplier = await SupplierService.get_supplier_by_id(db, order_data.supplierId)
                if not supplier:
                    raise ValueError("Поставщик не найден")
                print(f"[SUPPLIER_SERVICE] Found supplier: {supplier.name}")
            # Если нужно создать нового поставщика
            elif order_data.supplierName and order_data.supplierContacts:
                print(f"[SUPPLIER_SERVICE] Creating new supplier: {order_data.supplierName}")
                supplier = await SupplierService.create_supplier(
                    db,
                    SupplierCreate(
                        name=order_data.supplierName,
                        contacts=order_data.supplierContacts
                    )
                )
                print(f"[SUPPLIER_SERVICE] New supplier created: {supplier.id}")
            else:
                raise ValueError("Необходимо указать существующего поставщика или данные нового")

            # Создаем записи заказа для каждого продукта
            orders = []
            for product_item in order_data.products:
                print(f"[SUPPLIER_SERVICE] Processing product: {product_item.productId}, count: {product_item.count}, purchasePrice: {product_item.purchasePrice}")

                # Проверяем существование продукта
                result = await db.execute(select(Product).where(Product.id == product_item.productId))
                product = result.scalar_one_or_none()
                if not product:
                    raise ValueError(f"Продукт {product_item.productId} не найден")

                print(f"[SUPPLIER_SERVICE] Found product: {product.name}, current price: {product.price}")

                # Обновляем цену товара (ставим дефолтную из закупки)
                product.price = product_item.purchasePrice
                print(f"[SUPPLIER_SERVICE] Updated product price to: {product.price}")

                # Создаем заказ с ценой закупки
                order = OrderToSupplier(
                    supplierId=supplier.id,
                    ProductId=product_item.productId,
                    count=product_item.count,
                    purchasePrice=product_item.purchasePrice
                )
                db.add(order)
                orders.append(order)
                print(f"[SUPPLIER_SERVICE] Order item added to session")

                # Обновляем остатки на складе
                result = await db.execute(
                    select(ShopRest).where(ShopRest.productId == product_item.productId)
                )
                shop_rest = result.scalar_one_or_none()
                if shop_rest:
                    old_count = shop_rest.restCount
                    shop_rest.restCount += product_item.count
                    print(f"[SUPPLIER_SERVICE] Updated stock: {old_count} -> {shop_rest.restCount}")
                else:
                    # Если остатков не было, создаем
                    shop_rest = ShopRest(
                        productId=product_item.productId,
                        restCount=product_item.count
                    )
                    db.add(shop_rest)
                    print(f"[SUPPLIER_SERVICE] Created new stock entry: {product_item.count}")

            print(f"[SUPPLIER_SERVICE] Committing {len(orders)} order items to database...")
            await db.commit()
            print(f"[SUPPLIER_SERVICE] Order successfully created!")
            return orders[0] if orders else None

        except Exception as e:
            print(f"[SUPPLIER_SERVICE] ERROR in create_order: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise

    @staticmethod
    async def get_all_orders(db: AsyncSession, search: Optional[str] = None) -> List[dict]:
        """Получить все заказы с информацией о продуктах и поставщиках"""
        query = (
            select(OrderToSupplier)
            .options(
                joinedload(OrderToSupplier.supplier),
                joinedload(OrderToSupplier.product).joinedload(Product.color),
                joinedload(OrderToSupplier.product).joinedload(Product.category)
            )
        )

        result = await db.execute(query)
        all_orders = result.scalars().unique().all()

        # Группируем заказы по поставщику и дате
        orders_by_group = {}
        for order in all_orders:
            # Создаем ключ группировки (supplierId + дата)
            date_key = order.createdAt.strftime("%Y-%m-%d %H:%M")
            group_key = f"{order.supplierId}_{date_key}"

            if group_key not in orders_by_group:
                orders_by_group[group_key] = {
                    "id": order.id,
                    "supplierId": order.supplierId,
                    "supplierName": order.supplier.name,
                    "supplierContacts": order.supplier.contacts,
                    "createdAt": order.createdAt,
                    "products": []
                }

            # Добавляем продукт в группу
            product = order.product
            orders_by_group[group_key]["products"].append({
                "id": product.id,
                "name": product.name,
                "size": product.size,
                "price": product.price,  # Текущая цена продажи
                "purchasePrice": order.purchasePrice,  # Цена закупки
                "season": product.season.value,
                "colorName": product.color.name,
                "categoryName": product.category.name,
                "count": order.count
            })

        # Преобразуем в список
        result_orders = list(orders_by_group.values())

        # Фильтруем по поиску если указан
        if search:
            search_lower = search.lower()
            result_orders = [
                order for order in result_orders
                if search_lower in order["supplierName"].lower()
                or any(search_lower in p["name"].lower() for p in order["products"])
            ]

        # Сортируем по дате (новые первыми)
        result_orders.sort(key=lambda x: x["createdAt"], reverse=True)

        return result_orders

