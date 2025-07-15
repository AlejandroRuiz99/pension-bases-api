from typing import Dict

from pydantic import BaseModel


class ParametrosComputo(BaseModel):
    """Parámetros de cómputo para un año específico"""
    bases_incluidas: int
    periodo_meses: int
    divisor_base_reguladora: float


class ConfiguracionCompleta(BaseModel):
    """Configuración completa del sistema"""
    indices_revalorizacion: Dict[str, float]
    bases_minimas: Dict[int, float]
    parametros_computo: Dict[int, ParametrosComputo]
