from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.routes import router as auth_router
from src.product.routes import router as product_router
from src.supplier.routes import router as supplier_router
from src.discount.routes import router as discount_router
from src.config import settings


app = FastAPI(
    title="ERP System API",
    description="""
## ERP система для управления сотрудниками и продуктами

### Доступные модули:
- **Auth** - Аутентификация и управление сотрудниками
- **Products** - Управление продуктами
- **Suppliers** - Управление поставщиками и заказами

### Документация:
- Swagger UI: http://localhost:8008/docs
- ReDoc: http://localhost:8008/redoc
- OpenAPI JSON: http://localhost:8008/openapi.json
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(supplier_router, tags=["Suppliers"])  # Prefix уже установлен в routes.py
app.include_router(discount_router, tags=["Discounts"])  # Prefix уже установлен в routes.py


@app.get("/", tags=["Root"])
async def root():
    """
    Корневой endpoint API

    Возвращает информацию о доступных маршрутах
    """
    return {
        "message": "ERP System API",
        "status": "running",
        "version": "1.0.0",
        "documentation": {
            "swagger": "http://localhost:8008/docs",
            "redoc": "http://localhost:8008/redoc",
            "openapi": "http://localhost:8008/openapi.json"
        },
        "endpoints": {
            "auth": {
                "login": "POST /auth/login",
                "create_employee": "POST /auth/create-employee",
                "get_employees": "GET /auth/employees",
                "update_employee": "PATCH /auth/employees/{id}",
                "delete_employee": "DELETE /auth/employees/{id}"
            },
            "products": {
                "create": "POST /products/",
                "list": "GET /products/",
                "update": "PATCH /products/{id}",
                "delete": "DELETE /products/{id}"
            }
        }
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint

    Проверка работоспособности API
    """
    return {
        "status": "healthy",
        "api": "running",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=True
    )

