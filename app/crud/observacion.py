from sqlalchemy.orm import Session, joinedload
from app.models.observacion import Observacion
from app.schemas.observacion import ObservacionCreate, ObservacionUpdate
from typing import List, Optional
from datetime import date

def crear_observacion(db: Session, observacion: ObservacionCreate, user_id: int) -> Observacion:
    """Crear una nueva observación"""
    # Convertir los enums a sus valores de string para guardar en JSON
    sexo_cangrejos_values = [sexo.value for sexo in observacion.sexo_cangrejos]
    comportamientos_values = [comp.value for comp in observacion.comportamientos]
    amenazas_values = [amenaza.value for amenaza in observacion.amenazas_principales]
    
    db_observacion = Observacion(
        user_id=user_id,
        nombre_observador=observacion.nombre_observador,
        edad=observacion.edad,
        comunidad=observacion.comunidad,
        frecuencia_observacion=observacion.frecuencia_observacion,
        fecha_observacion=observacion.fecha_observacion,
        hora_observacion=observacion.hora_observacion,
        lugar_observacion=observacion.lugar_observacion,
        tipo_habitat=observacion.tipo_habitat,
        tipo_habitat_otro=observacion.tipo_habitat_otro,
        cantidad_cangrejos=observacion.cantidad_cangrejos,
        sexo_cangrejos=sexo_cangrejos_values,
        tamano_cangrejos=observacion.tamano_cangrejos,
        comportamientos=comportamientos_values,
        comportamiento_otro=observacion.comportamiento_otro,
        mortalidad_atropellamiento=observacion.mortalidad_atropellamiento,
        cambio_poblacion=observacion.cambio_poblacion,
        amenazas_principales=amenazas_values,
        amenaza_otra=observacion.amenaza_otra,
        importancia_conservacion=observacion.importancia_conservacion,
        acciones_proteccion=observacion.acciones_proteccion
    )
    
    db.add(db_observacion)
    db.commit()
    db.refresh(db_observacion)
    return db_observacion

def obtener_observaciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    comunidad: Optional[str] = None
) -> List[Observacion]:
    """Obtener lista de observaciones con filtros opcionales"""
    query = db.query(Observacion).options(joinedload(Observacion.usuario))
    
    if user_id:
        query = query.filter(Observacion.user_id == user_id)
    if fecha_inicio:
        query = query.filter(Observacion.fecha_observacion >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Observacion.fecha_observacion <= fecha_fin)
    if comunidad:
        query = query.filter(Observacion.comunidad.ilike(f"%{comunidad}%"))
    
    return query.offset(skip).limit(limit).all()

def obtener_observacion_por_id(db: Session, observacion_id: int) -> Optional[Observacion]:
    """Obtener una observación específica por ID"""
    return db.query(Observacion).options(joinedload(Observacion.usuario)).filter(Observacion.id == observacion_id).first()

def obtener_observaciones_usuario(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Observacion]:
    """Obtener todas las observaciones de un usuario específico"""
    return db.query(Observacion).filter(Observacion.user_id == user_id).offset(skip).limit(limit).all()

def actualizar_observacion(
    db: Session,
    observacion_id: int,
    observacion_update: ObservacionUpdate,
    user_id: int
) -> Optional[Observacion]:
    """Actualizar una observación existente (solo el creador puede actualizar)"""
    db_observacion = db.query(Observacion).filter(
        Observacion.id == observacion_id,
        Observacion.user_id == user_id
    ).first()
    
    if not db_observacion:
        return None
    
    # Actualizar solo los campos que se proporcionaron
    update_data = observacion_update.model_dump(exclude_unset=True)
    
    # Convertir enums a valores de string para campos JSON si están presentes
    if 'sexo_cangrejos' in update_data:
        update_data['sexo_cangrejos'] = [sexo.value for sexo in update_data['sexo_cangrejos']]
    if 'comportamientos' in update_data:
        update_data['comportamientos'] = [comp.value for comp in update_data['comportamientos']]
    if 'amenazas_principales' in update_data:
        update_data['amenazas_principales'] = [amenaza.value for amenaza in update_data['amenazas_principales']]
    
    for field, value in update_data.items():
        setattr(db_observacion, field, value)
    
    db.commit()
    db.refresh(db_observacion)
    return db_observacion

def actualizar_foto_observacion(db: Session, observacion_id: int, foto_url: str, user_id: int) -> Optional[Observacion]:
    """Actualizar solo la foto de una observación"""
    db_observacion = db.query(Observacion).filter(
        Observacion.id == observacion_id,
        Observacion.user_id == user_id
    ).first()
    
    if not db_observacion:
        return None
    
    db_observacion.foto_url = foto_url
    db.commit()
    db.refresh(db_observacion)
    return db_observacion

def eliminar_observacion(db: Session, observacion_id: int, user_id: int) -> bool:
    """Eliminar una observación (solo el creador puede eliminar)"""
    db_observacion = db.query(Observacion).filter(
        Observacion.id == observacion_id,
        Observacion.user_id == user_id
    ).first()
    
    if not db_observacion:
        return False
    
    db.delete(db_observacion)
    db.commit()
    return True

def contar_observaciones_usuario(db: Session, user_id: int) -> int:
    """Contar el total de observaciones de un usuario"""
    return db.query(Observacion).filter(Observacion.user_id == user_id).count()

def contar_observaciones_total(db: Session) -> int:
    """Contar el total de observaciones en el sistema"""
    return db.query(Observacion).count()
