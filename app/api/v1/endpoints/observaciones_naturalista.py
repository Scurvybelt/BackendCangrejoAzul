from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import json

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.observacion_naturalista import (
    ObservacionNaturalistaCreate,
    ObservacionNaturalistaInDB,
    ObservacionNaturalistaResponse,
    ObservacionNaturalistaImport,
    ImportResult,
    EstadisticasNaturalista
)
from app.crud import observacion_naturalista as crud_obs_nat

router = APIRouter()


@router.post("/importar", response_model=ImportResult, status_code=status.HTTP_201_CREATED)
async def importar_observaciones(
    archivo: UploadFile = File(..., description="Archivo JSON con observaciones de CONABIO"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Importar observaciones desde un archivo JSON de CONABIO/iNaturalist.
    Solo administradores pueden importar datos.
    
    El archivo debe ser un JSON con el formato del SNIB de CONABIO.
    """
    if not archivo.filename.endswith('.json'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser formato JSON"
        )
    
    try:
        contenido = await archivo.read()
        datos = json.loads(contenido.decode('utf-8'))
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al parsear JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al leer archivo: {str(e)}"
        )
    
    if not isinstance(datos, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El JSON debe contener una lista de observaciones"
        )
    
    # Convertir y validar cada observación
    observaciones_crear = []
    errores_validacion = []
    
    for i, item in enumerate(datos):
        try:
            obs_import = ObservacionNaturalistaImport(**item)
            obs_create = obs_import.to_create_schema()
            observaciones_crear.append(obs_create)
        except Exception as e:
            errores_validacion.append(f"Registro {i}: {str(e)}")
    
    # Insertar en la base de datos
    resultado = crud_obs_nat.crear_observaciones_bulk(db, observaciones_crear)
    
    return ImportResult(
        total_procesados=len(datos),
        insertados=resultado["insertados"],
        duplicados=resultado["duplicados"],
        errores=resultado["errores"] + len(errores_validacion),
        mensajes_error=errores_validacion + resultado["mensajes_error"]
    )


@router.post("/importar-json", response_model=ImportResult, status_code=status.HTTP_201_CREATED)
def importar_observaciones_json(
    observaciones: List[ObservacionNaturalistaImport],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Importar observaciones enviando directamente el JSON en el body.
    Solo administradores pueden importar datos.
    """
    observaciones_crear = []
    errores_validacion = []
    
    for i, obs in enumerate(observaciones):
        try:
            obs_create = obs.to_create_schema()
            observaciones_crear.append(obs_create)
        except Exception as e:
            errores_validacion.append(f"Registro {i}: {str(e)}")
    
    resultado = crud_obs_nat.crear_observaciones_bulk(db, observaciones_crear)
    
    return ImportResult(
        total_procesados=len(observaciones),
        insertados=resultado["insertados"],
        duplicados=resultado["duplicados"],
        errores=resultado["errores"] + len(errores_validacion),
        mensajes_error=errores_validacion + resultado["mensajes_error"]
    )


@router.get("/", response_model=List[ObservacionNaturalistaResponse])
def listar_observaciones(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Límite de registros a retornar"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    municipio: Optional[str] = Query(None, description="Filtrar por municipio"),
    fecha_inicio: Optional[date] = Query(None, description="Filtrar desde esta fecha"),
    fecha_fin: Optional[date] = Query(None, description="Filtrar hasta esta fecha"),
    especie: Optional[str] = Query(None, description="Filtrar por especie")
):
    """
    Listar observaciones de Naturalista con filtros opcionales.
    Este endpoint es público (no requiere autenticación).
    """
    observaciones = crud_obs_nat.obtener_observaciones(
        db=db,
        skip=skip,
        limit=limit,
        estado=estado,
        municipio=municipio,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        especie=especie
    )
    return observaciones


@router.get("/estadisticas", response_model=EstadisticasNaturalista)
def obtener_estadisticas(
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas agregadas de las observaciones de Naturalista.
    Este endpoint es público.
    """
    estadisticas = crud_obs_nat.obtener_estadisticas(db=db)
    return EstadisticasNaturalista(**estadisticas)


@router.get("/mapa")
def obtener_datos_mapa(
    db: Session = Depends(get_db),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    municipio: Optional[str] = Query(None, description="Filtrar por municipio"),
    limit: int = Query(1000, ge=1, le=5000, description="Límite de puntos")
):
    """
    Obtener coordenadas para visualización en mapa.
    Retorna latitud, longitud y datos básicos de cada observación.
    Este endpoint es público.
    """
    return crud_obs_nat.obtener_coordenadas_mapa(
        db=db,
        estado=estado,
        municipio=municipio,
        limit=limit
    )


@router.get("/total")
def obtener_total(
    db: Session = Depends(get_db),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    municipio: Optional[str] = Query(None, description="Filtrar por municipio")
):
    """
    Obtener el total de observaciones con filtros opcionales.
    Este endpoint es público.
    """
    total = crud_obs_nat.contar_observaciones(
        db=db,
        estado=estado,
        municipio=municipio
    )
    return {"total": total}


@router.get("/{observacion_id}", response_model=ObservacionNaturalistaResponse)
def obtener_observacion(
    observacion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener una observación específica por ID.
    Este endpoint es público.
    """
    observacion = crud_obs_nat.obtener_observacion_por_id(db=db, observacion_id=observacion_id)
    
    if not observacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada"
        )
    
    return observacion


@router.get("/ejemplar/{id_ejemplar}", response_model=ObservacionNaturalistaResponse)
def obtener_por_id_ejemplar(
    id_ejemplar: str,
    db: Session = Depends(get_db)
):
    """
    Obtener una observación por su ID de ejemplar (SNIB).
    Este endpoint es público.
    """
    observacion = crud_obs_nat.obtener_observacion_por_id_ejemplar(db=db, id_ejemplar=id_ejemplar)
    
    if not observacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada"
        )
    
    return observacion


@router.delete("/{observacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_observacion(
    observacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Eliminar una observación por ID.
    Solo administradores pueden eliminar.
    """
    eliminado = crud_obs_nat.eliminar_observacion(db=db, observacion_id=observacion_id)
    
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observación no encontrada"
        )
    
    return None


@router.delete("/", status_code=status.HTTP_200_OK)
def eliminar_todas_observaciones(
    confirmar: bool = Query(..., description="Debe ser True para confirmar eliminación"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Eliminar TODAS las observaciones de Naturalista.
    Solo administradores. Requiere confirmación explícita.
    ¡USAR CON PRECAUCIÓN!
    """
    if not confirmar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe confirmar la eliminación estableciendo confirmar=true"
        )
    
    total_eliminados = crud_obs_nat.eliminar_todas(db=db)
    
    return {"mensaje": f"Se eliminaron {total_eliminados} observaciones"}
