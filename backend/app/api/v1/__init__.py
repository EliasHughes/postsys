from fastapi import APIRouter

from app.api.v1 import accounting, auth, cash, customers, dashboard, inventory, products, purchases, reports, sales, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(sales.router)
api_router.include_router(inventory.router)
api_router.include_router(cash.router)
api_router.include_router(customers.router)
api_router.include_router(purchases.router)
api_router.include_router(accounting.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
api_router.include_router(users.router)
