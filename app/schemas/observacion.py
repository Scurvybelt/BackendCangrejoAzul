from pydantic import BaseModel, Field, field_validator
from datetime import date, time, datetime
from typing import Optional, List
from enum import Enum

# Enums para las opciones del formulario
class FrecuenciaObservacion(str, Enum):
    nunca = "Nunca"
    rara_vez = "Rara vez (1–2 veces al año)"
    a_veces = "A veces (cada temporada)"
    frecuentemente = "Frecuentemente (varias veces al mes)"
    muy_frecuentemente = "Muy frecuentemente (casi todos los días)"

class TipoHabitat(str, Enum):
    manglar = "Manglar"
    humedal = "Humedal / laguna"
    playa = "Playa / costa"
    carretera = "Carretera"
    zona_urbana = "Zona urbana"
    otro = "Otro"

class CantidadCangrejo(str, Enum):
    uno_cinco = "1–5"
    seis_veinte = "6–20"
    veintiuno_cincuenta = "21–50"
    mas_cincuenta = "Más de 50"

class SexoCangrejo(str, Enum):
    machos = "Machos"
    hembras = "Hembras"
    hembras_huevos = "Hembras con huevos (ovígeras)"
    no_se = "No sé identificarlo"

class TamanoCangrejo(str, Enum):
    pequenos = "Pequeños (<5 cm ancho de caparazón)"
    medianos = "Medianos (5–10 cm)"
    grandes = "Grandes (>10 cm)"
    mezcla = "Mezcla de tamaños"

class ComportamientoCangrejo(str, Enum):
    migrando = "Migrando (movimiento en grupo hacia agua)"
    alimentandose = "Alimentándose"
    escondiendose = "Escondiéndose en vegetación"
    cruzando_carretera = "Cruzando carretera"
    madrigueras = "Dentro o cerca de madrigueras"
    otro = "Otro"

class Mortalidad(str, Enum):
    si_muchos = "Sí, muchos (>10)"
    si_pocos = "Sí, pocos (1–10)"
    no = "No"

class CambiosPoblacion(str, Enum):
    mucho_menor = "Mucho menor"
    menor = "Menor"
    igual = "Igual"
    mayor = "Mayor"
    no_se = "No sé"

class Amenaza(str, Enum):
    perdida_habitat = "Pérdida de manglar/hábitat"
    captura_excesiva = "Captura excesiva"
    carreteras = "Carreteras y atropellamiento"
    contaminacion = "Contaminación"
    cambio_climatico = "Cambio climático (sequías, inundaciones)"
    otro = "Otro"

# Schema base para crear observación
class ObservacionBase(BaseModel):
    # Sección 1: Datos generales del observador
    nombre_observador: Optional[str] = Field(None, max_length=255, description="Nombre del observador (opcional)")
    edad: Optional[int] = Field(None, ge=1, le=120, description="Edad del observador")
    comunidad: str = Field(..., max_length=255, description="Comunidad o localidad donde vive")
    frecuencia_observacion: FrecuenciaObservacion = Field(..., description="Frecuencia con la que observa cangrejos")
    
    # Sección 2: Observación del cangrejo
    fecha_observacion: date = Field(..., description="Fecha de la observación")
    hora_observacion: time = Field(..., description="Hora de la observación")
    lugar_observacion: str = Field(..., max_length=500, description="Lugar específico de observación")
    tipo_habitat: TipoHabitat = Field(..., description="Tipo de hábitat donde observó los cangrejos")
    tipo_habitat_otro: Optional[str] = Field(None, max_length=255, description="Especificar si tipo_habitat es 'Otro'")
    cantidad_cangrejos: CantidadCangrejo = Field(..., description="Cantidad aproximada de cangrejos observados")
    
    # Sección 3: Identificación
    sexo_cangrejos: List[SexoCangrejo] = Field(..., min_length=1, description="Sexo de los cangrejos observados (puede ser múltiple)")
    tamano_cangrejos: TamanoCangrejo = Field(..., description="Tamaño aproximado de los cangrejos")
    
    # Sección 4: Comportamientos observados
    comportamientos: List[ComportamientoCangrejo] = Field(..., min_length=1, description="Comportamientos observados (puede ser múltiple)")
    comportamiento_otro: Optional[str] = Field(None, max_length=255, description="Especificar si comportamiento es 'Otro'")
    mortalidad_atropellamiento: Mortalidad = Field(..., description="Si observó mortalidad por atropellamiento")
    
    # Sección 5: Percepción local
    cambio_poblacion: CambiosPoblacion = Field(..., description="Cambio percibido en la población en los últimos 5 años")
    amenazas_principales: List[Amenaza] = Field(..., min_length=1, description="Principales amenazas percibidas (puede ser múltiple)")
    amenaza_otra: Optional[str] = Field(None, max_length=255, description="Especificar si amenaza es 'Otro'")
    importancia_conservacion: int = Field(..., ge=1, le=5, description="Importancia de la conservación (1-5)")
    acciones_proteccion: str = Field(..., min_length=10, description="Acciones necesarias para proteger los cangrejos")
    
    # Validadores
    @field_validator('tipo_habitat_otro')
    @classmethod
    def validar_tipo_habitat_otro(cls, v, info):
        if info.data.get('tipo_habitat') == TipoHabitat.otro and not v:
            raise ValueError('Debe especificar el tipo de hábitat cuando selecciona "Otro"')
        return v
    
    @field_validator('comportamiento_otro')
    @classmethod
    def validar_comportamiento_otro(cls, v, info):
        comportamientos = info.data.get('comportamientos', [])
        if ComportamientoCangrejo.otro in comportamientos and not v:
            raise ValueError('Debe especificar el comportamiento cuando selecciona "Otro"')
        return v
    
    @field_validator('amenaza_otra')
    @classmethod
    def validar_amenaza_otra(cls, v, info):
        amenazas = info.data.get('amenazas_principales', [])
        if Amenaza.otro in amenazas and not v:
            raise ValueError('Debe especificar la amenaza cuando selecciona "Otro"')
        return v

# Schema para crear observación (hereda de base)
class ObservacionCreate(ObservacionBase):
    pass

# Schema para actualizar observación (todos los campos opcionales)
class ObservacionUpdate(BaseModel):
    nombre_observador: Optional[str] = None
    edad: Optional[int] = None
    comunidad: Optional[str] = None
    frecuencia_observacion: Optional[FrecuenciaObservacion] = None
    fecha_observacion: Optional[date] = None
    hora_observacion: Optional[time] = None
    lugar_observacion: Optional[str] = None
    tipo_habitat: Optional[TipoHabitat] = None
    tipo_habitat_otro: Optional[str] = None
    cantidad_cangrejos: Optional[CantidadCangrejo] = None
    sexo_cangrejos: Optional[List[SexoCangrejo]] = None
    tamano_cangrejos: Optional[TamanoCangrejo] = None
    comportamientos: Optional[List[ComportamientoCangrejo]] = None
    comportamiento_otro: Optional[str] = None
    mortalidad_atropellamiento: Optional[Mortalidad] = None
    cambio_poblacion: Optional[CambiosPoblacion] = None
    amenazas_principales: Optional[List[Amenaza]] = None
    amenaza_otra: Optional[str] = None
    importancia_conservacion: Optional[int] = Field(None, ge=1, le=5)
    acciones_proteccion: Optional[str] = None

# Schema para respuesta con foto URL
class ObservacionConFoto(ObservacionBase):
    foto_url: Optional[str] = Field(None, max_length=500, description="URL de la foto/video subido")

# Schema para respuesta de la BD
class ObservacionInDB(ObservacionBase):
    id: int
    user_id: int
    foto_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema para respuesta pública (incluye info básica del usuario)
class ObservacionResponse(ObservacionInDB):
    usuario_email: Optional[str] = None
    usuario_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True
