from sqlalchemy import Column, Integer, String, DateTime, Text, Time, Date, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class TipoEventoEnum(str, enum.Enum):
    limpieza = "Limpieza"
    voluntariado = "Voluntariado"

# Tabla intermedia para la relación muchos-a-muchos entre eventos y usuarios inscritos
evento_usuarios = Table(
    'evento_usuarios',
    Base.metadata,
    Column('evento_id', Integer, ForeignKey('eventos.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('inscrito_at', DateTime(timezone=True), server_default=func.now())
)

class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    lugar = Column(String(255), nullable=False)
    duracion = Column(Integer, nullable=False, comment="Duración en minutos")
    requisitos = Column(Text)
    tipo = Column(Enum(TipoEventoEnum), nullable=False)
    
    # Relación con el admin que creó el evento
    creado_por_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    creado_por = relationship("User", foreign_keys=[creado_por_id], back_populates="eventos_creados")
    
    # Relación muchos-a-muchos con usuarios inscritos
    personas_inscritas = relationship(
        "User",
        secondary=evento_usuarios,
        back_populates="eventos_inscritos"
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def total_inscritos(self) -> int:
        """Retorna el número de personas inscritas en el evento"""
        return len(self.personas_inscritas)
