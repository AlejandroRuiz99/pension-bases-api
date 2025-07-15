"""
API FastAPI para extraer bases de cotización y calcular base reguladora.
Punto de entrada principal de la aplicación.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from api.endpoints import extract, simulate, config_info
from core.config.errors import BasesParserError


# Configuración de la aplicación durante el startup y shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando API de Bases de Cotización...")
    yield
    # Shutdown
    print("🛑 Cerrando API de Bases de Cotización...")


# Crear la aplicación FastAPI con documentación mejorada
app = FastAPI(
    title="🏢 API Bases de Cotización",
    description="""
    ## 📊 API para Extracción y Cálculo de Bases de Cotización
    
    Esta API permite:
    
    ### 📄 Extracción de PDFs
    * **Extraer bases de cotización** de archivos PDF
    * **Identificar empresas y regímenes** automáticamente
    * **Validar y procesar datos** de forma robusta
    
    ### 🧮 Simulación y Cálculo
    * **Simular períodos futuros** hasta la fecha de jubilación
    * **Aplicar revalorización** según normativa 2025
    * **Calcular base reguladora** para pensiones
    * **Manejar lagunas** de cotización automáticamente
    
    ### 🔧 Características
    * Validación automática con **Pydantic**
    * Manejo robusto de **errores**
    * Compatible con **múltiples regímenes** (General, Autónomo)
    
    ---
    
    ### 🚀 Inicio Rápido
    
    1. **Extraer bases**: Sube un PDF con `POST /api/extract`
    2. **Calcular pensión**: Usa las bases extraídas con `POST /api/simulate`
    3. **Ver configuración**: Consulta parámetros con `GET /api/simulate/config`
    """,
    version="1.0.0",
    contact={
        "name": "Soporte API Bases de Cotización",
        "email": "soporte@basescotizacion.es",
        "url": "https://github.com/tu-repo/bases-cotizacion"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo"
        }
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None
)

# Configurar CORS para permitir requests desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios concretos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de los endpoints
app.include_router(extract.router, prefix="/api", tags=["📄 Extracción"])
app.include_router(simulate.router, prefix="/api", tags=["🧮 Simulación"])
app.include_router(config_info.router, prefix="/api/config", tags=["🔧 Configuración"])


@app.get("/", response_class=HTMLResponse, tags=["🏠 Inicio"])
async def root():
    """Página de inicio con información de la API y enlaces útiles."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Bases de Cotización</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px; 
                line-height: 1.6;
                background-color: #f5f5f5;
            }
            .container { 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; text-align: center; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
            .endpoint { 
                background: #ecf0f1; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 5px; 
                border-left: 4px solid #3498db;
            }
            .method { 
                color: white; 
                padding: 3px 8px; 
                border-radius: 3px; 
                font-weight: bold; 
                font-size: 12px;
            }
            .get { background-color: #27ae60; }
            .post { background-color: #e74c3c; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .status { 
                text-align: center; 
                padding: 10px; 
                background: #d5f4e6; 
                border-radius: 5px; 
                margin: 20px 0;
            }
            .quick-links {
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
            }
            .link-button {
                background: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                transition: background 0.3s;
            }
            .link-button:hover {
                background: #2980b9;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 API Bases de Cotización</h1>
            
            <div class="status">
                ✅ <strong>API Activa</strong> - Todos los servicios funcionando correctamente
            </div>
            
            <div class="quick-links">
                <a href="/docs" class="link-button">📖 Documentación Swagger</a>
                <a href="/health" class="link-button">💊 Estado de Salud</a>
                <a href="/api/info" class="link-button">ℹ️ Información API</a>
            </div>
            
            <h2>🚀 Endpoints Disponibles</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/extract</strong><br>
                📄 Extrae bases de cotización de archivos PDF
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/simulate</strong><br>
                🧮 Calcula base reguladora completa con simulación
            </div>
            

            
            <div class="endpoint">
                <span class="method get">GET</span> <strong>/api/simulate/config</strong><br>
                ⚙️ Obtiene configuración disponible para simulaciones
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/process</strong><br>
                🚀 Procesa PDF completo: extrae bases y simula automáticamente
            </div>
            
            <h2>🔧 Cómo Usar</h2>
            
            <h3>🚀 Opción 1: Todo en uno (Recomendado)</h3>
            <ol>
                <li><strong>Procesamiento completo:</strong> Sube un PDF y obtén la base reguladora directamente con <code>POST /api/process</code></li>
            </ol>
            
            <h3>🔧 Opción 2: Paso a paso</h3>
            <ol>
                <li><strong>Extracción:</strong> Sube un PDF con bases de cotización usando <code>POST /api/extract</code></li>
                <li><strong>Simulación:</strong> Usa las bases extraídas para calcular la pensión con <code>POST /api/simulate</code></li>
                <li><strong>Configuración:</strong> Consulta parámetros disponibles con <code>GET /api/simulate/config</code></li>
            </ol>
            
            <h2>📱 Probar la API</h2>
            <p>Utiliza la <a href="/docs">documentación interactiva de Swagger</a> para probar todos los endpoints directamente desde el navegador.</p>
            
            <h2>ℹ️ Información Técnica</h2>
            <ul>
                <li><strong>Versión:</strong> 1.0.0</li>
                <li><strong>Framework:</strong> FastAPI</li>
                <li><strong>Validación:</strong> Pydantic</li>
            </ul>
        </div>
    </body>
    </html>
    """)


@app.get("/health", tags=["💊 Salud"])
async def health_check():
    """
    Endpoint de verificación de salud de la API.
    
    Returns:
        dict: Estado de salud con información del sistema
    """
    try:
        from core.config.config_manager import config
        
        # Verificar que se pueden cargar las configuraciones
        config.cargar_indices_revalorizacion()
        config.cargar_topes_cotizacion()
        config.cargar_parametros_computo()
        
        return {
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
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Servicio no disponible: {str(e)}"
        )


@app.get("/api/info", tags=["ℹ️ Información"])
async def api_info():
    """
    Información detallada sobre la API y sus capacidades.
    
    Returns:
        dict: Información completa de la API
    """
    return {
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
        },
        "contact": {
            "support": "Documentación disponible en /docs"
        }
    }


# Manejador global de errores
@app.exception_handler(BasesParserError)
async def bases_parser_exception_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return HTTPException(status_code=500, detail="Error interno del servidor")


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando servidor API...")
    print("📖 Documentación disponible en: http://localhost:8000/docs")
    print("🏠 Página principal: http://localhost:8000")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 