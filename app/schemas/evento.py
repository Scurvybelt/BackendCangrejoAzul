from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum

class TipoEventoEnum(str, Enum):
    limpieza = "Limpieza"
    voluntariado = "Voluntariado"

class EventoBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=255)
    descripcion: str = Field(..., min_length=10)
    fecha: date
    hora: time
    lugar: str = Field(..., min_length=3, max_length=255)
    duracion: int = Field(..., gt=0, description="Duración en minutos")
    requisitos: Optional[str] = None
    tipo: TipoEventoEnum

class EventoCreate(EventoBase):
    pass

class EventoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    descripcion: Optional[str] = Field(None, min_length=10)
    fecha: Optional[date] = None
    hora: Optional[time] = None
    lugar: Optional[str] = Field(None, min_length=3, max_length=255)
    duracion: Optional[int] = Field(None, gt=0)
    requisitos: Optional[str] = None
    tipo: Optional[TipoEventoEnum] = None

# Schema simple para usuarios inscritos (evita recursión)
class UserInscritoSimple(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: str
    
    class Config:
        from_attributes = True

class EventoResponse(EventoBase):
    id: int
    creado_por_id: Optional[int]
    personas_inscritas: List[UserInscritoSimple] = []
    total_inscritos: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EventoListResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    fecha: date
    hora: time
    lugar: str
    duracion: int
    tipo: TipoEventoEnum
    total_inscritos: int
    creado_por_id: Optional[int] = None
    
    class Config:
        from_attributes = True
