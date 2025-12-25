from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from src.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class EmployeeRole(str, enum.Enum):
    SELLER = "SELLER"
    ADMIN = "ADMIN"


class Season(str, enum.Enum):
    FALL = "FALL"
    WINTER = "WINTER"
    SPRING = "SPRING"
    SUMMER = "SUMMER"


class Employee(Base):
    __tablename__ = "Employee"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    role = Column(SQLEnum(EmployeeRole, name='EmployeeRole'), nullable=False)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    sales = relationship("Sale", back_populates="employee")


class ProductCategory(Base):
    __tablename__ = "ProductCategory"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="category")
    category_discounts = relationship("CategoryToDiscount", back_populates="category")


class ProductColor(Base):
    __tablename__ = "ProductColor"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="color")
    color_discounts = relationship("ColorToDiscount", back_populates="color")


class ProductSize(Base):
    __tablename__ = "ProductSize"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    value = Column(Integer, nullable=False, unique=True)

    products = relationship("Product", back_populates="size")
    size_discounts = relationship("SizeToDiscount", back_populates="size")


class Product(Base):
    __tablename__ = "Product"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    name = Column(String, nullable=False)
    sizeId = Column(String, ForeignKey("ProductSize.id", ondelete="CASCADE"), nullable=False)
    price = Column(Float, nullable=False)
    season = Column(SQLEnum(Season, name='Season'), nullable=False)
    colorId = Column(String, ForeignKey("ProductColor.id", ondelete="CASCADE"), nullable=False)
    categoryId = Column(String, ForeignKey("ProductCategory.id", ondelete="CASCADE"), nullable=False)

    size = relationship("ProductSize", back_populates="products")
    color = relationship("ProductColor", back_populates="products")
    category = relationship("ProductCategory", back_populates="products")
    shop_rest = relationship("ShopRest", back_populates="product", uselist=False, cascade="all, delete-orphan")
    product_sales = relationship("ProductToSale", back_populates="product", cascade="all, delete-orphan")
    product_discounts = relationship("ProductToDiscount", back_populates="product", cascade="all, delete-orphan")
    orders_to_supplier = relationship("OrderToSupplier", back_populates="product", cascade="all, delete-orphan")


class ShopRest(Base):
    __tablename__ = "ShopRest"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    productId = Column(String, ForeignKey("Product.id", ondelete="CASCADE"), unique=True, nullable=False)
    restCount = Column(Integer, nullable=False)

    product = relationship("Product", back_populates="shop_rest")


class Sale(Base):
    __tablename__ = "Sale"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    finalPrice = Column(Float, nullable=False)
    employeeId = Column(String, ForeignKey("Employee.id", ondelete="CASCADE"), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    employee = relationship("Employee", back_populates="sales")
    product_sales = relationship("ProductToSale", back_populates="sale")


class ProductToSale(Base):
    __tablename__ = "ProductToSale"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    saleId = Column(String, ForeignKey("Sale.id", ondelete="CASCADE"), nullable=False)
    ProductId = Column(String, ForeignKey("Product.id", ondelete="CASCADE"), nullable=False)
    count = Column(Integer, nullable=False)

    sale = relationship("Sale", back_populates="product_sales")
    product = relationship("Product", back_populates="product_sales")


class Supplier(Base):
    __tablename__ = "Supplier"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    name = Column(String, nullable=False)
    contacts = Column(String, nullable=False)

    orders = relationship("OrderToSupplier", back_populates="supplier")


class OrderToSupplier(Base):
    __tablename__ = "OrderToSupplier"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    supplierId = Column(String, ForeignKey("Supplier.id", ondelete="CASCADE"), nullable=False)
    ProductId = Column(String, ForeignKey("Product.id", ondelete="CASCADE"), nullable=False)
    count = Column(Integer, nullable=False)
    purchasePrice = Column(Float, nullable=False)  # Цена закупки за штуку
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    supplier = relationship("Supplier", back_populates="orders")
    product = relationship("Product", back_populates="orders_to_supplier")


class Discount(Base):
    __tablename__ = "Discount"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    name = Column(String, nullable=False)
    percentage = Column(Float, nullable=False)

    category_discounts = relationship("CategoryToDiscount", back_populates="discount", cascade="all, delete-orphan")
    color_discounts = relationship("ColorToDiscount", back_populates="discount", cascade="all, delete-orphan")
    season_discounts = relationship("SeasonToDiscount", back_populates="discount", cascade="all, delete-orphan")
    size_discounts = relationship("SizeToDiscount", back_populates="discount", cascade="all, delete-orphan")
    product_discounts = relationship("ProductToDiscount", back_populates="discount", cascade="all, delete-orphan")


class CategoryToDiscount(Base):
    __tablename__ = "CategoryToDiscount"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    categoryId = Column(String, ForeignKey("ProductCategory.id", ondelete="CASCADE"), nullable=False)
    discountId = Column(String, ForeignKey("Discount.id", ondelete="CASCADE"), nullable=False)

    category = relationship("ProductCategory", back_populates="category_discounts")
    discount = relationship("Discount", back_populates="category_discounts")


class ColorToDiscount(Base):
    __tablename__ = "ColorToDiscount"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    colorId = Column(String, ForeignKey("ProductColor.id", ondelete="CASCADE"), nullable=False)
    discountId = Column(String, ForeignKey("Discount.id", ondelete="CASCADE"), nullable=False)

    color = relationship("ProductColor", back_populates="color_discounts")
    discount = relationship("Discount", back_populates="color_discounts")


class SeasonToDiscount(Base):
    __tablename__ = "SeasonToDiscount"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    season = Column(SQLEnum(Season, name='Season'), nullable=False)
    discountId = Column(String, ForeignKey("Discount.id", ondelete="CASCADE"), nullable=False)

    discount = relationship("Discount", back_populates="season_discounts")


class SizeToDiscount(Base):
    __tablename__ = "SizeToDiscount"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    sizeId = Column(String, ForeignKey("ProductSize.id", ondelete="CASCADE"), nullable=False)
    discountId = Column(String, ForeignKey("Discount.id", ondelete="CASCADE"), nullable=False)

    size = relationship("ProductSize", back_populates="size_discounts")
    discount = relationship("Discount", back_populates="size_discounts")


class ProductToDiscount(Base):
    __tablename__ = "ProductToDiscount"

    id = Column(String, primary_key=True, default=generate_uuid, unique=True)
    productId = Column(String, ForeignKey("Product.id", ondelete="CASCADE"), nullable=False)
    discountId = Column(String, ForeignKey("Discount.id", ondelete="CASCADE"), nullable=False)

    product = relationship("Product", back_populates="product_discounts")
    discount = relationship("Discount", back_populates="product_discounts")

