"""
Endpoints para obtener información de configuración del sistema.
Proporciona acceso a los archivos de configuración YAML en formato JSON.
"""

from fastapi import APIRouter, HTTPException
from core.config.config_manager import config

router = APIRouter()


@router.get("/parametros", 
           summary="Obtener parámetros de cómputo", 
           description="Obtiene todos los parámetros de cómputo anual en formato JSON")
async def get_parametros_computo():
    """
    Obtiene los parámetros de cómputo anual.
    
    Returns:
        Dict: Parámetros de cómputo indexados por año
    """
    try:
        parametros = config.cargar_parametros_computo()
        return {
            "success": True,
            "data": parametros,
            "total_años": len(parametros),
            "años_disponibles": sorted(parametros.keys()) if parametros else [],
            "descripcion": "Parámetros de cómputo anual para cálculo de bases de cotización"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo parámetros: {str(e)}")


@router.get("/indices", 
           summary="Obtener índices de revalorización", 
           description="Obtiene todos los índices de revalorización en formato JSON")
async def get_indices_revalorizacion():
    """
    Obtiene los índices de revalorización.
    
    Returns:
        Dict: Índices de revalorización indexados por mes/año
    """
    try:
        indices = config.cargar_indices_revalorizacion()
        return {
            "success": True,
            "data": indices,
            "total_indices": len(indices),
            "rango_fechas": {
                "desde": min(indices.keys()) if indices else None,
                "hasta": max(indices.keys()) if indices else None
            },
            "descripcion": "Índices de revalorización para actualizar bases históricas"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo índices: {str(e)}")


@router.get("/topes", 
           summary="Obtener topes de cotización", 
           description="Obtiene todos los topes de cotización (bases mínimas y máximas) en formato JSON")
async def get_topes_cotizacion():
    """
    Obtiene los topes de cotización (bases mínimas y máximas).
    
    Returns:
        Dict: Topes de cotización indexados por año
    """
    try:
        topes = config.cargar_topes_cotizacion()
        return {
            "success": True,
            "data": topes,
            "total_años": len(topes),
            "años_disponibles": sorted(topes.keys()) if topes else [],
            "descripcion": "Topes de cotización (bases mínimas y máximas) por año"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo topes: {str(e)}")


@router.get("/all", 
           summary="Obtener toda la configuración", 
           description="Obtiene toda la configuración del sistema en un solo endpoint")
async def get_configuracion_completa():
    """
    Obtiene toda la configuración del sistema.
    
    Returns:
        Dict: Toda la configuración disponible
    """
    try:
        parametros = config.cargar_parametros_computo()
        indices = config.cargar_indices_revalorizacion()
        topes = config.cargar_topes_cotizacion()
        
        return {
            "success": True,
            "configuracion": {
                "parametros_computo": {
                    "data": parametros,
                    "total_años": len(parametros),
                    "años_disponibles": sorted(parametros.keys()) if parametros else []
                },
                "indices_revalorizacion": {
                    "data": indices,
                    "total_indices": len(indices),
                    "rango_fechas": {
                        "desde": min(indices.keys()) if indices else None,
                        "hasta": max(indices.keys()) if indices else None
                    }
                },
                "topes_cotizacion": {
                    "data": topes,
                    "total_años": len(topes),
                    "años_disponibles": sorted(topes.keys()) if topes else []
                }
            },
            "resumen": {
                "total_parametros": len(parametros),
                "total_indices": len(indices),
                "total_topes": len(topes),
                "configuracion_cargada": True
            },
            "descripcion": "Configuración completa del sistema de cálculo de bases de cotización"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración completa: {str(e)}") 