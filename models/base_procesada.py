"""
Modelo para representar una base de cotización procesada en la simulación.
Hereda de BaseCotizacion y añade información adicional del procesamiento.
"""

from typing import Optional
from pydantic import BaseModel

from models.bases_cotizacion import BaseCotizacion


class BaseProcesada(BaseCotizacion):
    """
    Base de cotización procesada con información adicional de período y revalorización.
    Hereda de BaseCotizacion y añade campos específicos del procesamiento.
    """
    
    periodo: str  # "revalorizado" o "no_revalorizado"
    base_original: Optional[float] = None  # Solo para bases revalorizadas
    indice_revalorizacion: Optional[float] = None  # Solo para bases revalorizadas 