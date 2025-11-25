from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.observacion_naturalista import ObservacionNaturalista
from app.schemas.observacion_naturalista import ObservacionNaturalistaCreate
from typing import List, Optional
from datetime import date


def crear_observacion(db: Session, observacion: ObservacionNaturalistaCreate) -> ObservacionNaturalista:
    """Crear una nueva observación de Naturalista"""
    db_observacion = ObservacionNaturalista(
        id_ejemplar=observacion.id_ejemplar,
        id_nombre_cat_valido=observacion.id_nombre_cat_valido,
        especie_valida_busqueda=observacion.especie_valida_busqueda,
        comentarios_cat_valido=observacion.comentarios_cat_valido,
        categoria_taxonomica=observacion.categoria_taxonomica,
        entid=observacion.entid,
        munid=observacion.munid,
        anpid=observacion.anpid,
        ecorid=observacion.ecorid,
        latitud=observacion.latitud,
        longitud=observacion.longitud,
        localidad=observacion.localidad,
        municipio=observacion.municipio,
        estado=observacion.estado,
        pais=observacion.pais,
        fecha_colecta=observacion.fecha_colecta,
        colector=observacion.colector,
        coleccion=observacion.coleccion,
        probable_loc_no_de_campo=observacion.probable_loc_no_de_campo,
        ejemplar_fosil=observacion.ejemplar_fosil,
        institucion=observacion.institucion,
        pais_coleccion=observacion.pais_coleccion,
        proyecto=observacion.proyecto,
        url_proyecto=observacion.url_proyecto,
        url_ejemplar=observacion.url_ejemplar,
        url_origen=observacion.url_origen,
        id_original=observacion.id_original,
        tipo_coleccion=observacion.tipo_coleccion,
        id_nombre_cat_valido_orig=observacion.id_nombre_cat_valido_orig
    )
    
    db.add(db_observacion)
    db.commit()
    db.refresh(db_observacion)
    return db_observacion


def crear_observaciones_bulk(db: Session, observaciones: List[ObservacionNaturalistaCreate]) -> dict:
    """Crear múltiples observaciones de forma eficiente"""
    insertados = 0
    duplicados = 0
    errores = 0
    mensajes_error = []
    
    for obs in observaciones:
        try:
            # Verificar si ya existe
            existe = db.query(ObservacionNaturalista).filter(
                ObservacionNaturalista.id_ejemplar == obs.id_ejemplar
            ).first()
            
            if existe:
                duplicados += 1
                continue
            
            db_observacion = ObservacionNaturalista(
                id_ejemplar=obs.id_ejemplar,
                id_nombre_cat_valido=obs.id_nombre_cat_valido,
                especie_valida_busqueda=obs.especie_valida_busqueda,
                comentarios_cat_valido=obs.comentarios_cat_valido,
                categoria_taxonomica=obs.categoria_taxonomica,
                entid=obs.entid,
                munid=obs.munid,
                anpid=obs.anpid,
                ecorid=obs.ecorid,
                latitud=obs.latitud,
                longitud=obs.longitud,
                localidad=obs.localidad,
                municipio=obs.municipio,
                estado=obs.estado,
                pais=obs.pais,
                fecha_colecta=obs.fecha_colecta,
                colector=obs.colector,
                coleccion=obs.coleccion,
                probable_loc_no_de_campo=obs.probable_loc_no_de_campo,
                ejemplar_fosil=obs.ejemplar_fosil,
                institucion=obs.institucion,
                pais_coleccion=obs.pais_coleccion,
                proyecto=obs.proyecto,
                url_proyecto=obs.url_proyecto,
                url_ejemplar=obs.url_ejemplar,
                url_origen=obs.url_origen,
                id_original=obs.id_original,
                tipo_coleccion=obs.tipo_coleccion,
                id_nombre_cat_valido_orig=obs.id_nombre_cat_valido_orig
            )
            db.add(db_observacion)
            insertados += 1
            
        except Exception as e:
            errores += 1
            mensajes_error.append(f"Error en {obs.id_ejemplar}: {str(e)}")
    
    db.commit()
    
    return {
        "insertados": insertados,
        "duplicados": duplicados,
        "errores": errores,
        "mensajes_error": mensajes_error
    }


def obtener_observaciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    municipio: Optional[str] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    especie: Optional[str] = None
) -> List[ObservacionNaturalista]:
    """Obtener lista de observaciones con filtros opcionales"""
    query = db.query(ObservacionNaturalista)
    
    if estado:
        query = query.filter(ObservacionNaturalista.estado.ilike(f"%{estado}%"))
    if municipio:
        query = query.filter(ObservacionNaturalista.municipio.ilike(f"%{municipio}%"))
    if fecha_inicio:
        query = query.filter(ObservacionNaturalista.fecha_colecta >= fecha_inicio)
    if fecha_fin:
        query = query.filter(ObservacionNaturalista.fecha_colecta <= fecha_fin)
    if especie:
        query = query.filter(ObservacionNaturalista.especie_valida_busqueda.ilike(f"%{especie}%"))
    
    return query.order_by(ObservacionNaturalista.fecha_colecta.desc()).offset(skip).limit(limit).all()


def obtener_observacion_por_id(db: Session, observacion_id: int) -> Optional[ObservacionNaturalista]:
    """Obtener una observación específica por ID"""
    return db.query(ObservacionNaturalista).filter(ObservacionNaturalista.id == observacion_id).first()


def obtener_observacion_por_id_ejemplar(db: Session, id_ejemplar: str) -> Optional[ObservacionNaturalista]:
    """Obtener una observación por ID de ejemplar (SNIB)"""
    return db.query(ObservacionNaturalista).filter(ObservacionNaturalista.id_ejemplar == id_ejemplar).first()


def contar_observaciones(
    db: Session,
    estado: Optional[str] = None,
    municipio: Optional[str] = None
) -> int:
    """Contar el total de observaciones con filtros opcionales"""
    query = db.query(ObservacionNaturalista)
    
    if estado:
        query = query.filter(ObservacionNaturalista.estado.ilike(f"%{estado}%"))
    if municipio:
        query = query.filter(ObservacionNaturalista.municipio.ilike(f"%{municipio}%"))
    
    return query.count()


def obtener_estadisticas(db: Session) -> dict:
    """Obtener estadísticas agregadas de las observaciones"""
    
    # Total de observaciones
    total = db.query(ObservacionNaturalista).count()
    
    # Por estado
    por_estado = {}
    estados_query = db.query(
        ObservacionNaturalista.estado,
        func.count(ObservacionNaturalista.id)
    ).group_by(ObservacionNaturalista.estado).all()
    
    for estado, count in estados_query:
        if estado:
            por_estado[estado] = count
    
    # Por municipio
    por_municipio = {}
    municipios_query = db.query(
        ObservacionNaturalista.municipio,
        func.count(ObservacionNaturalista.id)
    ).group_by(ObservacionNaturalista.municipio).order_by(
        func.count(ObservacionNaturalista.id).desc()
    ).limit(20).all()
    
    for municipio, count in municipios_query:
        if municipio:
            por_municipio[municipio] = count
    
    # Por año
    por_anio = {}
    anios_query = db.query(
        extract('year', ObservacionNaturalista.fecha_colecta).label('anio'),
        func.count(ObservacionNaturalista.id)
    ).filter(
        ObservacionNaturalista.fecha_colecta.isnot(None)
    ).group_by('anio').order_by('anio').all()
    
    for anio, count in anios_query:
        if anio:
            por_anio[int(anio)] = count
    
    # Rango de fechas
    fechas = db.query(
        func.min(ObservacionNaturalista.fecha_colecta),
        func.max(ObservacionNaturalista.fecha_colecta)
    ).first()
    
    rango_fechas = {
        "fecha_minima": str(fechas[0]) if fechas[0] else None,
        "fecha_maxima": str(fechas[1]) if fechas[1] else None
    }
    
    return {
        "total_observaciones": total,
        "por_estado": por_estado,
        "por_municipio": por_municipio,
        "por_anio": por_anio,
        "rango_fechas": rango_fechas
    }


def obtener_coordenadas_mapa(
    db: Session,
    estado: Optional[str] = None,
    municipio: Optional[str] = None,
    limit: int = 1000
) -> List[dict]:
    """Obtener coordenadas para visualización en mapa"""
    query = db.query(
        ObservacionNaturalista.id,
        ObservacionNaturalista.latitud,
        ObservacionNaturalista.longitud,
        ObservacionNaturalista.localidad,
        ObservacionNaturalista.municipio,
        ObservacionNaturalista.fecha_colecta,
        ObservacionNaturalista.url_origen
    )
    
    if estado:
        query = query.filter(ObservacionNaturalista.estado.ilike(f"%{estado}%"))
    if municipio:
        query = query.filter(ObservacionNaturalista.municipio.ilike(f"%{municipio}%"))
    
    resultados = query.limit(limit).all()
    
    return [
        {
            "id": r.id,
            "latitud": float(r.latitud),
            "longitud": float(r.longitud),
            "localidad": r.localidad,
            "municipio": r.municipio,
            "fecha": str(r.fecha_colecta) if r.fecha_colecta else None,
            "url_origen": r.url_origen
        }
        for r in resultados
    ]


def eliminar_observacion(db: Session, observacion_id: int) -> bool:
    """Eliminar una observación por ID"""
    db_observacion = db.query(ObservacionNaturalista).filter(
        ObservacionNaturalista.id == observacion_id
    ).first()
    
    if not db_observacion:
        return False
    
    db.delete(db_observacion)
    db.commit()
    return True


def eliminar_todas(db: Session) -> int:
    """Eliminar todas las observaciones (usar con precaución)"""
    count = db.query(ObservacionNaturalista).delete()
    db.commit()
    return count
