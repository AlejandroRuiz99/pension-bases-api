#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de simulación para jubilación el 11/10/2027.
Compara los índices calculados por el sistema con los extraídos de MM_content.txt.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from services.simulator import SimuladorPeriodos


def cargar_indices_referencia():
    """Carga los índices de referencia del JSON generado."""
    archivo_json = Path(__file__).parent.parent / 'resultados' / 'indices_revalorizacion.json'
    
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return datos['indices_revalorizacion']
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de referencia: {archivo_json}")
        return []
    except Exception as e:
        print(f"❌ Error cargando índices de referencia: {e}")
        return []


def crear_bases_cotizacion_test():
    """Crea bases de cotización de prueba para el período 2017-2027."""
    bases = []
    
    # Crear bases mensuales desde octubre 2017 hasta agosto 2025 (período con revalorización)
    años_meses = [
        (2017, [11, 12]),  # Nov-Dic 2017
        (2018, list(range(1, 13))),  # Todo 2018
        (2019, list(range(1, 13))),  # Todo 2019
        (2020, list(range(1, 13))),  # Todo 2020
        (2021, list(range(1, 13))),  # Todo 2021
        (2022, list(range(1, 13))),  # Todo 2022
        (2023, list(range(1, 13))),  # Todo 2023
        (2024, list(range(1, 13))),  # Todo 2024
        (2025, list(range(1, 9))),   # Ene-Ago 2025
    ]
    
    base_ejemplo = 2000.00  # Base de cotización ejemplo
    
    for año, meses in años_meses:
        for mes in meses:
            bases.append({
                "mes_anyo": f"{mes:02d}/{año}",
                "base": base_ejemplo,
                "empresa": "EMPRESA_TEST",
                "regimen": "GENERAL"
            })
    
    return {"bases": bases}


def test_simulacion_jubilacion_2027():
    """Test principal de simulación para jubilación 11/10/2027."""
    
    print("=" * 80)
    print("🧪 TEST DE SIMULACIÓN - JUBILACIÓN 11/10/2027")
    print("=" * 80)
    
    # 1. Cargar índices de referencia
    print("\n📊 1. CARGANDO ÍNDICES DE REFERENCIA...")
    indices_referencia = cargar_indices_referencia()
    
    if not indices_referencia:
        print("❌ No se pudieron cargar los índices de referencia")
        return False
    
    print(f"✅ Cargados {len(indices_referencia)} índices de referencia")
    
    # 2. Crear bases de cotización de prueba
    print("\n📋 2. CREANDO BASES DE COTIZACIÓN DE PRUEBA...")
    bases_test = crear_bases_cotizacion_test()
    print(f"✅ Creadas {len(bases_test['bases'])} bases de cotización")
    
    # 3. Crear simulador
    print("\n⚙️ 3. INICIALIZANDO SIMULADOR...")
    simulador = SimuladorPeriodos(
        bases_extraidas=bases_test,
        fecha_jubilacion="10/2027",  # Formato mm/AAAA
        regimen_acceso="GENERAL",
        sexo="MASCULINO"
    )
    print(f"✅ Simulador inicializado para jubilación: {simulador.fecha_jubilacion}")
    
    # 4. Mostrar IPCs cargados
    print(f"\n💹 4. IPCs ANUALES DISPONIBLES EN EL SISTEMA:")
    print("-" * 50)
    print(f"{'Año':<8} {'IPC':<10} {'Factor':<12}")
    print("-" * 50)
    
    for año in sorted(simulador.ipc_anual.keys()):
        if 2017 <= año <= 2027:  # Solo mostrar años relevantes
            ipc = simulador.ipc_anual[año]
            factor = 1 + (ipc / 100)
            print(f"{año:<8} {ipc:+6.2f}%{'':<3} {factor:.8f}")
    
    # 5. Calcular índices para diferentes años base y comparar
    print(f"\n🔍 5. COMPARACIÓN DE ÍNDICES CALCULADOS VS REFERENCIA:")
    print("=" * 100)
    print(f"{'Año Base':<10} {'Índice Sistema':<15} {'Índice Ref.':<15} {'Diferencia':<15} {'Estado':<10}")
    print("=" * 100)
    
    coincidencias = 0
    total_comparaciones = 0
    diferencias_significativas = []
    
    # Crear un diccionario de índices de referencia por año para fácil acceso
    indices_ref_por_año = {}
    for item in indices_referencia:
        año = item['año']
        if año not in indices_ref_por_año:
            indices_ref_por_año[año] = []
        indices_ref_por_año[año].append(item['indice_aplicado'])
    
    # Comparar índices por año (usando el promedio si hay múltiples meses)
    for año in range(2017, 2026):  # Años que deberían tener revalorización
        if año in indices_ref_por_año:
            # Calcular índice con nuestro sistema (usando enero como mes base para comparación)
            indice_sistema = simulador._calcular_indice_revalorizacion_ipc(año, 1)
            
            # Usar el promedio de los índices de referencia para ese año
            indices_año_ref = indices_ref_por_año[año]
            indice_referencia = sum(indices_año_ref) / len(indices_año_ref)
            
            # Calcular diferencia
            diferencia = abs(indice_sistema - indice_referencia)
            diferencia_porcentual = (diferencia / indice_referencia) * 100
            
            # Determinar estado
            if diferencia_porcentual < 0.1:  # Menos de 0.1% de diferencia
                estado = "✅ OK"
                coincidencias += 1
            elif diferencia_porcentual < 1.0:  # Menos de 1% de diferencia
                estado = "⚠️ MENOR"
            else:
                estado = "❌ MAYOR"
                diferencias_significativas.append({
                    'año': año,
                    'sistema': indice_sistema,
                    'referencia': indice_referencia,
                    'diferencia_pct': diferencia_porcentual
                })
            
            print(f"{año:<10} {indice_sistema:<15.7f} {indice_referencia:<15.7f} {diferencia:<15.7f} {estado}")
            total_comparaciones += 1
    
    # 6. Mostrar resumen de resultados
    print("=" * 100)
    print(f"\n📈 6. RESUMEN DE RESULTADOS:")
    print(f"   • Total comparaciones: {total_comparaciones}")
    print(f"   • Coincidencias exactas: {coincidencias}")
    print(f"   • Precisión: {(coincidencias/total_comparaciones)*100:.1f}%")
    
    if diferencias_significativas:
        print(f"\n⚠️ DIFERENCIAS SIGNIFICATIVAS (>1%):")
        for diff in diferencias_significativas:
            print(f"   • Año {diff['año']}: {diff['diferencia_pct']:.2f}% de diferencia")
    
    # 7. Mostrar ejemplo detallado de cálculo
    print(f"\n🔍 7. EJEMPLO DETALLADO - CÁLCULO PARA AÑO BASE 2020:")
    año_ejemplo = 2020
    print(f"   Base cotizada en: {año_ejemplo}")
    print(f"   Jubilación en: 2027")
    print(f"   Años de revalorización: {año_ejemplo + 1} hasta {2027 - 2} = {list(range(año_ejemplo + 1, 2027 - 1))}")
    
    print(f"\n   Cálculo paso a paso:")
    indice_acumulado = 1.0
    
    for año in range(año_ejemplo + 1, 2027 - 1):
        if año in simulador.ipc_anual:
            ipc = simulador.ipc_anual[año]
            factor = 1 + (ipc / 100)
            indice_acumulado *= factor
            print(f"   • {año}: IPC {ipc:+.2f}% → Factor {factor:.6f} → Acumulado {indice_acumulado:.7f}")
        else:
            print(f"   • {año}: IPC N/D → Factor 1.000000 → Acumulado {indice_acumulado:.7f}")
    
    indice_sistema_ejemplo = simulador._calcular_indice_revalorizacion_ipc(año_ejemplo, 1)
    print(f"\n   Resultado final del sistema: {indice_sistema_ejemplo:.7f}")
    
    # Buscar índice de referencia para 2020
    indices_2020_ref = [item['indice_aplicado'] for item in indices_referencia if item['año'] == 2020]
    if indices_2020_ref:
        indice_ref_ejemplo = sum(indices_2020_ref) / len(indices_2020_ref)
        print(f"   Índice de referencia (promedio): {indice_ref_ejemplo:.7f}")
        diferencia_ejemplo = abs(indice_sistema_ejemplo - indice_ref_ejemplo)
        print(f"   Diferencia absoluta: {diferencia_ejemplo:.7f}")
    
    # 8. Generar JSON de simulación
    print(f"\n📄 8. GENERANDO JSON DE SIMULACIÓN:")
    indices_simulacion = []
    
    # Generar índices para cada año-mes desde octubre 2017 hasta agosto 2025
    años_meses = [
        (2017, [11, 12]),  # Nov-Dic 2017
        (2018, list(range(1, 13))),  # Todo 2018
        (2019, list(range(1, 13))),  # Todo 2019
        (2020, list(range(1, 13))),  # Todo 2020
        (2021, list(range(1, 13))),  # Todo 2021
        (2022, list(range(1, 13))),  # Todo 2022
        (2023, list(range(1, 13))),  # Todo 2023
        (2024, list(range(1, 13))),  # Todo 2024
        (2025, list(range(1, 9))),   # Ene-Ago 2025
    ]
    
    meses_nombres = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    
    for año, meses in años_meses:
        for mes in meses:
            # Calcular índice para este año y mes específico
            indice_calculado = simulador._calcular_indice_revalorizacion_ipc(año, mes)
            
            indices_simulacion.append({
                "año": año,
                "mes": mes,
                "mes_nombre": meses_nombres[mes],
                "indice_aplicado": indice_calculado
            })
    
    # Crear estructura JSON similar a la de referencia
    json_simulacion = {
        "fecha_jubilacion": "11/10/2027",
        "rango_analisis": {
            "desde": "01/11/2017",
            "hasta": "31/08/2025"
        },
        "total_registros": len(indices_simulacion),
        "indices_revalorizacion": indices_simulacion
    }
    
    # Guardar JSON de simulación
    archivo_simulacion = Path(__file__).parent.parent / 'resultados' / 'indices_simulacion.json'
    try:
        with open(archivo_simulacion, 'w', encoding='utf-8') as f:
            json.dump(json_simulacion, f, indent=2, ensure_ascii=False)
        print(f"   ✅ JSON de simulación guardado en: {archivo_simulacion}")
        print(f"   📊 Total de registros generados: {len(indices_simulacion)}")
    except Exception as e:
        print(f"   ❌ Error guardando JSON de simulación: {e}")
    
    # 9. Conclusiones
    print(f"\n🎯 9. CONCLUSIONES:")
    if coincidencias / total_comparaciones >= 0.8:
        print("   ✅ El sistema calcula correctamente los índices de revalorización")
        print("   ✅ Los resultados coinciden con los datos de referencia de MM_content.txt")
        resultado_test = True
    else:
        print("   ❌ Hay diferencias significativas en los cálculos")
        print("   ❌ Revisar la implementación del cálculo de índices")
        resultado_test = False
    
    print("=" * 80)
    
    return resultado_test


def main():
    """Función principal del test."""
    print("Ejecutando test de simulación para jubilación 11/10/2027...")
    
    try:
        resultado = test_simulacion_jubilacion_2027()
        
        if resultado:
            print("\n🎉 TEST COMPLETADO EXITOSAMENTE")
            return 0
        else:
            print("\n💥 TEST FALLÓ - Revisar implementación")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERROR EN EL TEST: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
