#!/usr/bin/env python3
"""
Script para importar observaciones de iNaturalist/CONABIO desde JSON a la base de datos.

Uso:
    python scripts/importar_observaciones_naturalista.py ruta/al/archivo.json

El archivo JSON debe contener las observaciones filtradas de Veracruz.
"""

import json
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar los módulos de la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.observacion_naturalista import ObservacionNaturalista


def parsear_fecha(fecha_str: str) -> datetime.date:
    """Convertir string de fecha a objeto date"""
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def transformar_registro(registro: dict) -> dict:
    """Transformar un registro del JSON al formato del modelo"""
    return {
        "idejemplar": registro.get("idejemplar"),
        "id_naturalista": registro.get("id"),
        "idnombrecatvalido": registro.get("idnombrecatvalido"),
        "especievalidabusqueda": registro.get("especievalidabusqueda"),
        "categoriataxonomica": registro.get("categoriataxonomica"),
        "comentarioscatvalido": registro.get("comentarioscatvalido"),
        "idnombrecatvalidoorig": registro.get("idnombrecatvalidoorig"),
        "entid": registro.get("entid"),
        "munid": registro.get("munid"),
        "anpid": registro.get("anpid"),
        "ecorid": registro.get("ecorid"),
        "latitud": registro.get("latitud"),
        "longitud": registro.get("longitud"),
        "localidad": registro.get("localidad"),
        "municipiomapa": registro.get("municipiomapa"),
        "estadomapa": registro.get("estadomapa"),
        "paismapa": registro.get("paismapa"),
        "fechacolecta": parsear_fecha(registro.get("fechacolecta")),
        "colector": registro.get("colector") or None,
        "coleccion": registro.get("coleccion"),
        "institucion": registro.get("institucion"),
        "paiscoleccion": registro.get("paiscoleccion"),
        "proyecto": registro.get("proyecto"),
        "tipocoleccion": registro.get("tipocoleccion"),
        "urlproyecto": registro.get("urlproyecto") or None,
        "urlejemplar": registro.get("urlejemplar"),
        "urlorigen": registro.get("urlorigen"),
        "probablelocnodecampo": registro.get("probablelocnodecampo") or None,
        "ejemplarfosil": registro.get("ejemplarfosil") or None,
    }


def importar_json(archivo_json: str, db: Session) -> dict:
    """
    Importar observaciones desde archivo JSON a la base de datos.
    
    Returns:
        dict con estadísticas de la importación
    """
    # Leer archivo JSON
    print(f"📖 Leyendo archivo: {archivo_json}")
    with open(archivo_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    print(f"📊 Total de registros en JSON: {len(datos)}")
    
    # Estadísticas
    insertados = 0
    duplicados = 0
    errores = 0
    
    # Procesar cada registro
    for i, registro in enumerate(datos):
        try:
            idejemplar = registro.get("idejemplar")
            
            # Verificar si ya existe
            existente = db.query(ObservacionNaturalista).filter(
                ObservacionNaturalista.idejemplar == idejemplar
            ).first()
            
            if existente:
                duplicados += 1
                continue
            
            # Transformar y crear registro
            datos_transformados = transformar_registro(registro)
            nueva_obs = ObservacionNaturalista(**datos_transformados)
            db.add(nueva_obs)
            insertados += 1
            
            # Commit cada 50 registros
            if insertados % 50 == 0:
                db.commit()
                print(f"  ✓ Procesados {i + 1}/{len(datos)} registros...")
                
        except Exception as e:
            errores += 1
            print(f"  ✗ Error en registro {i + 1}: {str(e)}")
            db.rollback()
    
    # Commit final
    db.commit()
    
    return {
        "total_json": len(datos),
        "insertados": insertados,
        "duplicados": duplicados,
        "errores": errores
    }


def crear_tablas():
    """Crear las tablas si no existen"""
    print("🔧 Verificando/creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ Tablas listas")


def main():
    if len(sys.argv) < 2:
        print("❌ Error: Debe especificar la ruta al archivo JSON")
        print("Uso: python scripts/importar_observaciones_naturalista.py ruta/al/archivo.json")
        sys.exit(1)
    
    archivo_json = sys.argv[1]
    
    if not os.path.exists(archivo_json):
        print(f"❌ Error: El archivo no existe: {archivo_json}")
        sys.exit(1)
    
    print("=" * 60)
    print("🦀 IMPORTADOR DE OBSERVACIONES iNATURALIST/CONABIO")
    print("=" * 60)
    
    # Crear tablas
    crear_tablas()
    
    # Crear sesión de BD
    db = SessionLocal()
    
    try:
        # Importar datos
        resultados = importar_json(archivo_json, db)
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE IMPORTACIÓN")
        print("=" * 60)
        print(f"  Total en JSON:    {resultados['total_json']}")
        print(f"  Insertados:       {resultados['insertados']}")
        print(f"  Duplicados:       {resultados['duplicados']}")
        print(f"  Errores:          {resultados['errores']}")
        print("=" * 60)
        
        if resultados['insertados'] > 0:
            print("✅ Importación completada exitosamente")
        else:
            print("⚠️  No se insertaron nuevos registros")
            
    except Exception as e:
        print(f"❌ Error durante la importación: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

