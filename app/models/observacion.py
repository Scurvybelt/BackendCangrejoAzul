from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Time, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class FrecuenciaObservacionEnum(str, enum.Enum):
    nunca = "Nunca"
    rara_vez = "Rara vez (1–2 veces al año)"
    a_veces = "A veces (cada temporada)"
    frecuentemente = "Frecuentemente (varias veces al mes)"
    muy_frecuentemente = "Muy frecuentemente (casi todos los días)"

class TipoHabitatEnum(str, enum.Enum):
    manglar = "Manglar"
    humedal = "Humedal / laguna"
    playa = "Playa / costa"
    carretera = "Carretera"
    zona_urbana = "Zona urbana"
    otro = "Otro"

class CantidadCangrejoEnum(str, enum.Enum):
    uno_cinco = "1–5"
    seis_veinte = "6–20"
    veintiuno_cincuenta = "21–50"
    mas_cincuenta = "Más de 50"

class TamanoCangrejoEnum(str, enum.Enum):
    pequenos = "Pequeños (<5 cm ancho de caparazón)"
    medianos = "Medianos (5–10 cm)"
    grandes = "Grandes (>10 cm)"
    mezcla = "Mezcla de tamaños"

class MortalidadEnum(str, enum.Enum):
    si_muchos = "Sí, muchos (>10)"
    si_pocos = "Sí, pocos (1–10)"
    no = "No"

class CambiosPoblacionEnum(str, enum.Enum):
    mucho_menor = "Mucho menor"
    menor = "Menor"
    igual = "Igual"
    mayor = "Mayor"
    no_se = "No sé"

class Observacion(Base):
    __tablename__ = "observaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con el usuario que realizó la observación
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    usuario = relationship("User", backref="observaciones")
    
    # Sección 1: Datos generales del observador
    nombre_observador = Column(String(255), nullable=True, comment="Opcional")
    edad = Column(Integer, nullable=True)
    comunidad = Column(String(255), nullable=False)
    frecuencia_observacion = Column(SQLEnum(FrecuenciaObservacionEnum), nullable=False)
    
    # Sección 2: Observación del cangrejo
    fecha_observacion = Column(Date, nullable=False)
    hora_observacion = Column(Time, nullable=False)
    lugar_observacion = Column(String(500), nullable=False, comment="Colonia, playa, carretera, manglar, etc.")
    tipo_habitat = Column(SQLEnum(TipoHabitatEnum), nullable=False)
    tipo_habitat_otro = Column(String(255), nullable=True, comment="Si seleccionó 'Otro' en tipo_habitat")
    cantidad_cangrejos = Column(SQLEnum(CantidadCangrejoEnum), nullable=False)
    
    # Sección 3: Identificación
    # JSON array con las opciones seleccionadas: ["Machos", "Hembras", "Hembras con huevos", "No sé identificarlo"]
    sexo_cangrejos = Column(JSON, nullable=False, comment="Array de opciones seleccionadas")
    tamano_cangrejos = Column(SQLEnum(TamanoCangrejoEnum), nullable=False)
    
    # Sección 4: Comportamientos observados
    # JSON array con las opciones seleccionadas
    comportamientos = Column(JSON, nullable=False, comment="Array de comportamientos observados")
    comportamiento_otro = Column(String(255), nullable=True, comment="Si seleccionó 'Otro' en comportamientos")
    mortalidad_atropellamiento = Column(SQLEnum(MortalidadEnum), nullable=False)
    
    # Sección 5: Percepción local
    cambio_poblacion = Column(SQLEnum(CambiosPoblacionEnum), nullable=False)
    # JSON array con las amenazas seleccionadas
    amenazas_principales = Column(JSON, nullable=False, comment="Array de amenazas percibidas")
    amenaza_otra = Column(String(255), nullable=True, comment="Si seleccionó 'Otro' en amenazas")
    importancia_conservacion = Column(Integer, nullable=False, comment="Escala 1-5")
    acciones_proteccion = Column(Text, nullable=False, comment="Respuesta abierta")
    
    # Sección 6: Evidencia
    foto_url = Column(String(500), nullable=True, comment="URL o ruta del archivo de foto/video")
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
