import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator

# Importar constantes
from core.config.constants import *

# Importar mensajes de error
from core.config.errors import *

# Importar modelos
from models.bases_cotizacion import BaseCotizacion, BasesCotizacion

# Importar herramientas PDF
from utils.pdf_tools import cargar_pdf


class ExtractorBases:
    """Clase responsable de extraer las bases de cotización del texto del PDF."""

    @staticmethod
    def extraer_bases_cotizacion(texto_pdf: str) -> List[BaseCotizacion]:
        """Extrae las bases de cotización del texto del PDF."""
        if not texto_pdf:
            return []

        bases = []
        lineas = texto_pdf.split("\n")
        contexto = {CLAVE_REGIMEN: None, CLAVE_EMPRESA: None}

        for linea in lineas:
            if TEXTO_REGIMEN in linea:
                ExtractorBases._actualizar_contexto(linea, contexto)
            elif (
                re.match(PATRON_LINEA_ANUAL, linea)
                and contexto[CLAVE_REGIMEN]
            ):
                bases.extend(ExtractorBases._procesar_linea_bases(linea, contexto))

        return bases

    @staticmethod
    def _actualizar_contexto(linea: str, contexto: dict):
        """Actualiza el contexto (régimen y empresa) basado en la línea actual."""
        if REGIMEN_GENERAL in linea:
            contexto[CLAVE_REGIMEN] = REGIMEN_GENERAL
            # Extraer empresa de forma robusta
            try:
                if TEXTO_EMPRESA_RAZON_SOCIAL in linea:
                    # Usar regex para manejar espacios variables
                    match = re.search(PATRON_EMPRESA_REGEX, linea)
                    if match:
                        nombre_empresa = match.group(1).strip()
                        contexto[CLAVE_EMPRESA] = nombre_empresa
                    else:
                        # Fallback: dividir por "Empresa/Razón" y buscar hasta "CCC:"
                        partes = linea.split(TEXTO_EMPRESA_RAZON_SOCIAL)
                        if len(partes) > 1:
                            empresa_parte = partes[1].strip()
                            if TEXTO_CCC in empresa_parte:
                                # Extraer solo el nombre de la empresa antes de "CCC:"
                                nombre_empresa = empresa_parte.split(TEXTO_CCC)[0].strip()
                                # Limpiar "Social:" si está presente
                                nombre_empresa = nombre_empresa.replace("Social:", "").strip()
                                contexto[CLAVE_EMPRESA] = nombre_empresa
                            else:
                                # Limpiar "Social:" si está presente
                                empresa_limpia = empresa_parte.replace("Social:", "").strip()
                                contexto[CLAVE_EMPRESA] = empresa_limpia
                        else:
                            contexto[CLAVE_EMPRESA] = EMPRESA_NO_IDENTIFICADA
                else:
                    contexto[CLAVE_EMPRESA] = EMPRESA_NO_IDENTIFICADA
            except Exception as e:
                contexto[CLAVE_EMPRESA] = EMPRESA_NO_IDENTIFICADA
        elif TEXTO_AUTONOMOS in linea:
            contexto[CLAVE_REGIMEN] = REGIMEN_AUTONOMOS
            contexto[CLAVE_EMPRESA] = EMPRESA_AUTONOMO

    @staticmethod
    def _procesar_linea_bases(linea: str, contexto: dict) -> List[BaseCotizacion]:
        """Procesa una línea de bases de cotización y retorna objetos BaseCotizacion."""
        bases = []
        try:
            partes = linea.split()
            anho = int(partes[0])
            valores_meses = partes[1:13]  # Tomar solo los 12 meses

            for mes, base_str in enumerate(valores_meses, 1):
                base_val = ExtractorBases._convertir_base(base_str)
                if base_val is not None:
                    bases.append(
                        BaseCotizacion(
                            mes_anyo=FORMATO_MES_AÑO.format(mes, anho),
                            base=base_val,
                            empresa=contexto[CLAVE_EMPRESA],
                            regimen=contexto[CLAVE_REGIMEN],
                        )
                    )

        except Exception as e:
            print(ERROR_PROCESAMIENTO_BASES.format(str(e)))

        return bases

    @staticmethod
    def _convertir_base(base_str: str) -> Optional[float]:
        """Convierte un string de base a float o None si no es válido."""
        if base_str in [BASE_NO_DISPONIBLE, BASE_PENDIENTE]:
            return None
        try:
            return float(base_str.replace(".", "").replace(",", "."))
        except ValueError:
            return None


@dataclass
class ExtractorBasesCotizacion:
    """Clase principal para extraer bases de cotización de un PDF."""

    file_path: Path

    def __post_init__(self):
        self.file_path = (
            Path(self.file_path)
            if not isinstance(self.file_path, Path)
            else self.file_path
        )
        if not self.file_path.exists():
            raise ValueError(ERROR_ARCHIVO_NO_EXISTE.format(self.file_path))

        self.texto_pdf = ""
        self.bases_extraidas = []
        self.extractor_bases = ExtractorBases()

    def run(self) -> BasesCotizacion:
        """Ejecuta el proceso de extracción de bases de cotización."""
        try:
            self.texto_pdf = cargar_pdf(self.file_path)
            self.bases_extraidas = self.extractor_bases.extraer_bases_cotizacion(
                self.texto_pdf
            )

            # Ordenar las bases por fecha (formato: "MM/YYYY")
            self.bases_extraidas.sort(
                key=lambda x: (
                    int(x.mes_anyo.split("/")[1]),
                    int(x.mes_anyo.split("/")[0]),
                )
            )
            resultado = BasesCotizacion()

            for base in self.bases_extraidas:
                resultado.agregar_base(base)

            return resultado

        except Exception as e:
            raise Exception(ERROR_PROCESAMIENTO_BASES_COTIZACION.format(str(e)))



