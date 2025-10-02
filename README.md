# pension-bases_api
# 🏢 API Bases de Cotización

API profesional para extraer bases de cotización de PDFs y calcular base reguladora según la normativa española vigente 2025.

## 🚀 Características

- 📄 **Extracción automática** de bases de PDFs de la Seguridad Social
- 🧮 **Cálculo de base reguladora** con simulación de períodos futuros
- ⚙️ **Configuración actualizada** con índices de revalorización 2025
- 🔄 **Doble cálculo**: Reforma RD 2/2023 vs Prereforma (elige el más favorable)
- 🏢 **Múltiples regímenes**: General y Autónomo
- 👥 **Manejo de lagunas** diferenciado por sexo según DT 41ª
- 📊 **Revalorización dinámica con IPC**: Cálculo conforme a normativa LGSS (ver [REVALORIZACION_BASES.md](REVALORIZACION_BASES.md))

## 📊 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/process` | POST | 🚀 Procesamiento completo (PDF → Base Reguladora) |
| `/api/extract` | POST | 📄 Extrae bases de cotización de PDF |
| `/api/simulate` | POST | 🧮 Calcula base reguladora con simulación |
| `/api/simulate/config` | GET | ⚙️ Obtiene configuración disponible |
| `/docs` | GET | 📖 Documentación interactiva (Swagger) |

## 🛠️ Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/bases-cotizacion.git
cd bases-cotizacion

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar API
python app.py
```

## 🌐 Despliegue en Producción

### 1. Heroku (Recomendado - Fácil)

```bash
# Instalar Heroku CLI
# Ir a: https://devcenter.heroku.com/articles/heroku-cli

# Instalar gunicorn
pip install gunicorn

# Crear app en Heroku
heroku create tu-app-bases-cotizacion

# Configurar variables de entorno
heroku config:set ENVIRONMENT=production

# Desplegar
git add .
git commit -m "Deploy to production"
git push heroku main

# Ver logs
heroku logs --tail
```

**URL final**: `https://tu-app-bases-cotizacion.herokuapp.com`

### 2. Railway

1. Ve a [railway.app](https://railway.app)
2. Conecta tu repositorio GitHub
3. Se despliega automáticamente
4. **¡Listo!** 🎉

### 3. Render

1. Ve a [render.com](https://render.com)
2. Conecta GitHub → Nuevo Web Service
3. Configuración automática detectada
4. **Deploy** ✅

### 4. DigitalOcean App Platform

```bash
# Usar app_production.py como punto de entrada
# Configurar en el panel:
# - Build Command: pip install -r requirements-prod.txt
# - Run Command: gunicorn app_production:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📁 Archivos de Configuración Incluidos

- `Procfile` - Configuración para Heroku
- `runtime.txt` - Versión de Python
- `requirements-prod.txt` - Dependencias optimizadas
- `app_production.py` - Versión optimizada para producción

## 🔧 Configuración de Producción

### Variables de Entorno

```bash
# Opcional - para logs más detallados en desarrollo
ENVIRONMENT=development

# Para CORS específicos (reemplazar con tu dominio)
ALLOWED_ORIGINS=https://tu-frontend.com,https://tu-dominio.com
```

### Límites de Archivo

- **Tamaño máximo PDF**: 10MB
- **Timeout**: 30 segundos por request
- **Rate limiting**: Configurar según plataforma

## 📖 Ejemplos de Uso

### Procesamiento Completo (PDF → Base Reguladora)

```python
import requests

# Subir PDF y obtener base reguladora directamente
with open('bases_cotizacion.pdf', 'rb') as f:
    response = requests.post(
        'https://tu-api.herokuapp.com/api/process',
        files={'file': f},
        data={
            'fecha_jubilacion': '06/2025',
            'regimen_acceso': 'GENERAL',
            'sexo': 'MASCULINO'
        }
    )

resultado = response.json()
print(f"Base reguladora: {resultado['estadisticas']['base_reguladora']}€")
```

### Solo Extracción

```python
# Solo extraer bases del PDF
with open('bases.pdf', 'rb') as f:
    response = requests.post(
        'https://tu-api.herokuapp.com/api/extract',
        files={'file': f}
    )

bases = response.json()['bases']
print(f"Extraídas {len(bases)} bases de cotización")
```

## 🎯 Casos de Uso

1. **Calculadoras de pensiones** - Integrar en apps web/móvil
2. **Asesorías laborales** - Automatizar cálculos de clientes
3. **Gestorías** - Procesar múltiples PDFs automáticamente
4. **Plataformas financieras** - Estimaciones de pensiones

## 📚 Documentación Técnica Adicional

- **[REVALORIZACION_BASES.md](REVALORIZACION_BASES.md)**: Sistema de revalorización dinámica con IPC según normativa española
- **[scripts/ejemplo_revalorizacion.py](scripts/ejemplo_revalorizacion.py)**: Ejemplos prácticos de uso del sistema de revalorización

### ✨ Novedad: Sistema de Revalorización Dinámico

Este sistema ahora implementa el **método correcto de revalorización** según la Ley General de la Seguridad Social (LGSS):

- ✅ Cálculo dinámico basado en **IPC acumulado**
- ✅ Actualización automática año tras año
- ✅ Conforme al Real Decreto Legislativo 8/2015
- ✅ Transparente y auditable

**Antes**: Índices estáticos precalculados (~12,000 valores)  
**Ahora**: Cálculo dinámico desde IPCs anuales (~25 valores/año)

Ver documentación completa en [REVALORIZACION_BASES.md](REVALORIZACION_BASES.md)

## 🔐 Seguridad

- ✅ Validación de archivos PDF
- ✅ Límites de tamaño de archivo
- ✅ Sanitización de datos de entrada
- ✅ CORS configurado para producción
- ✅ Manejo seguro de errores (no exposición de detalles internos)

## 📱 URLs de Ejemplo

Después del despliegue, tu API estará disponible en:

- **Heroku**: `https://tu-app.herokuapp.com`
- **Railway**: `https://tu-app.railway.app`
- **Render**: `https://tu-app.onrender.com`

### Endpoints de Prueba

- 🏠 **Inicio**: `https://tu-api.com/`
- 📖 **Documentación**: `https://tu-api.com/docs`
- 💊 **Health Check**: `https://tu-api.com/health`
- ⚙️ **Configuración**: `https://tu-api.com/api/simulate/config`

## 🎉 ¡Tu API está lista para producción!

Con estos archivos, tu API se desplegará automáticamente en cualquier plataforma cloud moderna. **¡Empieza con Heroku para mayor simplicidad!**

---

**📧 Soporte**: [tu-email@example.com](mailto:tu-email@example.com)  
**🔗 Repositorio**: [GitHub](https://github.com/tu-usuario/bases-cotizacion) 