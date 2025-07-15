"""
Rutas y directorios del proyecto.
Gestiona todas las rutas principales del sistema.
"""

from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent.parent

# Directorios principales
CONFIG_DIR = BASE_DIR / "core" / "config"
TESTS_DIR = BASE_DIR / "tests"
UTILS_DIR = BASE_DIR / "utils"
MODELS_DIR = BASE_DIR / "models"
SERVICES_DIR = BASE_DIR / "services"
API_DIR = BASE_DIR / "api"
RESULTADOS_DIR = BASE_DIR / "resultados"

# Archivos de configuración YAML
CONFIG_FILES_DIR = CONFIG_DIR / "config_files"
PARAMETROS_COMPUTO_FILE = CONFIG_FILES_DIR / "parametros_computo_anual.yaml"
INDICES_REVALORIZACION_FILE = CONFIG_FILES_DIR / "indices_revalorizacion.yaml"
TOPES_COTIZACION_FILE = CONFIG_FILES_DIR / "topes_cotizacion.yaml"

# Directorios de pruebas
BASES_DATA_DIR = TESTS_DIR / "bases_data"
TEMPLATES_DIR = TESTS_DIR / "templates"

# Asegurar que los directorios existen
CONFIG_FILES_DIR.mkdir(parents=True, exist_ok=True)
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
