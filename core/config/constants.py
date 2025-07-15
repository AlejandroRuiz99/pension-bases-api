"""
Constantes para el extractor de bases de cotización.
Centraliza toda la configuración del sistema.
"""

## CONSTANTES BASES DE COTIZACIÓN ##

# === CONSTANTES DE RÉGIMEN ===
REGIMEN_GENERAL = "GENERAL"
REGIMEN_AUTONOMOS = "AUTONOMO"

# === TEXTOS DE BÚSQUEDA EN PDF ===
TEXTO_REGIMEN = "Régimen:"
TEXTO_EMPRESA_RAZON_SOCIAL = "Empresa/Razón"  # Flexible para espacios variables
TEXTO_CCC = "CCC:"
TEXTO_AUTONOMOS = "AUTÓNOMOS"

# === VALORES ESPECIALES DE BASES ===
BASE_NO_DISPONIBLE = "---"
BASE_PENDIENTE = "Pendiente"

# === PATRONES REGEX ===
PATRON_LINEA_ANUAL = r"^\d{4}"
PATRON_EMPRESA_REGEX = r"Empresa/Razón\s+Social:\s*(.+?)\s+CCC:"

# === CLAVES DE DICCIONARIO ===
CLAVE_REGIMEN = "regimen"
CLAVE_EMPRESA = "empresa"

# === FORMATOS ===
FORMATO_MES_AÑO = "{:02d}/{}"
FORMATO_FECHA = "%d/%m/%Y"



# === CONFIGURACIÓN DE ARCHIVO ===
ARCHIVO_SALIDA_DEFAULT = "bases_extraidas.json"
ENCODING_DEFAULT = "utf-8"

# === VALORES POR DEFECTO ===
EMPRESA_NO_IDENTIFICADA = "Empresa no identificada"
EMPRESA_AUTONOMO = "AUTÓNOMO"
