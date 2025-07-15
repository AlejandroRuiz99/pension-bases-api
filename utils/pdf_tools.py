from pathlib import Path
from typing import Union

import pdfplumber

from core.config.errors import (
    ERROR_ARCHIVO_NO_ENCONTRADO,
    ERROR_ARCHIVO_NO_PDF,
    ERROR_PDF_SIN_TEXTO,
    ERROR_PROCESANDO_PDF,
)


def validar_pdf(file_path: Union[str, Path]) -> Path:
    """Valida que el archivo exista y sea un PDF."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(ERROR_ARCHIVO_NO_ENCONTRADO.format(file_path))

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(ERROR_ARCHIVO_NO_PDF)

    return file_path


def cargar_pdf(file_path: Path) -> str:
    """Carga un archivo PDF y extrae su texto."""
    try:
        with pdfplumber.open(file_path) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() or ""

        if not texto:
            raise ValueError(ERROR_PDF_SIN_TEXTO)

        return texto
    except Exception as e:
        raise ValueError(ERROR_PROCESANDO_PDF.format(str(e)))
