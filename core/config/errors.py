"""
Mensajes de error para el extractor de bases de cotización.
Centraliza todos los mensajes de error del sistema.
"""


class BasesParserError(Exception):
    """Excepción personalizada para errores del parser de bases."""
    pass


# === ERRORES DE ARCHIVO ===
ERROR_ARCHIVO_NO_EXISTE = "El archivo no existe: {0}"
ERROR_ARCHIVO_NO_ENCONTRADO = "El archivo no fue encontrado: {0}"
ERROR_ARCHIVO_NO_PDF = "El archivo debe ser un PDF"

# === ERRORES DE PDF ===
ERROR_LECTURA_PDF = "Error al leer el PDF: {0}"
ERROR_PDF_SIN_TEXTO = "El PDF no contiene texto extraíble"
ERROR_PROCESANDO_PDF = "Error al procesar el PDF: {0}"

# === ERRORES DE PROCESAMIENTO ===
ERROR_PROCESAMIENTO_BASES_COTIZACION = "Error al procesar las bases de cotización: {0}"
ERROR_PROCESAMIENTO_BASES = "Error al procesar las bases: {0}" 