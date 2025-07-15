#!/usr/bin/env python3
"""
Script de demostración de la API Bases de Cotización.
Muestra todas las funcionalidades disponibles.
"""

import requests
import json
import time
from pathlib import Path

# Configuración de la API
API_BASE_URL = "http://localhost:8000"
API_URLS = {
    "health": f"{API_BASE_URL}/health",
    "info": f"{API_BASE_URL}/api/info",
    "config": f"{API_BASE_URL}/api/simulate/config",
    "extract": f"{API_BASE_URL}/api/extract",
    "simulate": f"{API_BASE_URL}/api/simulate",

}

def print_header(title):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*60}")
    print(f"🔥 {title}")
    print('='*60)

def print_section(title):
    """Imprime una sección formateada."""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print('─'*40)

def check_api_status():
    """Verifica que la API esté funcionando."""
    print_header("VERIFICACIÓN DE ESTADO DE LA API")
    
    try:
        response = requests.get(API_URLS["health"], timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API funcionando correctamente")
            print(f"📊 Estado: {health_data.get('status', 'unknown')}")
            print(f"📝 Mensaje: {health_data.get('message', 'N/A')}")
            print(f"🔢 Versión: {health_data.get('version', 'N/A')}")
            
            # Mostrar estado de servicios
            services = health_data.get('services', {})
            print("\n🔧 Estado de servicios:")
            for service, status in services.items():
                print(f"   • {service}: {status}")
                
            return True
        else:
            print(f"❌ Error: La API respondió con código {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar con la API")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def get_api_info():
    """Obtiene información detallada de la API."""
    print_section("Información de la API")
    
    try:
        response = requests.get(API_URLS["info"])
        if response.status_code == 200:
            info = response.json()
            print(f"📛 Nombre: {info.get('api_name', 'N/A')}")
            print(f"🔢 Versión: {info.get('version', 'N/A')}")
            print(f"📝 Descripción: {info.get('description', 'N/A')}")
            
            print("\n🚀 Características:")
            for feature in info.get('features', []):
                print(f"   • {feature}")
                
            print(f"\n📄 Formatos soportados: {', '.join(info.get('supported_formats', []))}")
            print(f"🏢 Regímenes soportados: {', '.join(info.get('supported_regimes', []))}")
            
        else:
            print(f"❌ Error obteniendo información: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def get_simulation_config():
    """Obtiene la configuración de simulación."""
    print_section("Configuración de Simulación")
    
    try:
        response = requests.get(API_URLS["config"])
        if response.status_code == 200:
            config = response.json()
            
            # Mostrar índices de revalorización
            indices = config.get('indices_revalorizacion', {})
            if indices:
                print("📈 Índices de Revalorización:")
                total_indices = indices.get('total_indices', 0)
                print(f"   📊 Total índices: {total_indices}")
                años_disponibles = indices.get('años_disponibles', [])
                if años_disponibles:
                    print(f"   📅 Años disponibles: {años_disponibles[:5]}..." if len(años_disponibles) > 5 else f"   📅 Años disponibles: {años_disponibles}")
                periodo_cobertura = indices.get('periodo_cobertura', {})
                if periodo_cobertura.get('desde') and periodo_cobertura.get('hasta'):
                    print(f"   📅 Rango: {periodo_cobertura['desde']} → {periodo_cobertura['hasta']}")
            
            # Mostrar bases mínimas
            bases_min = config.get('bases_minimas', {})
            if bases_min:
                print("\n💰 Bases Mínimas:")
                años_disponibles = bases_min.get('años_disponibles', [])
                if años_disponibles:
                    print(f"   📅 Años disponibles: {años_disponibles[:5]}..." if len(años_disponibles) > 5 else f"   📅 Años disponibles: {años_disponibles}")
                    año_min = bases_min.get('año_minimo')
                    año_max = bases_min.get('año_maximo')
                    if año_min and año_max:
                        print(f"   📊 Rango: {año_min} → {año_max}")
                else:
                    print("   ⚠️ No hay datos de bases mínimas disponibles")
            
            # Mostrar parámetros de cómputo
            params = config.get('parametros_computo', {})
            if params:
                print("\n🧮 Parámetros de Cómputo:")
                años_disponibles = params.get('años_disponibles', [])
                if años_disponibles:
                    print(f"   📅 Años disponibles: {años_disponibles[:5]}..." if len(años_disponibles) > 5 else f"   📅 Años disponibles: {años_disponibles}")
                    año_min = params.get('año_minimo')
                    año_max = params.get('año_maximo')
                    if año_min and año_max:
                        print(f"   📊 Rango: {año_min} → {año_max}")
                else:
                    print("   ⚠️ No hay datos de parámetros de cómputo disponibles")
            
            return config
        else:
            print(f"❌ Error obteniendo configuración: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_extraction():
    """Prueba la extracción de bases (simulada con datos de ejemplo)."""
    print_section("Prueba de Extracción de Bases")
    
    # Buscar archivos PDF de prueba
    test_files = list(Path("tests/bases_data").glob("*.pdf"))
    
    if not test_files:
        print("⚠️  No se encontraron archivos PDF de prueba en tests/bases_data/")
        print("💡 Para probar la extracción, añade archivos PDF en esa carpeta")
        return None
    
    test_file = test_files[0]
    print(f"📄 Usando archivo de prueba: {test_file.name}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            response = requests.post(API_URLS["extract"], files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Extracción exitosa")
            print(f"📊 Total bases extraídas: {result.get('total_bases', 0)}")
            print(f"📝 Mensaje: {result.get('message', 'N/A')}")
            
            # Mostrar metadatos
            metadata = result.get('metadata', {})
            print(f"\n📁 Metadatos del archivo:")
            print(f"   • Nombre: {metadata.get('filename', 'N/A')}")
            print(f"   • Tamaño: {metadata.get('file_size', 0):,} bytes")
            print(f"   • Empresas: {metadata.get('total_empresas', 0)}")
            
            # Mostrar algunas bases de ejemplo
            bases = result.get('bases', [])
            if bases:
                print(f"\n📋 Primeras 3 bases extraídas:")
                for base in bases[:3]:
                    print(f"   • {base.get('mes_anyo', 'N/A')}: {base.get('base', 0):.2f}€ - {base.get('empresa', 'N/A')}")
            
            return bases
        else:
            print(f"❌ Error en extracción: {response.status_code}")
            if response.text:
                print(f"📝 Detalle: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_simulation(bases=None):
    """Prueba la simulación de bases."""
    print_section("Prueba de Simulación")
    
    # Si no hay bases de extracción, usar datos de ejemplo
    if not bases:
        print("📊 Usando datos de ejemplo para la simulación")
        bases = [
            {"mes_anyo": "01/2023", "base": 2500.00, "empresa": "EMPRESA EJEMPLO SL", "regimen": "GENERAL"},
            {"mes_anyo": "02/2023", "base": 2550.00, "empresa": "EMPRESA EJEMPLO SL", "regimen": "GENERAL"},
            {"mes_anyo": "03/2023", "base": 2600.00, "empresa": "EMPRESA EJEMPLO SL", "regimen": "GENERAL"},
        ]
    
    # Preparar datos de simulación
    simulation_data = {
        "bases_extraidas": bases[:12] if len(bases) > 12 else bases,  # Máximo 12 bases para la demo
        "fecha_jubilacion": "06/2025",
        "regimen_acceso": "GENERAL",
        "sexo": "MASCULINO"
    }
    
    try:
        # Prueba simulación completa
        print("🧮 Ejecutando simulación completa...")
        response = requests.post(API_URLS["simulate"], json=simulation_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simulación completa exitosa")
            
            # Mostrar cálculo elegido
            calculo_elegido = result.get('calculo_elegido', 'N/A')
            print(f"\n🏆 Cálculo elegido: {calculo_elegido}")
            
            # Estadísticas principales
            stats = result.get('estadisticas', {})
            print(f"\n📊 Estadísticas del cálculo elegido:")
            print(f"   • Total bases: {stats.get('total_bases', 0)}")
            print(f"   • Bases revalorizadas: {stats.get('bases_revalorizadas', 0)}")
            print(f"   • Suma total: {stats.get('suma_total', 0):,.2f}€")
            print(f"   • 💰 Base reguladora: {stats.get('base_reguladora', 0):,.2f}€")
            
            # Mostrar comparativa si está disponible
            comparativa = result.get('comparativa_calculos', {})
            if comparativa:
                print(f"\n🔍 Comparativa de cálculos:")
                for calculo, datos in comparativa.items():
                    br = datos.get('estadisticas', {}).get('base_reguladora', 0)
                    print(f"   • {calculo}: {br:,.2f}€")
            
        else:
            print(f"❌ Error en simulación completa: {response.status_code}")
        

            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_endpoints():
    """Muestra todos los endpoints disponibles."""
    print_section("Endpoints Disponibles")
    
    endpoints = [
        ("GET", "/", "🏠 Página de inicio con información"),
        ("GET", "/health", "💊 Estado de salud de la API"),
        ("GET", "/docs", "📖 Documentación Swagger interactiva"),
        ("GET", "/api/info", "ℹ️ Información detallada de la API"),
        ("GET", "/api/simulate/config", "⚙️ Configuración de simulación"),
        ("POST", "/api/extract", "📄 Extraer bases de PDF"),
        ("POST", "/api/simulate", "🧮 Simulación completa"),
        ("POST", "/api/process", "🚀 Procesar PDF completo (Extraer + Simular)"),
    ]
    
    for method, endpoint, description in endpoints:
        color = "🟢" if method == "GET" else "🔴"
        print(f"{color} {method:4} {endpoint:25} - {description}")

def show_documentation_links():
    """Muestra enlaces importantes."""
    print_section("Enlaces Importantes")
    
    links = [
        ("🏠 Página Principal", "http://localhost:8000"),
        ("📖 Documentación Swagger", "http://localhost:8000/docs"),
        ("💊 Health Check", "http://localhost:8000/health"),
        ("ℹ️ Información API", "http://localhost:8000/api/info"),
    ]
    
    for title, url in links:
        print(f"{title}: {url}")

def main():
    """Función principal de demostración."""
    print_header("DEMOSTRACIÓN COMPLETA DE LA API BASES DE COTIZACIÓN")
    print("🚀 Esta demostración probará todas las funcionalidades de la API")
    
    # 1. Verificar estado de la API
    if not check_api_status():
        print("\n❌ No se puede continuar sin conexión a la API")
        return
    
    # 2. Obtener información de la API
    get_api_info()
    
    # 3. Mostrar endpoints disponibles
    show_endpoints()
    
    # 4. Mostrar enlaces importantes
    show_documentation_links()
    
    # 5. Obtener configuración
    config = get_simulation_config()
    
    # 6. Probar extracción
    extracted_bases = test_extraction()
    
    # 7. Probar simulación
    test_simulation(extracted_bases)
    
    print("\n" + "─" * 60)
    print("📋 Pruebas de Endpoints de Configuración")
    print("─" * 60)

    # Probar endpoints de configuración individual
config_endpoints = [
    ("parametros", "📊 Parámetros de Cómputo"),
    ("indices", "📈 Índices de Revalorización"), 
    ("topes", "💰 Topes de Cotización"),
    ("all", "🔧 Configuración Completa")
]

for endpoint, nombre in config_endpoints:
    try:
        print(f"\n🔍 Probando {nombre}...")
        response = requests.get(f"{API_BASE_URL}/api/config/{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {nombre} obtenida exitosamente")
            
            if endpoint == "parametros":
                print(f"   📊 Total años: {data.get('total_años', 0)}")
                print(f"   📅 Años disponibles: {data.get('años_disponibles', [])[:3]}...")
            elif endpoint == "indices":
                print(f"   📈 Total índices: {data.get('total_indices', 0)}")
                rango = data.get('rango_fechas', {})
                print(f"   📅 Rango: {rango.get('desde', 'N/A')} → {rango.get('hasta', 'N/A')}")
            elif endpoint == "topes":
                print(f"   💰 Total años: {data.get('total_años', 0)}")
                print(f"   📅 Años disponibles: {data.get('años_disponibles', [])[:3]}...")
            elif endpoint == "all":
                resumen = data.get('resumen', {})
                print(f"   📊 Parámetros: {resumen.get('total_parametros', 0)}")
                print(f"   📈 Índices: {resumen.get('total_indices', 0)}")
                print(f"   💰 Topes: {resumen.get('total_topes', 0)}")
        else:
            print(f"❌ Error {response.status_code}: {nombre}")
            
    except Exception as e:
        print(f"❌ Error probando {nombre}: {str(e)}")

print("\n" + "─" * 60)
print("📋 Enlaces Directos a Endpoints de Configuración:")
print("📊 Parámetros: http://localhost:8000/api/config/parametros")
print("📈 Índices: http://localhost:8000/api/config/indices")
print("💰 Topes: http://localhost:8000/api/config/topes")
print("🔧 Todo: http://localhost:8000/api/config/all")

# Mensaje final
print_header("¡DEMOSTRACIÓN COMPLETADA!")
print("✅ Todas las pruebas han sido ejecutadas")
print("📖 Visita http://localhost:8000/docs para probar la API interactivamente")
print("🏠 Página principal: http://localhost:8000")

if __name__ == "__main__":
    main() 