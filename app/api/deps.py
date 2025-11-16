"""
Dependencias comunes para los endpoints de la API
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import get_db

def get_db_session() -> Generator:
    """
    Dependencia para obtener la sesión de base de datos
    """
    try:
        db = get_db()
        yield db
    finally:
        pass
