"""
Modelo para representar las bases de cotización.
Estructura simplificada y eficiente.
"""

import json
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from core.config.constants import FORMATO_FECHA


def serialize_date(obj):
    """Serializa objetos date y datetime para JSON"""
    if isinstance(obj, (datetime, date)):
        return obj.strftime(FORMATO_FECHA)
    raise TypeError(f"Type {type(obj)} not serializable")


class BaseCotizacion(BaseModel):
    """Representa una base de cotización individual."""
    
    mes_anyo: str
    base: float
    empresa: str
    regimen: str
    metadatos_pluriactividad: Optional[Dict[str, Any]] = None

    @field_validator("base", mode="before")
    @classmethod
    def convertir_base_a_float(cls, v):
        """Convierte el valor de base a flotante"""
        if v is None:
            return 0.0
        return round(float(v), 2)

    def to_json(self) -> str:
        """Serialización JSON personalizada"""
        return json.dumps(self.model_dump(), default=serialize_date, ensure_ascii=False)


class BasesCotizacion(BaseModel):
    """Contenedor para todas las bases de cotización."""
    
    bases: List[BaseCotizacion] = Field(default_factory=list)

    def agregar_base(self, base: BaseCotizacion):
        """Añade una base de cotización a la lista"""
        self.bases.append(base)

    def to_json(self) -> str:
        """Serialización JSON personalizada"""
        return json.dumps(self.model_dump(), default=serialize_date, ensure_ascii=False)

    class Config:
        """Configuración del modelo"""
        validate_assignment = True
