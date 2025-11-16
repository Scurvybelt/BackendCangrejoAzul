from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.observacion import (
    ObservacionCreate,
    ObservacionUpdate,
    ObservacionInDB,
    ObservacionResponse
)
from app.crud import observacion as crud_observacion
import shutil
import os
from pathlib import Path

router = APIRouter()

# Directorio para guardar fotos (ajusta según tu configuración)
UPLOAD_DIR = Path("uploads/observaciones")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=ObservacionInDB, status_code=status.HTTP_201_CREATED)
def crear_observacion(
    *,
    db: Session = Depends(get_db),
    observacion_in: ObservacionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Crear una nueva observación de cangrejo azul.
    El usuario se identifica automáticamente por el token Bearer.
    """
    observacion = crud_observacion.crear_observacion(
        db=db,
        observacion=observacion_in,
        user_id=current_user.id
    )
    return observacion

@router.get("/", response_model=List[ObservacionResponse])
def listar_observaciones(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de registros a retornar"),
    user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    fecha_inicio: Optional[date] = Query(None, description="Filtrar desde esta fecha"),
    fecha_fin: Optional[date] = Query(None, description="Filtrar hasta esta fecha"),
    comunidad: Optional[str] = Query(None, description="Filtrar por comunidad"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Listar observaciones con filtros opcionales.
    Usuarios normales solo ven sus propias observaciones.
    Administradores pueden ver todas las observaciones.
    """
    # Si el usuario no es admin, solo puede ver sus propias observaciones
    if current_user.permiso.value != "admin":
        user_id = current_user.id
    
    observaciones = crud_observacion.obtener_observaciones(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        comunidad=comunidad
    )
    
    # Agregar información del usuario a la respuesta
    observaciones_response = []
    for obs in observaciones:
        obs_dict = ObservacionResponse.model_validate(obs)
        obs_dict.usuario_email = obs.usuario.email if obs.usuario else None
        obs_dict.usuario_nombre = obs.usuario.full_name if obs.usuario else None
        observaciones_response.append(obs_dict)
    
    return observaciones_response

@router.get("/mis-observaciones", response_model=List[ObservacionInDB])
def obtener_mis_observaciones(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener todas las observaciones del usuario autenticado.
    """
    observaciones = crud_observacion.obtener_observaciones_usuario(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return observaciones

@router.get("/estadisticas")
def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de observaciones del usuario.
    """
    total_observaciones = crud_observacion.contar_observaciones_usuario(
        db=db,
        user_id=current_user.id
    )
    
    return {
        "total_observaciones": total_observaciones,
        "usuario": current_user.username
    }

@router.get("/estadisticas/global")
def obtener_estadisticas_globales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener estadísticas globales (solo administradores).
    """
    if current_user.permiso.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver estadísticas globales"
        )
    
    total_observaciones = crud_observacion.contar_observaciones_total(db=db)
    
    return {
        "total_observaciones": total_observaciones
    }

@router.get("/{observacion_id}", response_model=ObservacionResponse)
def obtener_observacion(
    observacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtener una observación específica por ID.
    """
    observacion = crud_observacion.obtener_observacion_por_id(db=db, observacion_id=observacion_id)
    
    if not observacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada"
        )
    
    # Los usuarios solo pueden ver sus propias observaciones (excepto admins)
    if current_user.permiso.value != "admin" and observacion.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver esta observación"
        )
    
    obs_response = ObservacionResponse.model_validate(observacion)
    obs_response.usuario_email = observacion.usuario.email if observacion.usuario else None
    obs_response.usuario_nombre = observacion.usuario.full_name if observacion.usuario else None
    
    return obs_response

@router.put("/{observacion_id}", response_model=ObservacionInDB)
def actualizar_observacion(
    observacion_id: int,
    observacion_update: ObservacionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualizar una observación existente.
    Solo el creador de la observación puede actualizarla.
    """
    observacion = crud_observacion.actualizar_observacion(
        db=db,
        observacion_id=observacion_id,
        observacion_update=observacion_update,
        user_id=current_user.id
    )
    
    if not observacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada o no tiene permisos para actualizarla"
        )
    
    return observacion

@router.post("/{observacion_id}/foto", response_model=ObservacionInDB)
async def subir_foto_observacion(
    observacion_id: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Subir una foto o video para una observación existente.
    Formatos aceptados: jpg, jpeg, png, mp4, mov
    """
    # Verificar que el usuario sea el creador de la observación
    observacion = crud_observacion.obtener_observacion_por_id(db=db, observacion_id=observacion_id)
    
    if not observacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada"
        )
    
    if observacion.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para subir foto a esta observación"
        )
    
    # Validar extensión de archivo
    extensiones_permitidas = {".jpg", ".jpeg", ".png", ".mp4", ".mov"}
    file_ext = Path(foto.filename).suffix.lower()
    
    if file_ext not in extensiones_permitidas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de archivo no permitido. Use: {', '.join(extensiones_permitidas)}"
        )
    
    # Generar nombre único para el archivo
    file_name = f"obs_{observacion_id}_{current_user.id}_{foto.filename}"
    file_path = UPLOAD_DIR / file_name
    
    # Guardar el archivo
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el archivo: {str(e)}"
        )
    
    # Actualizar la URL de la foto en la base de datos
    foto_url = f"/uploads/observaciones/{file_name}"
    observacion_actualizada = crud_observacion.actualizar_foto_observacion(
        db=db,
        observacion_id=observacion_id,
        foto_url=foto_url,
        user_id=current_user.id
    )
    
    return observacion_actualizada

@router.delete("/{observacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_observacion(
    observacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Eliminar una observación.
    Solo el creador de la observación puede eliminarla.
    """
    eliminado = crud_observacion.eliminar_observacion(
        db=db,
        observacion_id=observacion_id,
        user_id=current_user.id
    )
    
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada o no tiene permisos para eliminarla"
        )
    
    return None
