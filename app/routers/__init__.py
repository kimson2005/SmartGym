from app.routers.health import router as health_router
from app.routers.users import router as users_router
from app.routers.equipments import router as equipments_router

__all__ = ["health_router", "users_router", "equipments_router"]
