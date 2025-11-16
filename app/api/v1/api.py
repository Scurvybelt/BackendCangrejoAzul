from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, eventos, observaciones

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])
api_router.include_router(eventos.router, prefix="/eventos", tags=["Eventos"])
api_router.include_router(observaciones.router, prefix="/observaciones", tags=["Observaciones"])
