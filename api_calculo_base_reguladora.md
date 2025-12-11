# 📋 API de Cálculo de Base Reguladora - Documentación Completa de Integración

## 📖 Índice

1. [Información General](#información-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Endpoints de la API](#endpoints-de-la-api)
4. [Modelos de Datos](#modelos-de-datos)
5. [Servicios Internos](#servicios-internos)
6. [Sistema de Configuración](#sistema-de-configuración)
7. [Manejo de Errores](#manejo-de-errores)
8. [Ejemplos de Integración](#ejemplos-de-integración)
9. [Dependencias y Tecnologías](#dependencias-y-tecnologías)
10. [Variables de Entorno](#variables-de-entorno)
11. [Consideraciones de Seguridad](#consideraciones-de-seguridad)

---

## 🎯 Información General

### Descripción
API RESTful profesional para extraer bases de cotización de archivos PDF de la Seguridad Social española y calcular la base reguladora de pensiones según la normativa vigente 2025.

### Propósito
Esta API automatiza el proceso completo de:
- Extracción de bases de cotización desde PDFs oficiales
- Simulación de períodos futuros hasta la jubilación
- Cálculo de base reguladora conforme al Real Decreto 2/2023
- Revalorización dinámica con IPC según LGSS

### Características Principales
- ✅ **Extracción automática** de PDFs de la Seguridad Social
- ✅ **Doble cálculo**: Reforma RD 2/2023 vs Prereforma (elige el más favorable)
- ✅ **Revalorización dinámica** con IPC acumulado
- ✅ **Manejo de lagunas** diferenciado por sexo (DT 41ª LGSS)
- ✅ **Pluriactividad**: Agregación automática de múltiples regímenes
- ✅ **Múltiples regímenes**: General y Autónomo
- ✅ **Validación robusta** con Pydantic

### Información Técnica Base
- **Framework**: FastAPI 0.104.1
- **Versión API**: 1.0.0
- **Python**: 3.9+
- **Documentación interactiva**: Swagger UI en `/docs`
- **Puerto por defecto**: 8000
- **Base URL Desarrollo**: `http://localhost:8000`
- **Base URL Producción**: Variable según plataforma de despliegue

---

## 🏗️ Arquitectura del Sistema

### Estructura de Directorios

```
basesParser/
├── api/                          # Capa de endpoints HTTP
│   ├── endpoints/
│   │   ├── extract.py           # Endpoint de extracción de PDFs
│   │   ├── simulate.py          # Endpoints de simulación y proceso completo
│   │   └── config_info.py       # Endpoints de configuración
│   └── client.py
├── models/                       # Modelos de datos Pydantic
│   ├── api_models.py            # Modelos de Request/Response
│   ├── bases_cotizacion.py      # Modelo de bases individuales
│   ├── base_procesada.py        # Modelo de bases procesadas
│   └── configuraciones.py       # Modelos de configuración
├── services/                     # Lógica de negocio
│   ├── extractor.py             # Servicio de extracción de PDFs
│   └── simulator.py             # Servicio de simulación y cálculo
├── core/                         # Configuración y utilidades centrales
│   └── config/
│       ├── config_files/        # Archivos YAML de configuración
│       │   ├── ipc_anual.yaml
│       │   ├── parametros_computo_anual.yaml
│       │   └── topes_cotizacion.yaml
│       ├── config_manager.py    # Gestor de configuraciones
│       ├── constants.py         # Constantes del sistema
│       ├── errors.py            # Excepciones personalizadas
│       └── paths.py             # Rutas del sistema
├── utils/                        # Utilidades auxiliares
│   └── pdf_tools.py             # Herramientas para procesamiento PDF
├── app.py                        # Aplicación principal (desarrollo)
├── app_production.py            # Aplicación optimizada (producción)
└── requirements.txt             # Dependencias Python
```

### Patrón de Diseño

**Arquitectura en Capas:**

```
┌─────────────────────────────────────────┐
│   Capa HTTP (FastAPI Endpoints)        │
│   - Validación de entrada               │
│   - Serialización de respuesta          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   Capa de Servicios (Business Logic)   │
│   - ExtractorBasesCotizacion            │
│   - SimuladorPeriodos                   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   Capa de Datos (Models & Config)      │
│   - Modelos Pydantic                    │
│   - ConfigManager                       │
│   - YAML configurations                 │
└─────────────────────────────────────────┘
```

---

## 🚀 Endpoints de la API

### Endpoint 1: Raíz de la API

**GET /**

Página HTML de bienvenida con información de la API y enlaces a documentación.

**Respuesta**: HTML con interfaz visual de la API.

---

### Endpoint 2: Estado de Salud

**GET /health**

Verifica el estado de salud de la API y sus servicios.

**Respuesta Exitosa (200):**
```json
{
  "status": "healthy",
  "message": "API funcionando correctamente",
  "version": "1.0.0",
  "services": {
    "extraction": "✅ Operativo",
    "simulation": "✅ Operativo",
    "configuration": "✅ Operativo"
  },
  "endpoints": {
    "documentation": "/docs",
    "health": "/health",
    "extract": "/api/extract",
    "simulate": "/api/simulate",
    "config": "/api/simulate/config"
  }
}
```

**Respuesta Error (503):**
```json
{
  "detail": "Servicio no disponible: {error_message}"
}
```

---

### Endpoint 3: Información de la API

**GET /api/info**

Devuelve información detallada sobre las capacidades de la API.

**Respuesta (200):**
```json
{
  "api_name": "API Bases de Cotización",
  "version": "1.0.0",
  "description": "API para extraer bases de cotización y calcular base reguladora",
  "features": [
    "Extracción automática de PDFs",
    "Cálculo de base reguladora",
    "Simulación de períodos futuros",
    "Revalorización según normativa 2025",
    "Manejo de lagunas automático",
    "Múltiples regímenes (General, Autónomo)"
  ],
  "supported_formats": ["PDF"],
  "supported_regimes": ["GENERAL", "AUTONOMO"],
  "documentation": {
    "swagger": "/docs"
  }
}
```

---

### Endpoint 4: Extraer Bases de Cotización

**POST /api/extract**

Extrae automáticamente las bases de cotización de un archivo PDF.

**Content-Type**: `multipart/form-data`

**Parámetros:**
- `file` (File, required): Archivo PDF con bases de cotización
  - Formato: PDF
  - Tamaño máximo: 10MB
  - Extensión: `.pdf`

**Ejemplo de Request (Python):**
```python
import requests

url = "http://localhost:8000/api/extract"
files = {'file': open('bases_cotizacion.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Ejemplo de Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@bases_cotizacion.pdf"
```

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "message": "Se extrajeron 24 bases de cotización exitosamente",
  "total_bases": 24,
  "bases": [
    {
      "mes_anyo": "01/2023",
      "base": 2500.50,
      "empresa": "EMPRESA EJEMPLO SL",
      "regimen": "GENERAL"
    },
    {
      "mes_anyo": "02/2023",
      "base": 2550.75,
      "empresa": "EMPRESA EJEMPLO SL",
      "regimen": "GENERAL"
    }
  ],
  "metadata": {
    "filename": "bases_cotizacion.pdf",
    "file_size": 1024000,
    "total_empresas": 2,
    "periodo_bases": {
      "desde": "01/2022",
      "hasta": "12/2023"
    }
  }
}
```

**Respuestas de Error:**

- **400 Bad Request:**
  ```json
  {
    "detail": "El archivo debe ser un PDF"
  }
  ```

- **400 Bad Request (tamaño):**
  ```json
  {
    "detail": "El archivo es demasiado grande. Máximo 10MB"
  }
  ```

- **500 Internal Server Error:**
  ```json
  {
    "detail": "Error interno: {error_description}"
  }
  ```

---

### Endpoint 5: Simular y Calcular Base Reguladora

**POST /api/simulate**

Calcula la base reguladora de pensión con simulación completa de períodos.

**Content-Type**: `application/json`

**Parámetros del Body:**
```json
{
  "bases_extraidas": [
    {
      "mes_anyo": "01/2023",
      "base": 2500.50,
      "empresa": "EMPRESA EJEMPLO SL",
      "regimen": "GENERAL"
    }
  ],
  "fecha_jubilacion": "06/2025",
  "regimen_acceso": "GENERAL",
  "sexo": "MASCULINO"
}
```

**Campos:**
- `bases_extraidas` (List[Dict], required): Lista de bases de cotización extraídas
- `fecha_jubilacion` (String, required): Fecha de jubilación en formato `MM/YYYY`
- `regimen_acceso` (String, optional): "GENERAL" o "AUTONOMO" (default: "GENERAL")
- `sexo` (String, required): "MASCULINO" o "FEMENINO" (afecta cálculo de lagunas)

**Ejemplo de Request (Python):**
```python
import requests

url = "http://localhost:8000/api/simulate"
data = {
  "bases_extraidas": [
    {"mes_anyo": "01/2023", "base": 2500.50, "empresa": "EMPRESA SL", "regimen": "GENERAL"},
    {"mes_anyo": "02/2023", "base": 2550.75, "empresa": "EMPRESA SL", "regimen": "GENERAL"}
  ],
  "fecha_jubilacion": "06/2025",
  "regimen_acceso": "GENERAL",
  "sexo": "MASCULINO"
}
response = requests.post(url, json=data)
print(response.json())
```

**Respuesta Exitosa (200):**
```json
{
  "success": true,
  "message": "Simulación completada exitosamente",
  "calculo_elegido": "reforma_rd2_2023",
  "bases_procesadas": [
    {
      "mes_anyo": "05/2025",
      "base": 2650.25,
      "empresa": "EMPRESA SL",
      "regimen": "GENERAL",
      "periodo": "no_revalorizado"
    },
    {
      "mes_anyo": "04/2025",
      "base": 2638.00,
      "empresa": "EMPRESA SL",
      "regimen": "GENERAL",
      "periodo": "no_revalorizado"
    },
    {
      "mes_anyo": "12/2022",
      "base": 2850.45,
      "base_original": 2600.00,
      "indice_revalorizacion": 1.0963558,
      "metodo_revalorizacion": "IPC_ACUMULADO",
      "año_base": 2022,
      "empresa": "EMPRESA SL",
      "regimen": "GENERAL",
      "periodo": "revalorizado"
    }
  ],
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
      "parametros": {
        "bases_incluidas": 300,
        "divisor": 350,
        "periodo_meses": 300
      },
      "estadisticas": {
        "total_bases": 300,
        "base_reguladora": 2028.57,
        "suma_total": 710000.00
      }
    },
    "calculo_prereforma": {
      "parametros": {
        "bases_incluidas": 300,
        "divisor": 350,
        "periodo_meses": 300
      },
      "estadisticas": {
        "total_bases": 300,
        "base_reguladora": 2020.45,
        "suma_total": 707158.50
      }
    }
  },
  "parametros_computo": {
    "bases_incluidas": 300,
    "periodo_meses": 300,
    "divisor_base_reguladora": 350
  },
  "fecha_jubilacion": "06/2025",
  "regimen_acceso": "GENERAL",
  "sexo": "MASCULINO"
}
```

**Respuestas de Error:**

- **400 Bad Request:**
  ```json
  {
    "detail": "No se proporcionaron bases para procesar"
  }
  ```

- **400 Bad Request (validación):**
  ```json
  {
    "detail": "Fecha de jubilación debe estar en formato MM/YYYY"
  }
  ```

---

### Endpoint 6: Proceso Completo (PDF → Base Reguladora)

**POST /api/process**

Endpoint todo-en-uno que extrae bases de un PDF y calcula automáticamente la base reguladora.

**Content-Type**: `multipart/form-data`

**Parámetros:**
- `file` (File, required): Archivo PDF con bases de cotización
- `fecha_jubilacion` (String, required): Fecha de jubilación (MM/YYYY)
- `regimen_acceso` (String, optional): "GENERAL" o "AUTONOMO" (default: "GENERAL")
- `sexo` (String, required): "MASCULINO" o "FEMENINO"

**Ejemplo de Request (Python):**
```python
import requests

url = "http://localhost:8000/api/process"
files = {'file': open('bases_cotizacion.pdf', 'rb')}
data = {
  'fecha_jubilacion': '06/2025',
  'regimen_acceso': 'GENERAL',
  'sexo': 'MASCULINO'
}
response = requests.post(url, files=files, data=data)
print(response.json())
```

**Ejemplo de Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/process" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@bases_cotizacion.pdf" \
  -F "fecha_jubilacion=06/2025" \
  -F "regimen_acceso=GENERAL" \
  -F "sexo=MASCULINO"
```

**Respuesta Exitosa (200):**
Combina la estructura de `/api/simulate` con información adicional de extracción:

```json
{
  "success": true,
  "message": "PDF procesado exitosamente: 24 bases extraídas y simulación completada",
  "calculo_elegido": "reforma_rd2_2023",
  "bases_procesadas": [...],
  "estadisticas": {...},
  "comparativa_calculos": {...},
  "parametros_computo": {...},
  "fecha_jubilacion": "06/2025",
  "regimen_acceso": "GENERAL",
  "sexo": "MASCULINO",
  "metadata_extraccion": {
    "filename": "bases_cotizacion.pdf",
    "file_size": 1024000,
    "total_bases_extraidas": 24,
    "total_empresas": 2,
    "periodo_extraido": {
      "desde": "01/2023",
      "hasta": "12/2024"
    }
  }
}
```

**Respuestas de Error:**

- **400 Bad Request:**
  ```json
  {
    "detail": "No se encontraron bases de cotización en el PDF"
  }
  ```

---

### Endpoint 7: Obtener Configuración de Simulación

**GET /api/simulate/config**

Obtiene información sobre la configuración disponible para simulaciones.

**Respuesta (200):**
```json
{
  "parametros_computo": {
    "años_disponibles": [2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036],
    "año_minimo": 2025,
    "año_maximo": 2036
  },
  "indices_revalorizacion": {
    "total_indices": 26,
    "años_disponibles": [2000, 2001, 2002, 2023, 2024, 2025],
    "periodo_cobertura": {
      "desde": 2000,
      "hasta": 2025
    }
  },
  "bases_minimas": {
    "años_disponibles": [1997, 1998, 2023, 2024, 2025],
    "año_minimo": 1997,
    "año_maximo": 2025
  },
  "regimenes_soportados": ["GENERAL", "AUTONOMO"]
}
```

---

### Endpoint 8: Obtener Parámetros de Cómputo

**GET /api/config/parametros**

Obtiene todos los parámetros de cómputo anual.

**Respuesta (200):**
```json
{
  "success": true,
  "data": {
    "2025": {
      "bases_incluidas": 300,
      "periodo_meses": 300,
      "divisor_base_reguladora": 350
    },
    "2026": {
      "bases_incluidas": 302,
      "periodo_meses": 304,
      "divisor_base_reguladora": 352.33
    }
  },
  "total_años": 12,
  "años_disponibles": [2025, 2026, 2027, 2028],
  "descripcion": "Parámetros de cómputo anual para cálculo de bases de cotización"
}
```

---

### Endpoint 9: Obtener Índices de Revalorización

**GET /api/config/indices**

Obtiene los índices IPC para revalorización de bases.

**Respuesta (200):**
```json
{
  "success": true,
  "data": {
    "2000": 3.4,
    "2001": 3.6,
    "2022": 8.4,
    "2023": 3.5,
    "2024": 3.2,
    "2025": 2.8
  },
  "total_indices": 26,
  "rango_fechas": {
    "desde": "2000",
    "hasta": "2025"
  },
  "descripcion": "Índices de revalorización para actualizar bases históricas"
}
```

---

### Endpoint 10: Obtener Topes de Cotización

**GET /api/config/topes**

Obtiene los topes de cotización (bases mínimas y máximas) por año.

**Respuesta (200):**
```json
{
  "success": true,
  "data": {
    "2025": {
      "base_minima_mensual": 1323.0,
      "base_maxima_mensual": 4720.50
    },
    "2024": {
      "base_minima_mensual": 1323.0,
      "base_maxima_mensual": 4720.50
    }
  },
  "total_años": 29,
  "años_disponibles": [1997, 1998, 2023, 2024, 2025],
  "descripcion": "Topes de cotización (bases mínimas y máximas) por año"
}
```

---

### Endpoint 11: Obtener Toda la Configuración

**GET /api/config/all**

Obtiene toda la configuración del sistema en un solo endpoint.

**Respuesta (200):**
```json
{
  "success": true,
  "configuracion": {
    "parametros_computo": {
      "data": {...},
      "total_años": 12,
      "años_disponibles": [2025, 2026, 2027]
    },
    "indices_revalorizacion": {
      "data": {...},
      "total_indices": 26,
      "rango_fechas": {
        "desde": "2000",
        "hasta": "2025"
      }
    },
    "topes_cotizacion": {
      "data": {...},
      "total_años": 29,
      "años_disponibles": [1997, 2025]
    }
  },
  "resumen": {
    "total_parametros": 12,
    "total_indices": 26,
    "total_topes": 29,
    "configuracion_cargada": true
  },
  "descripcion": "Configuración completa del sistema de cálculo de bases de cotización"
}
```

---

## 📊 Modelos de Datos

### BaseCotizacion (Modelo Base)

Representa una base de cotización individual.

```python
{
  "mes_anyo": str,              # Formato: "MM/YYYY" (ej: "01/2023")
  "base": float,                # Base de cotización en euros (ej: 2500.50)
  "empresa": str,               # Nombre de la empresa o "AUTONOMO"
  "regimen": str,               # "GENERAL" o "AUTONOMO"
  "metadatos_pluriactividad": Optional[Dict]  # Solo si es pluriactividad
}
```

**Ejemplo:**
```json
{
  "mes_anyo": "01/2023",
  "base": 2500.50,
  "empresa": "EMPRESA EJEMPLO SL",
  "regimen": "GENERAL"
}
```

**Ejemplo con Pluriactividad:**
```json
{
  "mes_anyo": "01/2023",
  "base": 4200.00,
  "empresa": "PLURIACTIVIDAD_2_EMPRESAS",
  "regimen": "GENERAL",
  "metadatos_pluriactividad": {
    "es_pluriactividad": true,
    "bases_individuales": [
      {"mes_anyo": "01/2023", "base": 2500.00, "empresa": "EMPRESA A", "regimen": "GENERAL"},
      {"mes_anyo": "01/2023", "base": 1700.00, "empresa": "AUTONOMO", "regimen": "AUTONOMO"}
    ],
    "base_bruta": 4200.00,
    "tope_aplicado": "ninguno",
    "empresas_detalle": ["EMPRESA A", "AUTONOMO"]
  }
}
```

---

### BaseProcesada (Modelo de Base Procesada)

Base de cotización procesada con información de revalorización.

```python
{
  "mes_anyo": str,
  "base": float,                      # Base revalorizada
  "empresa": str,
  "regimen": str,
  "periodo": str,                     # "revalorizado" o "no_revalorizado"
  "base_original": Optional[float],   # Solo si está revalorizada
  "indice_revalorizacion": Optional[float],  # Solo si está revalorizada
  "metodo_revalorizacion": Optional[str],    # Solo si está revalorizada
  "año_base": Optional[int]           # Solo si está revalorizada
}
```

**Ejemplo (Base Revalorizada):**
```json
{
  "mes_anyo": "12/2022",
  "base": 2850.45,
  "base_original": 2600.00,
  "indice_revalorizacion": 1.0963558,
  "metodo_revalorizacion": "IPC_ACUMULADO",
  "año_base": 2022,
  "empresa": "EMPRESA SL",
  "regimen": "GENERAL",
  "periodo": "revalorizado"
}
```

**Ejemplo (Base No Revalorizada):**
```json
{
  "mes_anyo": "05/2025",
  "base": 2650.25,
  "empresa": "EMPRESA SL",
  "regimen": "GENERAL",
  "periodo": "no_revalorizado"
}
```

---

### ExtractRequest

No requiere body JSON. Solo archivo multipart/form-data.

---

### ExtractResponse

```python
{
  "success": bool,
  "message": str,
  "total_bases": int,
  "bases": List[BaseCotizacion],
  "metadata": {
    "filename": str,
    "file_size": int,
    "total_empresas": int,
    "periodo_bases": {
      "desde": str,
      "hasta": str
    }
  }
}
```

---

### SimulateRequest

```python
{
  "bases_extraidas": List[Dict],
  "fecha_jubilacion": str,      # Formato: "MM/YYYY"
  "regimen_acceso": str,        # "GENERAL" o "AUTONOMO"
  "sexo": str                   # "MASCULINO" o "FEMENINO"
}
```

**Validaciones:**
- `fecha_jubilacion`: Debe tener formato `MM/YYYY`
- `regimen_acceso`: Solo acepta "GENERAL" o "AUTONOMO"
- `sexo`: Solo acepta "MASCULINO" o "FEMENINO"

---

### EstadisticasResponse

```python
{
  "total_bases": int,
  "bases_revalorizadas": int,
  "bases_no_revalorizadas": int,
  "suma_periodo_revalorizado": float,
  "suma_periodo_no_revalorizado": float,
  "suma_total": float,
  "base_reguladora": float
}
```

---

### SimulateResponse

```python
{
  "success": bool,
  "message": str,
  "bases_procesadas": List[Dict],
  "estadisticas": EstadisticasResponse,
  "calculo_elegido": str,        # "reforma_rd2_2023" o "prereforma"
  "comparativa_calculos": {
    "calculo_reforma_rd2_2023": {
      "parametros": Dict,
      "estadisticas": Dict
    },
    "calculo_prereforma": {
      "parametros": Dict,
      "estadisticas": Dict
    }
  },
  "parametros_computo": Dict,
  "fecha_jubilacion": str,
  "regimen_acceso": str,
  "sexo": str,
  "metadata_extraccion": Optional[Dict]  # Solo en /api/process
}
```

---

### ErrorResponse

```python
{
  "success": bool,              # Siempre false
  "error": str,
  "details": Optional[str]
}
```

---

## 🔧 Servicios Internos

### ExtractorBasesCotizacion

**Ubicación**: `services/extractor.py`

**Propósito**: Extraer bases de cotización de archivos PDF.

**Clase Principal**: `ExtractorBasesCotizacion`

**Constructor:**
```python
ExtractorBasesCotizacion(file_path: Path)
```

**Método Principal:**
```python
def run(self) -> BasesCotizacion:
    """
    Ejecuta el proceso de extracción de bases de cotización.
    
    Returns:
        BasesCotizacion: Objeto con todas las bases extraídas
        
    Raises:
        Exception: Si hay errores en el procesamiento
    """
```

**Proceso Interno:**
1. Carga el texto del PDF usando `pdfplumber`
2. Identifica regímenes (GENERAL/AUTONOMO)
3. Extrae nombres de empresas
4. Parsea líneas anuales con 12 meses de bases
5. Valida y estructura datos en objetos `BaseCotizacion`
6. Ordena bases cronológicamente

**Patrones de Extracción:**
- Detecta líneas con `Régimen: GENERAL` o `AUTÓNOMOS`
- Extrae empresa desde patrón: `Empresa/Razón Social: {nombre} CCC:`
- Parsea líneas anuales con formato: `YYYY valor1 valor2 ... valor12`
- Maneja valores especiales: `---` (no disponible), `Pendiente`

---

### SimuladorPeriodos

**Ubicación**: `services/simulator.py`

**Propósito**: Simular períodos futuros y calcular base reguladora.

**Clase Principal**: `SimuladorPeriodos`

**Constructor:**
```python
SimuladorPeriodos(
    bases_extraidas: Dict,
    fecha_jubilacion: str,
    regimen_acceso: str = "GENERAL",
    sexo: str = "MASCULINO"
)
```

**Método Principal:**
```python
def procesar_bases_completo(self) -> Dict:
    """
    Ejecuta el proceso completo de simulación y procesamiento.
    Realiza doble cálculo: reforma RD 2/2023 vs prereforma.
    
    Returns:
        Dict: Resultado completo con bases procesadas y estadísticas
    """
```

**Funcionalidades Clave:**

1. **Simulación de Períodos Futuros:**
   - Calcula promedio de últimos 6 meses
   - Simula bases hasta 1 mes antes de jubilación
   - Marca bases simuladas con empresa="SIMULADA"

2. **Manejo de Lagunas:**
   - Diferenciado por sexo según DT 41ª LGSS
   - **Régimen General:**
     - Primeros 48 meses: 100% base mínima
     - Meses 49-60 (mujeres): 100% base mínima
     - Meses 61-84 (mujeres): 80% base mínima
     - Resto (mujeres): 50% base mínima
     - Hombres después mes 48: 50% base mínima
   - **Régimen Autónomo:** Base 0 en lagunas

3. **Pluriactividad:**
   - Suma automática de bases del mismo mes
   - Aplica topes mínimos y máximos
   - Mantiene metadatos de bases individuales

4. **Revalorización con IPC:**
   - Cálculo dinámico mes a mes
   - Usa IPC acumulado desde año de cotización
   - No revaloriza últimos 24 meses
   - Proyección automática para años futuros

5. **Doble Cálculo:**
   - **Reforma RD 2/2023**: Parámetros actuales (300 bases / 350 divisor)
   - **Prereforma**: Parámetros antiguos (300 bases / 350 divisor)
   - Elige automáticamente el más favorable

**Métodos Importantes:**

```python
def simular_periodo_futuro(self) -> List[BaseCotizacion]:
    """Simula bases futuras si faltan hasta la jubilación."""

def calcular_base_laguna(self, fecha_laguna: str, n_laguna: int) -> float:
    """Imputa base para laguna según normativa LGSS art. 209.1 y DT 41ª."""

def obtener_bases_periodo_computo(self, usar_parametros_antiguos: bool = False) -> List[BaseCotizacion]:
    """Obtiene bases del período de cómputo, incluyendo lagunas."""

def revalorizar_bases(self, bases_con_periodo: List[Dict]) -> List[Dict]:
    """Revaloriza bases aplicando IPC acumulado."""
```

---

## ⚙️ Sistema de Configuración

### ConfigManager

**Ubicación**: `core/config/config_manager.py`

**Propósito**: Gestión centralizada de configuraciones desde archivos YAML.

**Instancia Global:**
```python
from core.config.config_manager import config
```

**Métodos Públicos:**

```python
# Cargar parámetros de cómputo
parametros = config.cargar_parametros_computo()
# Retorna: Dict[int, Dict] - Parámetros por año

# Cargar topes de cotización
topes = config.cargar_topes_cotizacion()
# Retorna: Dict[int, Dict] - Topes por año

# Cargar IPC anual
ipc = config.cargar_ipc_anual()
# Retorna: Dict[int, float] - IPC por año

# Recargar configuraciones
config.reload()
```

**Archivos de Configuración:**

#### 1. parametros_computo_anual.yaml

Estructura:
```yaml
parametros_computo_anual:
  2025:
    bases_incluidas: 300
    periodo_meses: 300
    divisor_base_reguladora: 350
  2026:
    bases_incluidas: 302
    periodo_meses: 304
    divisor_base_reguladora: 352.33
```

#### 2. topes_cotizacion.yaml

Estructura:
```yaml
topes_cotizacion:
  2025:
    base_minima_mensual: 1323.0
    base_maxima_mensual: 4720.50
  2024:
    base_minima_mensual: 1323.0
    base_maxima_mensual: 4720.50
```

#### 3. ipc_anual.yaml

Estructura:
```yaml
ipc_anual:
  2000: 3.4
  2001: 3.6
  2022: 8.4
  2023: 3.5
  2024: 3.2
  2025: 2.8
```

**Caché de Configuraciones:**

El `ConfigManager` carga todas las configuraciones al inicializar y las mantiene en caché. Esto mejora el rendimiento evitando lecturas repetidas de archivos YAML.

---

### Constantes del Sistema

**Ubicación**: `core/config/constants.py`

**Constantes Principales:**

```python
# Regímenes
REGIMEN_GENERAL = "GENERAL"
REGIMEN_AUTONOMOS = "AUTONOMO"

# Textos de búsqueda en PDF
TEXTO_REGIMEN = "Régimen:"
TEXTO_EMPRESA_RAZON_SOCIAL = "Empresa/Razón"
TEXTO_CCC = "CCC:"
TEXTO_AUTONOMOS = "AUTÓNOMOS"

# Valores especiales
BASE_NO_DISPONIBLE = "---"
BASE_PENDIENTE = "Pendiente"

# Patrones regex
PATRON_LINEA_ANUAL = r"^\d{4}"
PATRON_EMPRESA_REGEX = r"Empresa/Razón\s+Social:\s*(.+?)\s+CCC:"

# Formatos
FORMATO_MES_AÑO = "{:02d}/{}"
FORMATO_FECHA = "%d/%m/%Y"

# Valores por defecto
EMPRESA_NO_IDENTIFICADA = "Empresa no identificada"
EMPRESA_AUTONOMO = "AUTÓNOMO"
```

---

## 🚨 Manejo de Errores

### Excepciones Personalizadas

**BasesParserError**

Excepción base para errores del sistema.

```python
from core.config.errors import BasesParserError

raise BasesParserError("Mensaje de error personalizado")
```

### Mensajes de Error Estándar

```python
# Errores de archivo
ERROR_ARCHIVO_NO_EXISTE = "El archivo no existe: {0}"
ERROR_ARCHIVO_NO_PDF = "El archivo debe ser un PDF"

# Errores de PDF
ERROR_LECTURA_PDF = "Error al leer el PDF: {0}"
ERROR_PDF_SIN_TEXTO = "El PDF no contiene texto extraíble"

# Errores de procesamiento
ERROR_PROCESAMIENTO_BASES_COTIZACION = "Error al procesar las bases de cotización: {0}"
```

### Códigos de Estado HTTP

| Código | Descripción | Uso |
|--------|-------------|-----|
| 200 | OK | Operación exitosa |
| 400 | Bad Request | Error en datos de entrada, validación fallida |
| 500 | Internal Server Error | Error interno del servidor |
| 503 | Service Unavailable | Servicio no disponible (health check) |

### Manejo en Endpoints

Todos los endpoints implementan manejo de errores robusto:

```python
try:
    # Lógica del endpoint
    return resultado
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except BasesParserError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
```

**En Producción:**
- No se exponen detalles internos del error
- Se registran en logs para debugging
- Se devuelve mensaje genérico al cliente

---

## 💡 Ejemplos de Integración

### Ejemplo 1: Integración Frontend JavaScript

```javascript
// Proceso completo: Subir PDF y obtener base reguladora
async function calcularBaseReguladora(pdfFile, fechaJubilacion, regimen, sexo) {
  const formData = new FormData();
  formData.append('file', pdfFile);
  formData.append('fecha_jubilacion', fechaJubilacion);
  formData.append('regimen_acceso', regimen);
  formData.append('sexo', sexo);

  try {
    const response = await fetch('http://localhost:8000/api/process', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const resultado = await response.json();
    
    console.log('Base Reguladora:', resultado.estadisticas.base_reguladora);
    console.log('Cálculo Elegido:', resultado.calculo_elegido);
    console.log('Total Bases:', resultado.estadisticas.total_bases);
    
    return resultado;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
}

// Uso
const fileInput = document.getElementById('pdfInput');
calcularBaseReguladora(
  fileInput.files[0],
  '06/2025',
  'GENERAL',
  'MASCULINO'
);
```

---

### Ejemplo 2: Integración Python (Paso a Paso)

```python
import requests

API_URL = "http://localhost:8000"

def procesar_pension_completo(pdf_path, fecha_jubilacion, regimen='GENERAL', sexo='MASCULINO'):
    """
    Procesa un PDF completo y devuelve la base reguladora.
    """
    # Paso 1: Subir y procesar PDF
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {
            'fecha_jubilacion': fecha_jubilacion,
            'regimen_acceso': regimen,
            'sexo': sexo
        }
        
        response = requests.post(f"{API_URL}/api/process", files=files, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Error: {response.json()['detail']}")
    
    resultado = response.json()
    
    # Extraer información clave
    return {
        'base_reguladora': resultado['estadisticas']['base_reguladora'],
        'calculo_usado': resultado['calculo_elegido'],
        'total_bases': resultado['estadisticas']['total_bases'],
        'suma_total': resultado['estadisticas']['suma_total'],
        'bases_extraidas': resultado['metadata_extraccion']['total_bases_extraidas'],
        'periodo': resultado['metadata_extraccion']['periodo_extraido']
    }

# Uso
resultado = procesar_pension_completo(
    'bases_cotizacion.pdf',
    '06/2025',
    'GENERAL',
    'MASCULINO'
)

print(f"Base Reguladora: {resultado['base_reguladora']}€")
print(f"Método usado: {resultado['calculo_usado']}")
```

---

### Ejemplo 3: Integración con React

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function CalculadoraPension() {
  const [file, setFile] = useState(null);
  const [fechaJubilacion, setFechaJubilacion] = useState('');
  const [regimen, setRegimen] = useState('GENERAL');
  const [sexo, setSexo] = useState('MASCULINO');
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file || !fechaJubilacion) {
      setError('Por favor complete todos los campos');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('fecha_jubilacion', fechaJubilacion);
    formData.append('regimen_acceso', regimen);
    formData.append('sexo', sexo);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/process',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setResultado(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar el archivo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="calculadora-pension">
      <h2>Calculadora de Base Reguladora</h2>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>PDF de Bases de Cotización:</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        <div>
          <label>Fecha de Jubilación (MM/YYYY):</label>
          <input
            type="text"
            placeholder="06/2025"
            value={fechaJubilacion}
            onChange={(e) => setFechaJubilacion(e.target.value)}
          />
        </div>

        <div>
          <label>Régimen:</label>
          <select value={regimen} onChange={(e) => setRegimen(e.target.value)}>
            <option value="GENERAL">General</option>
            <option value="AUTONOMO">Autónomo</option>
          </select>
        </div>

        <div>
          <label>Sexo:</label>
          <select value={sexo} onChange={(e) => setSexo(e.target.value)}>
            <option value="MASCULINO">Masculino</option>
            <option value="FEMENINO">Femenino</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Procesando...' : 'Calcular Base Reguladora'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {resultado && (
        <div className="resultado">
          <h3>Resultado del Cálculo</h3>
          <p><strong>Base Reguladora:</strong> {resultado.estadisticas.base_reguladora}€</p>
          <p><strong>Método Usado:</strong> {resultado.calculo_elegido}</p>
          <p><strong>Total Bases:</strong> {resultado.estadisticas.total_bases}</p>
          <p><strong>Suma Total:</strong> {resultado.estadisticas.suma_total}€</p>
          
          <h4>Comparativa de Cálculos</h4>
          <p>
            Reforma RD 2/2023: {resultado.comparativa_calculos.calculo_reforma_rd2_2023.estadisticas.base_reguladora}€
          </p>
          <p>
            Prereforma: {resultado.comparativa_calculos.calculo_prereforma.estadisticas.base_reguladora}€
          </p>
        </div>
      )}
    </div>
  );
}

export default CalculadoraPension;
```

---

### Ejemplo 4: Verificar Estado de Salud (Monitoreo)

```python
import requests
import time

def verificar_salud_api(url="http://localhost:8000"):
    """
    Verifica el estado de salud de la API.
    Útil para monitoreo y health checks.
    """
    try:
        response = requests.get(f"{url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Saludable - Versión: {data['version']}")
            print(f"   Servicios:")
            for servicio, estado in data['services'].items():
                print(f"   - {servicio}: {estado}")
            return True
        else:
            print(f"❌ API no saludable - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar a la API: {e}")
        return False

# Uso en monitoreo continuo
while True:
    verificar_salud_api()
    time.sleep(60)  # Verificar cada minuto
```

---

## 🔧 Dependencias y Tecnologías

### Dependencias Principales

```txt
# Framework Web
fastapi==0.104.1                # Framework web moderno y rápido
uvicorn==0.24.0                 # Servidor ASGI
gunicorn==21.2.0                # Servidor HTTP para producción

# Validación de Datos
pydantic==2.5.0                 # Validación y serialización de datos
pydantic-core==2.14.1

# Procesamiento de PDFs
pdfplumber==0.11.7              # Extracción de texto de PDFs
pdfminer-six==20250506          # Herramientas de parsing PDF
pypdfium2==4.30.1               # Renderizado de PDFs

# Manejo de Datos
pandas==2.3.0                   # Análisis de datos
numpy==1.26.4                   # Operaciones numéricas

# Fechas y Tiempo
python-dateutil==2.8.2          # Manipulación avanzada de fechas
pytz==2025.2                    # Zonas horarias

# Configuración
PyYAML==6.0.1                   # Parsing de archivos YAML
python-dotenv==1.1.1            # Variables de entorno

# HTTP y Archivos
requests==2.31.0                # Cliente HTTP
python-multipart==0.0.6         # Soporte para multipart/form-data

# Utilidades
click==8.1.8                    # CLI utilities
colorama==0.4.6                 # Colores en terminal
rich==13.9.4                    # Terminal formatting
```

### Dependencias de Desarrollo y Testing

```txt
pytest==8.4.1                   # Framework de testing
```

### Tecnologías de Infraestructura

- **Python**: 3.9+
- **Servidor ASGI**: Uvicorn (desarrollo) / Gunicorn + Uvicorn workers (producción)
- **Base de datos**: No requiere (configuración en YAML)
- **Almacenamiento**: Sistema de archivos local para PDFs temporales

---

## 🌍 Variables de Entorno

### Variables Opcionales

```bash
# Entorno de ejecución
ENVIRONMENT=development          # "development" o "production"

# Puerto (para producción)
PORT=8000                        # Puerto en el que escucha la API

# CORS (para producción específica)
ALLOWED_ORIGINS=https://tu-frontend.com,https://otro-dominio.com
```

### Configuración de Desarrollo

Archivo `.env` (opcional):
```env
ENVIRONMENT=development
PORT=8000
```

### Configuración de Producción

Variables necesarias según plataforma:

**Heroku:**
```bash
heroku config:set ENVIRONMENT=production
# El PORT se asigna automáticamente
```

**Railway/Render:**
- Detectan automáticamente Python y requirements.txt
- No requieren configuración adicional

**DigitalOcean:**
```bash
ENVIRONMENT=production
PORT=8080  # O el puerto configurado
```

---

## 🔒 Consideraciones de Seguridad

### 1. Validación de Archivos

✅ **Implementado:**
- Verificación de extensión `.pdf`
- Límite de tamaño: 10MB máximo
- Validación de contenido del PDF

❌ **No implementado (considerar para producción):**
- Escaneo antivirus de archivos subidos
- Validación de firma digital del PDF
- Whitelist de tipos MIME

### 2. CORS (Cross-Origin Resource Sharing)

**Desarrollo:**
```python
allow_origins=["*"]  # Permite todos los orígenes
```

**Producción (Recomendado):**
```python
allowed_origins = [
    "https://tu-frontend.com",
    "https://otro-dominio-autorizado.com"
]
```

Modificar en `app_production.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Lista específica
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Métodos específicos
    allow_headers=["*"]
)
```

### 3. Manejo de Errores en Producción

✅ **Implementado:**
- No expone stack traces en producción
- Mensajes de error genéricos para el cliente
- Logging interno para debugging

### 4. Archivos Temporales

✅ **Implementado:**
- PDFs se guardan en archivos temporales
- Limpieza automática después del procesamiento
- Uso de `tempfile` de Python

### 5. Validación de Datos

✅ **Implementado:**
- Validación con Pydantic en todos los endpoints
- Sanitización de datos de entrada
- Validación de formatos de fecha
- Validación de valores numéricos

### 6. Rate Limiting

❌ **No implementado**

Para producción, considerar añadir:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/process")
@limiter.limit("10/minute")  # 10 requests por minuto
async def process_pdf_complete(...):
    ...
```

### 7. Autenticación y Autorización

❌ **No implementado**

La API actual es pública. Para producción con acceso restringido:

**Opción 1: API Key**
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != "tu-api-key-secreta":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/api/process")
async def process(api_key: str = Depends(get_api_key)):
    ...
```

**Opción 2: JWT Token**
```python
from fastapi import Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    # Verificar JWT token
    pass
```

### 8. HTTPS en Producción

⚠️ **Importante:**
- Usar siempre HTTPS en producción
- Plataformas como Heroku, Railway, Render proveen HTTPS automáticamente
- Para servidores propios, configurar certificados SSL/TLS

### 9. Logging y Auditoría

**Implementar en producción:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.post("/api/process")
async def process_pdf_complete(...):
    logger.info(f"Procesando PDF: {file.filename} - Usuario: {user_id}")
    # ... lógica
    logger.info(f"PDF procesado exitosamente: {file.filename}")
```

---

## 🎓 Normativa y Referencias Legales

### Legislación Aplicada

1. **Real Decreto 2/2023**
   - Reforma del sistema de pensiones
   - Nuevos parámetros de cálculo progresivos

2. **Ley General de la Seguridad Social (LGSS)**
   - Real Decreto Legislativo 8/2015
   - Artículo 209.1: Cálculo de base reguladora
   - Disposición Transitoria 41ª: Manejo de lagunas diferenciado por sexo

3. **Revalorización de Bases**
   - Índice de Precios al Consumo (IPC)
   - Fuente: Instituto Nacional de Estadística (INE)

---

## 📝 Notas para Integración

### Puntos Clave

1. **Endpoint Recomendado**: `/api/process`
   - Procesa todo en un solo paso
   - Más eficiente que extract + simulate separado

2. **Formato de Fechas**: Siempre `MM/YYYY`
   - Ejemplo válido: `06/2025`
   - Ejemplo inválido: `2025-06`, `06/25`

3. **Regímenes Soportados**: Solo dos opciones
   - `GENERAL`
   - `AUTONOMO`

4. **Sexo del Cotizante**: Afecta cálculo de lagunas
   - `MASCULINO`: Aplica reglas estándar
   - `FEMENINO`: Aplica DT 41ª (más favorable)

5. **Tamaño de Archivos**: Máximo 10MB por PDF
   - Validar en frontend antes de enviar
   - Mostrar error claro al usuario

6. **Tiempos de Procesamiento**:
   - Extracción: 2-5 segundos típico
   - Simulación: 1-3 segundos típico
   - Proceso completo: 3-8 segundos típico

7. **Doble Cálculo Automático**:
   - La API calcula con ambos métodos
   - Devuelve ambos resultados en `comparativa_calculos`
   - El campo `calculo_elegido` indica cuál es más favorable

### Recomendaciones de UX

1. **Mostrar Progress**:
   ```javascript
   // Indicar al usuario que el procesamiento puede tardar
   showLoading("Procesando PDF, esto puede tardar unos segundos...");
   ```

2. **Validar Fecha**:
   ```javascript
   function validarFecha(fecha) {
     const regex = /^\d{2}\/\d{4}$/;
     return regex.test(fecha);
   }
   ```

3. **Mostrar Comparativa**:
   - Siempre mostrar ambos cálculos al usuario
   - Destacar visualmente el más favorable
   - Explicar la diferencia entre reforma y prereforma

4. **Manejo de Errores**:
   - Mostrar mensajes de error claros
   - Sugerir soluciones (ej: "El archivo es muy grande, intente con un PDF más pequeño")

---

## 🧪 Testing de la API

### Verificación Básica

```bash
# 1. Verificar que la API está corriendo
curl http://localhost:8000/health

# 2. Ver documentación interactiva
# Abrir en navegador: http://localhost:8000/docs

# 3. Probar extracción (necesitas un PDF)
curl -X POST "http://localhost:8000/api/extract" \
  -F "file=@test.pdf"

# 4. Ver configuración disponible
curl http://localhost:8000/api/simulate/config
```

### Test con Python

```python
import requests

# Test health check
response = requests.get("http://localhost:8000/health")
assert response.status_code == 200
assert response.json()["status"] == "healthy"

# Test configuración
response = requests.get("http://localhost:8000/api/simulate/config")
assert response.status_code == 200
assert "regimenes_soportados" in response.json()
```

---

## 🚀 Despliegue

### Opción 1: Desarrollo Local

```bash
# Clonar repositorio (si aplica)
git clone <repo-url>
cd basesParser

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py

# API disponible en: http://localhost:8000
# Documentación en: http://localhost:8000/docs
```

### Opción 2: Producción con Heroku

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Crear app
heroku create tu-app-bases-api

# Configurar
heroku config:set ENVIRONMENT=production

# Desplegar
git push heroku main

# Ver logs
heroku logs --tail

# URL: https://tu-app-bases-api.herokuapp.com
```

### Opción 3: Docker (Recomendado para integración)

Crear `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app_production:app", "--host", "0.0.0.0", "--port", "8000"]
```

Construir y ejecutar:
```bash
docker build -t bases-api .
docker run -p 8000:8000 bases-api
```

---

## 📞 Información de Contacto y Soporte

### Documentación
- **Swagger UI**: `{base_url}/docs`
- **Este archivo**: Documentación completa de integración

### Endpoints de Utilidad
- **Health Check**: `GET /health`
- **Info API**: `GET /api/info`
- **Config**: `GET /api/simulate/config`

---

## 📚 Glosario de Términos

- **Base de Cotización**: Importe sobre el que se calculan las cotizaciones a la Seguridad Social
- **Base Reguladora**: Promedio de bases que determina la cuantía de la pensión
- **Laguna de Cotización**: Período sin cotización dentro del período de cómputo
- **Período de Cómputo**: Ventana temporal de bases consideradas para el cálculo
- **Revalorización**: Actualización de bases antiguas aplicando IPC acumulado
- **Pluriactividad**: Cotización simultánea en múltiples regímenes o empresas
- **IPC**: Índice de Precios al Consumo (inflación)
- **LGSS**: Ley General de la Seguridad Social
- **DT 41ª**: Disposición Transitoria 41ª de la LGSS (reglas especiales de lagunas para mujeres)
- **RD 2/2023**: Real Decreto 2/2023 de reforma del sistema de pensiones

---

## ✅ Checklist de Integración

Usa este checklist al integrar la API:

- [ ] Entorno de desarrollo configurado y API corriendo
- [ ] Health check funcionando (`GET /health`)
- [ ] Documentación Swagger revisada (`/docs`)
- [ ] Endpoint de extracción probado con PDF real
- [ ] Endpoint de simulación probado
- [ ] Endpoint de proceso completo probado
- [ ] Validación de fechas implementada en frontend
- [ ] Validación de tamaño de archivo (10MB)
- [ ] Manejo de errores implementado
- [ ] Loading states implementados (procesamiento puede tardar)
- [ ] CORS configurado correctamente para producción
- [ ] Variables de entorno configuradas
- [ ] Testing básico completado
- [ ] Monitoreo de salud implementado
- [ ] Despliegue en producción exitoso

---

## 🔄 Versionado

**Versión Actual**: 1.0.0

**Cambios Futuros**:
- Las actualizaciones de normativa se reflejan en archivos YAML
- Los parámetros de cómputo se actualizan anualmente
- El IPC se actualiza conforme INE publica nuevos datos

**Compatibilidad**:
- La API mantiene retrocompatibilidad en respuestas
- Nuevos campos se añaden sin eliminar existentes

---

## 📄 Licencia

MIT License - Ver archivo `LICENSE` en el repositorio

---

**Fin de la Documentación**

Esta documentación está diseñada para que cualquier agente de IA o desarrollador pueda integrar exitosamente esta API con otros sistemas. Si necesitas información adicional, consulta la documentación interactiva en `/docs` o revisa el código fuente.


