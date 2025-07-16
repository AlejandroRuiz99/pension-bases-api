"""
API FastAPI para extraer bases de cotización y calcular base reguladora.
Versión optimizada para producción.
"""

import os
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
    print("🚀 Iniciando API de Bases de Cotización (Producción)...")
    yield
    # Shutdown
    print("🛑 Cerrando API de Bases de Cotización...")


# Crear la aplicación FastAPI con documentación
app = FastAPI(
    title="🏢 API Bases de Cotización",
    description="""
    ## 📊 API para Extracción y Cálculo de Bases de Cotización
    
    API profesional para:
    * **📄 Extracción de bases** de archivos PDF
    * **🧮 Simulación de períodos** y cálculo de base reguladora  
    * **⚙️ Configuración** de parámetros normativos
    
    ### 🚀 Endpoints Principales:
    * `POST /api/process` - Procesamiento completo (PDF → Base Reguladora)
    * `POST /api/extract` - Extracción de bases de PDF
    * `POST /api/simulate` - Cálculo de base reguladora
    * `GET /api/simulate/config` - Configuración disponible
    """,
    version="1.0.0",
    contact={
        "name": "API Bases de Cotización",
        "url": "https://github.com/tu-usuario/bases-cotizacion"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para producción
allowed_origins = [
    "https://pension-bases-api-e707c1384c99.herokuapp.com",  # Tu app de Heroku
    "http://localhost:3000",  # Para desarrollo local
    "http://localhost:8080",  # Para desarrollo local
    "http://localhost:8000",  # Para desarrollo local
]

# Por ahora, permitir todos los orígenes para facilitar testing
allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
    """Página de inicio de la API."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Bases de Cotización</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; color: white;
            }
            .container { 
                background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; 
                backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { text-align: center; font-size: 2.5em; margin-bottom: 10px; }
            .subtitle { text-align: center; opacity: 0.9; margin-bottom: 30px; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
            .feature { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: center; }
            .links { display: flex; justify-content: center; gap: 15px; margin: 30px 0; flex-wrap: wrap; }
            .btn { 
                background: rgba(255,255,255,0.2); color: white; padding: 12px 24px; 
                border-radius: 25px; text-decoration: none; transition: all 0.3s;
                border: 1px solid rgba(255,255,255,0.3);
            }
            .btn:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
            .status { text-align: center; background: rgba(0,255,0,0.2); padding: 15px; border-radius: 10px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 API Bases de Cotización</h1>
            <p class="subtitle">Extracción y cálculo de bases reguladoras profesional</p>
            
            <div class="status">
                ✅ <strong>API Activa</strong> - Todos los servicios operativos
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>📄 Extracción</h3>
                    <p>Procesa PDFs de la Seguridad Social automáticamente</p>
                </div>
                <div class="feature">
                    <h3>🧮 Cálculo</h3>
                    <p>Simula períodos y calcula base reguladora según normativa 2025</p>
                </div>
                <div class="feature">
                    <h3>⚙️ Configuración</h3>
                    <p>Parámetros actualizados de índices y topes de cotización</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs" class="btn">📖 Documentación API</a>
                <a href="/health" class="btn">💊 Estado</a>
                <a href="/api/simulate/config" class="btn">⚙️ Configuración</a>
            </div>
        </div>
    </body>
    </html>
    """)


@app.get("/health", tags=["💊 Salud"])
async def health_check():
    """Endpoint de verificación de salud."""
    try:
        from core.config.config_manager import config
        
        # Verificar configuraciones
        config.cargar_indices_revalorizacion()
        config.cargar_topes_cotizacion()
        config.cargar_parametros_computo()
        
        return {
            "status": "healthy",
            "message": "API funcionando correctamente",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "services": {
                "extraction": "✅ Operativo",
                "simulation": "✅ Operativo", 
                "configuration": "✅ Operativo"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Servicio no disponible: {str(e)}")


# Manejadores de errores
@app.exception_handler(BasesParserError)
async def bases_parser_exception_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # En producción, no mostrar detalles del error
    if os.getenv("ENVIRONMENT") == "development":
        return HTTPException(status_code=500, detail=str(exc))
    else:
        return HTTPException(status_code=500, detail="Error interno del servidor")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Iniciando servidor de producción...")
    print(f"📖 Documentación: http://localhost:{port}/docs")
    
    uvicorn.run(
        "app_production:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    ) 