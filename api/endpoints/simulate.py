"""
Endpoint para simular períodos y calcular base reguladora.
"""

import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse

from services.simulator import SimuladorPeriodos
from services.extractor import ExtractorBasesCotizacion
from models.api_models import SimulateRequest, SimulateResponse, EstadisticasResponse, ErrorResponse
from core.config.errors import BasesParserError


router = APIRouter()


@router.post(
    "/process",
    response_model=SimulateResponse,
    summary="🚀 Procesar PDF completo (Extraer + Simular)",
    description="""
    Endpoint completo que extrae bases de un PDF y calcula automáticamente la base reguladora.
    
    ### 🎯 Proceso completo en un solo paso:
    1. **📄 Extrae bases** del archivo PDF proporcionado
    2. **🧮 Simula períodos** hasta la fecha de jubilación
    3. **📊 Calcula base reguladora** final
    
    ### 📋 Parámetros necesarios:
    * **Archivo PDF** con bases de cotización
    * **Fecha de jubilación** en formato MM/YYYY
    * **Régimen de acceso** (GENERAL o AUTONOMO)
    * **Sexo del cotizante** (MASCULINO o FEMENINO) - Para cálculo correcto de lagunas
    
    ### ✅ Ventajas:
    * **Un solo endpoint** para todo el proceso
    * **Automático** - no necesitas llamar extract + simulate
    * **Eficiente** - procesa todo en memoria
    * **Resultado completo** con estadísticas detalladas
    
    ### 📊 Respuesta:
    Devuelve el mismo resultado que `/simulate` pero con las bases extraídas automáticamente del PDF.
    """,
    responses={
        200: {
            "description": "Procesamiento completado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "PDF procesado y simulación completada exitosamente",
                        "estadisticas": {
                            "total_bases": 24,
                            "base_reguladora": 2028.57,
                            "suma_total": 710000.00
                        },
                        "metadata_extraccion": {
                            "total_bases_extraidas": 24,
                            "periodo_extraido": "01/2023 - 12/2024"
                        }
                    }
                }
            }
        },
        400: {"description": "Error en el archivo PDF o parámetros"},
        500: {"description": "Error interno del servidor"}
    }
)
async def process_pdf_complete(
    file: UploadFile = File(..., description="📁 Archivo PDF con bases de cotización"),
    fecha_jubilacion: str = Form(..., description="📅 Fecha de jubilación (MM/YYYY)"),
    regimen_acceso: str = Form(default="GENERAL", description="⚙️ Régimen de acceso"),
    sexo: str = Form(..., description="👤 Sexo del cotizante (MASCULINO o FEMENINO)")
):
    """
    Procesa un PDF completo: extrae bases y calcula base reguladora automáticamente.
    
    Args:
        file: Archivo PDF con bases de cotización
        fecha_jubilacion: Fecha de jubilación en formato MM/YYYY  
        regimen_acceso: Régimen de acceso (GENERAL o AUTONOMO)
        
    Returns:
        SimulateResponse: Resultado completo con base reguladora y estadísticas
        
    Raises:
        HTTPException: Si hay errores en el procesamiento
    """
    # Validar archivo PDF
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
    
    # Validar formato de fecha
    import re
    if not re.match(r'^\d{2}/\d{4}$', fecha_jubilacion):
        raise HTTPException(
            status_code=400,
            detail="Fecha de jubilación debe estar en formato MM/YYYY"
        )
    
    # Validar régimen
    if regimen_acceso.upper() not in ["GENERAL", "AUTONOMO"]:
        raise HTTPException(
            status_code=400,
            detail="Régimen debe ser GENERAL o AUTONOMO"
        )
    
    # Validar sexo
    if sexo.upper() not in ["MASCULINO", "FEMENINO"]:
        raise HTTPException(
            status_code=400,
            detail="Sexo debe ser MASCULINO o FEMENINO"
        )
    
    regimen_acceso = regimen_acceso.upper()
    sexo = sexo.upper()
    
    try:
        # PASO 1: Extraer bases del PDF
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = Path(temp_file.name)
        
        try:
            # Extraer bases usando el servicio
            extractor = ExtractorBasesCotizacion(temp_file_path)
            resultado_extraccion = extractor.run()
            
            if not resultado_extraccion.bases:
                raise HTTPException(
                    status_code=400,
                    detail="No se encontraron bases de cotización en el PDF"
                )
            
            # Preparar metadatos de extracción
            metadata_extraccion = {
                "filename": file.filename,
                "file_size": len(content),
                "total_bases_extraidas": len(resultado_extraccion.bases),
                "total_empresas": len(set(base.empresa for base in resultado_extraccion.bases)),
                "periodo_extraido": {
                    "desde": min(base.mes_anyo for base in resultado_extraccion.bases),
                    "hasta": max(base.mes_anyo for base in resultado_extraccion.bases)
                }
            }
            
        finally:
            # Limpiar archivo temporal
            if temp_file_path.exists():
                temp_file_path.unlink()
        
        # PASO 2: Simular con las bases extraídas
        # Convertir bases a formato dict para el simulador
        bases_dict = [base.model_dump() for base in resultado_extraccion.bases]
        
        # Preparar datos para el simulador
        bases_data = {
            "bases": bases_dict
        }
        
        # Crear y ejecutar simulador
        simulador = SimuladorPeriodos(
            bases_extraidas=bases_data,
            fecha_jubilacion=fecha_jubilacion,
            regimen_acceso=regimen_acceso,
            sexo=sexo
        )
        
        # Procesar bases completas
        resultado_simulacion = simulador.procesar_bases_completo()
        
        # Crear response con estadísticas estructuradas
        estadisticas = EstadisticasResponse(**resultado_simulacion["estadisticas"])
        
        # Combinar resultados
        return SimulateResponse(
            success=True,
            message=f"PDF procesado exitosamente: {len(resultado_extraccion.bases)} bases extraídas y simulación completada",
            bases_procesadas=resultado_simulacion["bases_procesadas"],
            estadisticas=estadisticas,
            calculo_elegido=resultado_simulacion["calculo_elegido"],
            comparativa_calculos=resultado_simulacion["comparativa_calculos"],
            parametros_computo=resultado_simulacion["parametros_computo"],
            fecha_jubilacion=resultado_simulacion["fecha_jubilacion"],
            regimen_acceso=resultado_simulacion["regimen_acceso"],
            sexo=sexo,
            # Añadir metadatos de extracción como campo extra
            metadata_extraccion=metadata_extraccion
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BasesParserError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post(
    "/simulate", 
    response_model=SimulateResponse,
    summary="🧮 Calcular base reguladora completa",
    description="""
    Calcula la base reguladora de pensión con simulación completa de períodos.
    
    ### 🎯 Que hace este endpoint:
    * **Simula períodos futuros** hasta la fecha de jubilación
    * **Aplica revalorización** según normativa vigente 2025
    * **Maneja lagunas** de cotización automáticamente
    * **Calcula base reguladora** final para la pensión
    
    ### 📊 Proceso de cálculo:
    1. **Validación** de datos de entrada
    2. **Simulación** de períodos futuros si es necesario
    3. **Revalorización** de bases según fecha
    4. **Cálculo** de base reguladora final
    
    ### ⚙️ Parámetros considerados:
    * Número de bases a incluir según año de jubilación
    * Índices de revalorización aplicables
    * Divisor para calcular base reguladora
    * Régimen de cotización (General/Autónomo)
    
    ### 📈 Resultado detallado:
    Devuelve base reguladora, estadísticas completas y todas las bases procesadas.
    """,
    responses={
        200: {
            "description": "Simulación completada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Simulación completada exitosamente",
                        "calculo_elegido": "reforma_rd2_2023",
                        "estadisticas": {
                            "total_bases": 300,
                            "bases_revalorizadas": 276,
                            "bases_no_revalorizadas": 24,
                            "suma_periodo_revalorizado": 650000.00,
                            "suma_periodo_no_revalorizado": 60000.00,
                            "suma_total": 710000.00,
                            "base_reguladora": 2028.57
                        },
                        "comparativa_calculos": {
                            "calculo_reforma_rd2_2023": {
                                "parametros": {"bases_incluidas": 300, "divisor": 350},
                                "estadisticas": {"base_reguladora": 2028.57}
                            },
                            "calculo_prereforma": {
                                "parametros": {"bases_incluidas": 300, "divisor": 350},
                                "estadisticas": {"base_reguladora": 2020.45}
                            }
                        },
                        "fecha_jubilacion": "06/2025",
                        "regimen_acceso": "GENERAL"
                    }
                }
            }
        },
        400: {"description": "Error en los datos de entrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def simulate_bases(request: SimulateRequest):
    """
    Simula períodos y calcula la base reguladora de pensión.
    
    Args:
        request: Datos para la simulación (bases, fecha jubilación, régimen)
        
    Returns:
        SimulateResponse: Resultado de la simulación con base reguladora
        
    Raises:
        HTTPException: Si hay errores en el procesamiento
    """
    try:
        # Validar que hay bases para procesar
        if not request.bases_extraidas:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron bases para procesar"
            )
        
        # Preparar datos para el simulador
        bases_data = {
            "bases": request.bases_extraidas
        }
        
        # Crear y ejecutar simulador
        simulador = SimuladorPeriodos(
            bases_extraidas=bases_data,
            fecha_jubilacion=request.fecha_jubilacion,
            regimen_acceso=request.regimen_acceso,
            sexo=request.sexo
        )
        
        # Procesar bases completas
        resultado = simulador.procesar_bases_completo()
        
        # Crear response con estadísticas estructuradas
        estadisticas = EstadisticasResponse(**resultado["estadisticas"])
        
        return SimulateResponse(
            success=True,
            message="Simulación completada exitosamente",
            bases_procesadas=resultado["bases_procesadas"],
            estadisticas=estadisticas,
            calculo_elegido=resultado["calculo_elegido"],
            comparativa_calculos=resultado["comparativa_calculos"],
            parametros_computo=resultado["parametros_computo"],
            fecha_jubilacion=resultado["fecha_jubilacion"],
            regimen_acceso=resultado["regimen_acceso"],
            sexo=request.sexo
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BasesParserError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")



@router.get("/simulate/health")
async def simulate_health():
    """Endpoint de salud para el servicio de simulación."""
    return {"status": "healthy", "service": "simulation"}


@router.get(
    "/simulate/config",
    summary="⚙️ Configuración de simulación",
    description="""
    Obtiene toda la configuración disponible para realizar simulaciones.
    
    ### 📋 Configuración incluida:
    * **Índices de revalorización** por año
    * **Bases mínimas** de cotización
    * **Parámetros de cómputo** anual
    * **Regímenes** soportados
    
    ### 🔧 Utilidad:
    * Validar parámetros antes de simular
    * Mostrar opciones disponibles en interfaces
    * Verificar actualizaciones de normativa
    
    ### 📊 Datos actualizados:
    La configuración se carga desde archivos YAML actualizados con la normativa vigente.
    """,
    responses={
        200: {
            "description": "Configuración obtenida correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "indices_revalorizacion": {
                            "2023": 1.035,
                            "2024": 1.027,
                            "2025": 1.025
                        },
                        "bases_minimas": {
                            "GENERAL": {
                                "2024": 1080.00,
                                "2025": 1134.00
                            }
                        },
                        "parametros_computo": {
                            "2025": {
                                "numero_bases": 300,
                                "divisor": 350
                            }
                        },
                        "regimenes_soportados": ["GENERAL", "AUTONOMO"]
                    }
                }
            }
        },
        503: {"description": "Error al cargar configuración"}
    }
)
async def get_simulation_config():
    """
    Obtiene la configuración disponible para simulaciones.
    
    Returns:
        dict: Configuración de parámetros de simulación
    """
    try:
        from core.config.config_manager import config
        
        # Cargar configuraciones
        parametros = config.cargar_parametros_computo()
        indices = config.cargar_indices_revalorizacion()
        topes_cotizacion = config.cargar_topes_cotizacion()
        
        # Extraer bases mínimas de topes de cotización
        bases_minimas = {año: datos["base_minima_mensual"] for año, datos in topes_cotizacion.items()}
        
        # Obtener años disponibles
        años_parametros = sorted(parametros.keys())
        años_indices = sorted([int(fecha.split('/')[1]) for fecha in indices.keys()])
        años_bases_minimas = sorted(bases_minimas.keys())
        
        return {
            "parametros_computo": {
                "años_disponibles": años_parametros,
                "año_minimo": min(años_parametros),
                "año_maximo": max(años_parametros)
            },
            "indices_revalorizacion": {
                "total_indices": len(indices),
                "años_disponibles": list(set(años_indices)),
                "periodo_cobertura": {
                    "desde": min(años_indices) if años_indices else None,
                    "hasta": max(años_indices) if años_indices else None
                }
            },
            "bases_minimas": {
                "años_disponibles": años_bases_minimas,
                "año_minimo": min(años_bases_minimas) if años_bases_minimas else None,
                "año_maximo": max(años_bases_minimas) if años_bases_minimas else None
            },
            "regimenes_soportados": ["GENERAL", "AUTONOMO"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo configuración: {str(e)}")
