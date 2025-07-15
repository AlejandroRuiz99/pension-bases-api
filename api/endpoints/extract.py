"""
Endpoint para extraer bases de cotización de archivos PDF.
"""

import tempfile
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from services.extractor import ExtractorBasesCotizacion
from models.api_models import ExtractResponse, ErrorResponse
from core.config.errors import BasesParserError


router = APIRouter()


@router.post(
    "/extract", 
    response_model=ExtractResponse,
    summary="📄 Extraer bases de cotización",
    description="""
    Extrae automáticamente las bases de cotización de un archivo PDF.
    
    ### 📋 Que hace este endpoint:
    * Procesa archivos PDF de la Seguridad Social
    * Identifica automáticamente empresas y regímenes
    * Extrae todas las bases de cotización por mes/año
    * Valida y estructura los datos extraídos
    
    ### 📄 Formato soportado:
    * **PDFs estándar** de bases de cotización de la Seguridad Social
    * Tamaño máximo: **10MB**
    
    ### 📊 Datos extraídos:
    * Mes/año de cotización
    * Base de cotización mensual
    * Empresa empleadora
    * Régimen de cotización
    
    ### ✅ Respuesta exitosa:
    Devuelve todas las bases encontradas con metadatos del archivo procesado.
    """,
    responses={
        200: {
            "description": "Bases extraídas correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Se extrajeron 24 bases de cotización exitosamente",
                        "total_bases": 24,
                        "bases": [
                            {
                                "mes_anyo": "01/2023",
                                "base": 2500.50,
                                "empresa": "EMPRESA EJEMPLO SL",
                                "regimen": "GENERAL"
                            }
                        ],
                        "metadata": {
                            "filename": "bases_cotizacion.pdf",
                            "file_size": 1024000,
                            "total_empresas": 2,
                            "periodo_bases": {
                                "desde": "01/2022",
                                "hasta": "12/2023"
                            }
                        }
                    }
                }
            }
        },
        400: {"description": "Error en el archivo o formato no válido"},
        500: {"description": "Error interno del servidor"}
    }
)
async def extract_bases(file: UploadFile = File(..., description="📁 Archivo PDF con bases de cotización")):
    """
    Extrae bases de cotización de un archivo PDF.
    
    Args:
        file: Archivo PDF con las bases de cotización
        
    Returns:
        ExtractResponse: Bases extraídas y metadatos
        
    Raises:
        HTTPException: Si hay errores en el procesamiento
    """
    # Validar tipo de archivo
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF"
        )
    
    # Validar tamaño del archivo (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail="El archivo es demasiado grande. Máximo 10MB"
        )
    
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Leer y guardar el contenido del archivo
            content = await file.read()
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # Extraer bases usando el servicio
            extractor = ExtractorBasesCotizacion(temp_file_path)
            resultado = extractor.run()
            
            # Preparar metadatos
            metadata = {
                "filename": file.filename,
                "file_size": len(content),
                "total_empresas": len(set(base.empresa for base in resultado.bases)),
                "periodo_bases": {
                    "desde": min(base.mes_anyo for base in resultado.bases) if resultado.bases else None,
                    "hasta": max(base.mes_anyo for base in resultado.bases) if resultado.bases else None
                }
            }
            
            return ExtractResponse(
                success=True,
                message=f"Se extrajeron {len(resultado.bases)} bases de cotización exitosamente",
                total_bases=len(resultado.bases),
                bases=resultado.bases,
                metadata=metadata
            )
            
        finally:
            # Limpiar archivo temporal
            if temp_file_path.exists():
                temp_file_path.unlink()
                
    except BasesParserError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/extract/health")
async def extract_health():
    """Endpoint de salud para el servicio de extracción."""
    return {"status": "healthy", "service": "extraction"}
