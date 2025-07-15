#!/usr/bin/env python3
"""
Script de prueba para la API de bases de cotización.
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import BasesAPIClient


def main():
    """Función principal de prueba."""
    # Crear cliente
    client = BasesAPIClient("http://localhost:8000")
    
    print("🧪 Probando API de Bases de Cotización")
    print("=" * 50)
    
    # 1. Health check
    print("1. Verificando estado de la API...")
    if client.health_check():
        print("   ✅ API funcionando correctamente")
    else:
        print("   ❌ API no responde. ¿Está ejecutándose?")
        print("   💡 Ejecuta: python app.py")
        return
    
    # 2. Obtener configuración
    print("\n2. Obteniendo configuración...")
    try:
        config = client.get_simulation_config()
        print(f"   ✅ Configuración obtenida")
        print(f"   📊 Años parámetros: {config['parametros_computo']['años_disponibles'][:5]}...")
        print(f"   📈 Régimenes: {config['regimenes_soportados']}")
    except Exception as e:
        print(f"   ❌ Error obteniendo configuración: {e}")
    
    # 3. Probar con archivo de ejemplo si existe
    test_files = [
        Path("tests/bases_data/bases1.pdf"),
        Path("tests/bases_data/bases2.pdf")
    ]
    
    for test_file in test_files:
        if test_file.exists():
            print(f"\n3. Probando extracción con {test_file.name}...")
            try:
                result = client.extract_bases(test_file)
                print(f"   ✅ Extraídas {result['total_bases']} bases")
                
                # Probar simulación si hay bases
                if result['total_bases'] > 0:
                    print("\n4. Probando simulación...")
                    # Convertir bases al formato esperado
                    bases_dict = [base.__dict__ for base in result['bases']]
                    sim_result = client.simulate_bases(
                        bases_dict, 
                        "06/2025", 
                        "GENERAL",
                        "MASCULINO"
                    )
                    print(f"   ✅ Base reguladora: {sim_result['estadisticas']['base_reguladora']:.2f}€")
                    
            except Exception as e:
                print(f"   ❌ Error en prueba: {e}")
            break
    else:
        print("\n3. No se encontraron archivos de prueba")
        print("   💡 Coloca un PDF en tests/bases_data/ para probar extracción")
    
    print("\n✅ Pruebas completadas")
    print("\n📖 Documentación disponible en: http://localhost:8000/docs")


if __name__ == "__main__":
    main() 