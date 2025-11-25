from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


class ObservacionNaturalistaBase(BaseModel):
    """Schema base para observaciones de iNaturalist/CONABIO"""
    
    id_ejemplar: str = Field(..., max_length=100, description="ID único del ejemplar en SNIB")
    id_nombre_cat_valido: Optional[str] = Field(None, max_length=50)
    especie_valida_busqueda: str = Field(..., max_length=100, description="Nombre científico")
    comentarios_cat_valido: Optional[str] = None
    categoria_taxonomica: Optional[str] = Field(None, max_length=50)
    
    # IDs geográficos
    entid: Optional[int] = None
    munid: Optional[int] = None
    anpid: Optional[int] = None
    ecorid: Optional[int] = None
    
    # Coordenadas
    latitud: float = Field(..., description="Latitud en grados decimales")
    longitud: float = Field(..., description="Longitud en grados decimales")
    
    # Localidad
    localidad: Optional[str] = Field(None, max_length=500)
    municipio: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field("MEXICO", max_length=100)
    
    # Colecta
    fecha_colecta: Optional[date] = None
    colector: Optional[str] = Field(None, max_length=255)
    coleccion: Optional[str] = Field(None, max_length=255)
    probable_loc_no_de_campo: Optional[str] = Field(None, max_length=255)
    ejemplar_fosil: Optional[str] = Field(None, max_length=50)
    
    # Institucional
    institucion: Optional[str] = Field(None, max_length=255)
    pais_coleccion: Optional[str] = Field(None, max_length=100)
    proyecto: Optional[str] = Field(None, max_length=100)
    
    # URLs
    url_proyecto: Optional[str] = Field(None, max_length=500)
    url_ejemplar: Optional[str] = Field(None, max_length=500)
    url_origen: Optional[str] = Field(None, max_length=500)
    
    # IDs originales
    id_original: Optional[int] = None
    tipo_coleccion: Optional[int] = None
    id_nombre_cat_valido_orig: Optional[str] = Field(None, max_length=50)


class ObservacionNaturalistaCreate(ObservacionNaturalistaBase):
    """Schema para crear una observación de Naturalista"""
    pass


class ObservacionNaturalistaImport(BaseModel):
    """
    Schema para importar datos del JSON de CONABIO.
    Mapea los nombres de campos del JSON original a los nombres del modelo.
    """
    idejemplar: str
    idnombrecatvalido: Optional[str] = None
    especievalidabusqueda: str
    comentarioscatvalido: Optional[str] = None
    categoriataxonomica: Optional[str] = None
    entid: Optional[int] = None
    munid: Optional[int] = None
    anpid: Optional[int] = None
    ecorid: Optional[int] = None
    latitud: float
    longitud: float
    localidad: Optional[str] = None
    municipiomapa: Optional[str] = None
    estadomapa: Optional[str] = None
    paismapa: Optional[str] = None
    fechacolecta: Optional[str] = None
    colector: Optional[str] = None
    coleccion: Optional[str] = None
    probablelocnodecampo: Optional[str] = None
    ejemplarfosil: Optional[str] = None
    institucion: Optional[str] = None
    paiscoleccion: Optional[str] = None
    proyecto: Optional[str] = None
    urlproyecto: Optional[str] = None
    urlejemplar: Optional[str] = None
    urlorigen: Optional[str] = None
    id: Optional[int] = None
    tipocoleccion: Optional[int] = None
    idnombrecatvalidoorig: Optional[str] = None

    def to_create_schema(self) -> ObservacionNaturalistaCreate:
        """Convierte del formato JSON de CONABIO al formato del modelo"""
        fecha = None
        if self.fechacolecta:
            try:
                fecha = datetime.strptime(self.fechacolecta, "%Y-%m-%d").date()
            except ValueError:
                fecha = None
        
        return ObservacionNaturalistaCreate(
            id_ejemplar=self.idejemplar,
            id_nombre_cat_valido=self.idnombrecatvalido,
            especie_valida_busqueda=self.especievalidabusqueda,
            comentarios_cat_valido=self.comentarioscatvalido,
            categoria_taxonomica=self.categoriataxonomica,
            entid=self.entid,
            munid=self.munid,
            anpid=self.anpid,
            ecorid=self.ecorid,
            latitud=self.latitud,
            longitud=self.longitud,
            localidad=self.localidad,
            municipio=self.municipiomapa,
            estado=self.estadomapa,
            pais=self.paismapa,
            fecha_colecta=fecha,
            colector=self.colector if self.colector else None,
            coleccion=self.coleccion,
            probable_loc_no_de_campo=self.probablelocnodecampo if self.probablelocnodecampo else None,
            ejemplar_fosil=self.ejemplarfosil if self.ejemplarfosil else None,
            institucion=self.institucion,
            pais_coleccion=self.paiscoleccion,
            proyecto=self.proyecto,
            url_proyecto=self.urlproyecto if self.urlproyecto else None,
            url_ejemplar=self.urlejemplar,
            url_origen=self.urlorigen,
            id_original=self.id,
            tipo_coleccion=self.tipocoleccion,
            id_nombre_cat_valido_orig=self.idnombrecatvalidoorig
        )


class ObservacionNaturalistaInDB(ObservacionNaturalistaBase):
    """Schema para observación en la base de datos"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ObservacionNaturalistaResponse(ObservacionNaturalistaInDB):
    """Schema para respuesta de la API"""
    pass


class ImportResult(BaseModel):
    """Schema para resultado de importación masiva"""
    total_procesados: int
    insertados: int
    duplicados: int
    errores: int
    mensajes_error: List[str] = []


class EstadisticasNaturalista(BaseModel):
    """Schema para estadísticas de observaciones de Naturalista"""
    total_observaciones: int
    por_estado: dict
    por_municipio: dict
    por_anio: dict
    rango_fechas: dict
