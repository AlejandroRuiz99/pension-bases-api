"""
Modelos Pydantic para requests y responses de la API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from fastapi import UploadFile

from models.bases_cotizacion import BaseCotizacion
from models.base_procesada import BaseProcesada


class ExtractRequest(BaseModel):
    """Request para extraer bases de cotización de un PDF."""
    # El archivo PDF se manejará como UploadFile en el endpoint
    pass


class ExtractResponse(BaseModel):
    """Response con las bases extraídas del PDF."""
    success: bool
    message: str
    total_bases: int
    bases: List[BaseCotizacion]
    metadata: Optional[dict] = None


class SimulateRequest(BaseModel):
    """Request para simular y calcular base reguladora."""
    bases_extraidas: List[dict]  # Bases en formato dict para flexibilidad
    fecha_jubilacion: str = Field(..., description="Fecha de jubilación en formato MM/AAAA")
    regimen_acceso: str = Field(default="GENERAL", description="Régimen de acceso")
    sexo: str = Field(..., description="Sexo del cotizante (MASCULINO o FEMENINO)")

    @field_validator("fecha_jubilacion")
    @classmethod
    def validar_fecha_jubilacion(cls, v):
        """Valida el formato de fecha de jubilación."""
        import re
        if not re.match(r'^\d{2}/\d{4}$', v):
            raise ValueError("Fecha debe estar en formato MM/AAAA")
        return v

    @field_validator("regimen_acceso")
    @classmethod
    def validar_regimen(cls, v):
        """Valida el régimen de acceso."""
        if v.upper() not in ["GENERAL", "AUTONOMO"]:
            raise ValueError("Régimen debe ser GENERAL o AUTONOMO")
        return v.upper()

    @field_validator("sexo")
    @classmethod
    def validar_sexo(cls, v):
        """Valida el sexo del cotizante."""
        if v.upper() not in ["MASCULINO", "FEMENINO"]:
            raise ValueError("Sexo debe ser MASCULINO o FEMENINO")
        return v.upper()


class EstadisticasResponse(BaseModel):
    """Estadísticas del resultado de simulación."""
    total_bases: int
    bases_revalorizadas: int
    bases_no_revalorizadas: int
    suma_periodo_revalorizado: float
    suma_periodo_no_revalorizado: float
    suma_total: float
    base_reguladora: float


class SimulateResponse(BaseModel):
    """Response con el resultado de la simulación."""
    success: bool
    message: str
    bases_procesadas: List[dict]  # Usando dict para mantener flexibilidad
    estadisticas: EstadisticasResponse
    calculo_elegido: str  # Indica qué cálculo fue elegido
    comparativa_calculos: dict  # Comparativa completa de ambos cálculos
    parametros_computo: dict
    fecha_jubilacion: str
    regimen_acceso: str
    sexo: str
    metadata_extraccion: Optional[dict] = None  # Solo para endpoint /process


class ErrorResponse(BaseModel):
    """Response estándar para errores."""
    success: bool = False
    error: str
    details: Optional[str] = None 