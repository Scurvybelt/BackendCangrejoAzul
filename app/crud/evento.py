from sqlalchemy.orm import Session
from app.models.evento import Evento
from app.models.user import User
from app.schemas.evento import EventoCreate, EventoUpdate
from typing import List, Optional
from datetime import date

def get_evento_by_id(db: Session, evento_id: int):
    """Obtener evento por ID"""
    return db.query(Evento).filter(Evento.id == evento_id).first()

def get_eventos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    tipo: Optional[str] = None,
    fecha_desde: Optional[date] = None
):
    """Obtener lista de eventos con filtros opcionales"""
    query = db.query(Evento)
    
    if tipo:
        query = query.filter(Evento.tipo == tipo)
    
    if fecha_desde:
        query = query.filter(Evento.fecha >= fecha_desde)
    
    return query.order_by(Evento.fecha.desc(), Evento.hora.desc()).offset(skip).limit(limit).all()

def create_evento(db: Session, evento: EventoCreate, creado_por_id: int):
    """Crear un nuevo evento (solo admins)"""
    db_evento = Evento(
        titulo=evento.titulo,
        descripcion=evento.descripcion,
        fecha=evento.fecha,
        hora=evento.hora,
        lugar=evento.lugar,
        duracion=evento.duracion,
        requisitos=evento.requisitos,
        tipo=evento.tipo,
        creado_por_id=creado_por_id
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

def update_evento(db: Session, evento_id: int, evento_data: EventoUpdate):
    """Actualizar datos de evento"""
    evento = get_evento_by_id(db, evento_id)
    if evento:
        update_data = evento_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(evento, key, value)
        db.commit()
        db.refresh(evento)
    return evento

def delete_evento(db: Session, evento_id: int):
    """Eliminar evento"""
    evento = get_evento_by_id(db, evento_id)
    if evento:
        db.delete(evento)
        db.commit()
    return evento

def inscribir_usuario(db: Session, evento_id: int, user_id: int):
    """Inscribir un usuario a un evento"""
    evento = get_evento_by_id(db, evento_id)
    user = db.query(User).filter(User.id == user_id).first()
    
    if evento and user:
        # Verificar si ya está inscrito
        if user not in evento.personas_inscritas:
            evento.personas_inscritas.append(user)
            db.commit()
            db.refresh(evento)
    return evento

def desinscribir_usuario(db: Session, evento_id: int, user_id: int):
    """Desinscribir un usuario de un evento"""
    evento = get_evento_by_id(db, evento_id)
    user = db.query(User).filter(User.id == user_id).first()
    
    if evento and user:
        if user in evento.personas_inscritas:
            evento.personas_inscritas.remove(user)
            db.commit()
            db.refresh(evento)
    return evento

def get_eventos_usuario(db: Session, user_id: int):
    """Obtener eventos en los que está inscrito un usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user.eventos_inscritos
    return []
