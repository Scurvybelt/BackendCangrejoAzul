from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Numeric
from sqlalchemy.sql import func
from app.core.database import Base


class ObservacionNaturalista(Base):
    """Modelo para observaciones de iNaturalist/CONABIO"""
    __tablename__ = "observaciones_naturalista"
    
    id = Column(Integer, primary_key=True, index=True)
    id_ejemplar = Column(String(100), unique=True, nullable=False)
    id_nombre_cat_valido = Column(String(50))
    especie_valida_busqueda = Column(String(100), nullable=False)
    comentarios_cat_valido = Column(Text)
    categoria_taxonomica = Column(String(50))
    entid = Column(Integer)
    munid = Column(Integer)
    anpid = Column(Integer)
    ecorid = Column(Integer)
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)
    localidad = Column(String(500))
    municipio = Column(String(100))
    estado = Column(String(100))
    pais = Column(String(100), default="MEXICO")
    fecha_colecta = Column(Date)
    colector = Column(String(255))
    coleccion = Column(String(255))
    probable_loc_no_de_campo = Column(String(255))
    ejemplar_fosil = Column(String(50))
    institucion = Column(String(255))
    pais_coleccion = Column(String(100))
    proyecto = Column(String(100))
    url_proyecto = Column(String(500))
    url_ejemplar = Column(String(500))
    url_origen = Column(String(500))
    id_original = Column(Integer)
    tipo_coleccion = Column(Integer)
    id_nombre_cat_valido_orig = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
