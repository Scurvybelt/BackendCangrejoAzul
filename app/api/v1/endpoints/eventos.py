from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.crud import evento as crud_evento
from app.schemas import EventoCreate, EventoResponse, EventoUpdate
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
async def crear_evento(
    evento: EventoCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Crear un nuevo evento (solo administradores)
    
    Requiere permisos de administrador
    """
    nuevo_evento = crud_evento.create_evento(
        db=db, 
        evento=evento, 
        creado_por_id=current_admin.id
    )
    return nuevo_evento

@router.get("/", response_model=List[EventoResponse])
async def listar_eventos(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: Limpieza o Voluntariado"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar eventos desde esta fecha"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener lista de eventos
    
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros
    - **tipo**: Filtrar por tipo de evento
    - **fecha_desde**: Mostrar eventos desde esta fecha
    """
    eventos = crud_evento.get_eventos(
        db, 
        skip=skip, 
        limit=limit,
        tipo=tipo,
        fecha_desde=fecha_desde
    )
    return eventos

@router.get("/{evento_id}", response_model=EventoResponse)
async def obtener_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener información de un evento específico
    """
    evento = crud_evento.get_evento_by_id(db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return evento

@router.put("/{evento_id}", response_model=EventoResponse)
async def actualizar_evento(
    evento_id: int,
    evento_data: EventoUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Actualizar un evento (solo administradores)
    """
    evento = crud_evento.update_evento(db, evento_id=evento_id, evento_data=evento_data)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return evento

@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Eliminar un evento (solo administradores)
    """
    evento = crud_evento.delete_evento(db, evento_id=evento_id)
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return None

@router.post("/{evento_id}/inscribir", response_model=EventoResponse)
async def inscribirse_a_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Inscribirse a un evento
    
    Cualquier usuario autenticado puede inscribirse
    """
    evento = crud_evento.inscribir_usuario(
        db, 
        evento_id=evento_id, 
        user_id=current_user.id
    )
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return evento

@router.delete("/{evento_id}/desinscribir", response_model=EventoResponse)
async def desinscribirse_de_evento(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Desinscribirse de un evento
    """
    evento = crud_evento.desinscribir_usuario(
        db, 
        evento_id=evento_id, 
        user_id=current_user.id
    )
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return evento

@router.get("/mis-eventos/inscritos", response_model=List[EventoResponse])
async def mis_eventos_inscritos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener eventos en los que el usuario está inscrito
    """
    eventos = crud_evento.get_eventos_usuario(db, user_id=current_user.id)
    return eventos
