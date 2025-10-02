#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mejorar la precisión de los índices de revalorización.
Analiza las diferencias y propone mejoras al sistema de cálculo.
"""

import json
import sys
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from services.simulator import SimuladorPeriodos


def analizar_patron_diferencias():
    """Analiza el patrón de diferencias para identificar problemas."""
    
    print("=" * 80)
    print("🔍 ANÁLISIS DE PATRONES EN LAS DIFERENCIAS")
    print("=" * 80)
    
    # Cargar datos de referencia
    archivo_referencia = Path(__file__).parent.parent / 'resultados' / 'indices_revalorizacion.json'
    with open(archivo_referencia, 'r', encoding='utf-8') as f:
        datos_ref = json.load(f)
    
    # Analizar patrones por año
    diferencias_por_año = {}
    
    for item in datos_ref['indices_revalorizacion']:
        año = item['año']
        if año not in diferencias_por_año:
            diferencias_por_año[año] = []
        diferencias_por_año[año].append(item['indice_aplicado'])
    
    print("\n📊 ANÁLISIS POR AÑO:")
    print(f"{'Año':<6} {'Min Índice':<12} {'Max Índice':<12} {'Promedio':<12} {'Variación':<12}")
    print("-" * 60)
    
    for año in sorted(diferencias_por_año.keys()):
        indices = diferencias_por_año[año]
        min_idx = min(indices)
        max_idx = max(indices)
        promedio = sum(indices) / len(indices)
        variacion = max_idx - min_idx
        
        print(f"{año:<6} {min_idx:<12.7f} {max_idx:<12.7f} {promedio:<12.7f} {variacion:<12.7f}")
    
    return diferencias_por_año


def crear_ipc_mensual_mejorado():
    """Crea un sistema de IPC mensual más preciso basado en los datos del PDF."""
    
    print("\n🔧 CREANDO SISTEMA DE IPC MENSUAL MEJORADO")
    print("-" * 50)
    
    # Cargar datos de referencia
    archivo_referencia = Path(__file__).parent.parent / 'resultados' / 'indices_revalorizacion.json'
    with open(archivo_referencia, 'r', encoding='utf-8') as f:
        datos_ref = json.load(f)
    
    # Cargar IPC anual actual
    archivo_ipc = root_dir / 'core' / 'config' / 'config_files' / 'ipc_anual.yaml'
    with open(archivo_ipc, 'r', encoding='utf-8') as f:
        ipc_data = yaml.safe_load(f)
    
    ipc_anual = ipc_data['ipc_anual']
    
    # Calcular IPCs mensuales implícitos desde los índices del PDF
    print("\n📈 CALCULANDO IPCs MENSUALES IMPLÍCITOS:")
    
    # Agrupar por año-mes para análisis
    indices_por_periodo = {}
    for item in datos_ref['indices_revalorizacion']:
        clave = f"{item['año']}-{item['mes']:02d}"
        indices_por_periodo[clave] = item['indice_aplicado']
    
    # Calcular IPCs mensuales implícitos
    ipc_mensual_calculado = {}
    
    # Para cada año, calcular la variación mensual implícita
    for año in range(2018, 2026):  # Años con datos suficientes
        if año in ipc_anual:
            ipc_anual_valor = ipc_anual[año]
            factor_anual = 1 + (ipc_anual_valor / 100)
            
            # Distribuir el IPC anual en 12 meses
            factor_mensual = factor_anual ** (1/12)
            ipc_mensual = (factor_mensual - 1) * 100
            
            for mes in range(1, 13):
                clave = f"{año}-{mes:02d}"
                ipc_mensual_calculado[clave] = ipc_mensual
    
    return ipc_mensual_calculado, indices_por_periodo


def calcular_indice_mejorado(año_base, mes_base, fecha_jubilacion, ipc_mensual):
    """
    Calcula el índice de revalorización con precisión mensual.
    
    Args:
        año_base: Año de la base de cotización
        mes_base: Mes de la base de cotización  
        fecha_jubilacion: Fecha de jubilación
        ipc_mensual: Diccionario con IPCs mensuales
    
    Returns:
        float: Índice de revalorización calculado
    """
    
    # Fecha de inicio (mes siguiente a la cotización)
    if mes_base == 12:
        fecha_inicio = datetime(año_base + 1, 1, 1)
    else:
        fecha_inicio = datetime(año_base, mes_base + 1, 1)
    
    # Fecha límite (24 meses antes de jubilación)
    fecha_limite = fecha_jubilacion - relativedelta(months=24)
    
    # Si la fecha de inicio es posterior al límite, no hay revalorización
    if fecha_inicio >= fecha_limite:
        return 1.0
    
    # Calcular índice acumulativo mes a mes
    indice_acumulado = 1.0
    fecha_actual = fecha_inicio
    
    while fecha_actual < fecha_limite:
        clave_mes = f"{fecha_actual.year}-{fecha_actual.month:02d}"
        
        if clave_mes in ipc_mensual:
            ipc_mes = ipc_mensual[clave_mes]
            factor_mes = 1 + (ipc_mes / 100)
            indice_acumulado *= factor_mes
        else:
            # Si no hay datos, usar IPC anual distribuido
            # Cargar IPC anual como fallback
            archivo_ipc = root_dir / 'core' / 'config' / 'config_files' / 'ipc_anual.yaml'
            with open(archivo_ipc, 'r', encoding='utf-8') as f:
                ipc_data = yaml.safe_load(f)
            
            ipc_anual = ipc_data['ipc_anual']
            
            if fecha_actual.year in ipc_anual:
                ipc_anual_valor = ipc_anual[fecha_actual.year]
                factor_anual = 1 + (ipc_anual_valor / 100)
                factor_mensual = factor_anual ** (1/12)
                indice_acumulado *= factor_mensual
        
        # Avanzar al siguiente mes
        fecha_actual += relativedelta(months=1)
    
    return indice_acumulado


def generar_indices_mejorados():
    """Genera nuevos índices con el sistema mejorado."""
    
    print("\n🚀 GENERANDO ÍNDICES CON SISTEMA MEJORADO")
    print("-" * 50)
    
    # Crear sistema de IPC mensual
    ipc_mensual, indices_referencia = crear_ipc_mensual_mejorado()
    
    # Fecha de jubilación
    fecha_jubilacion = datetime(2027, 10, 11)
    
    # Generar nuevos índices
    indices_mejorados = []
    
    # Períodos a calcular
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
    
    print(f"{'Período':<10} {'Índice Original':<15} {'Índice Mejorado':<15} {'Diferencia':<12}")
    print("-" * 60)
    
    for año, meses in años_meses:
        for mes in meses:
            # Calcular índice mejorado
            indice_mejorado = calcular_indice_mejorado(año, mes, fecha_jubilacion, ipc_mensual)
            
            # Obtener índice de referencia
            clave_ref = f"{año}-{mes:02d}"
            indice_referencia = indices_referencia.get(clave_ref, 0)
            
            # Calcular diferencia
            diferencia = abs(indice_mejorado - indice_referencia) if indice_referencia > 0 else 0
            
            print(f"{año}-{mes:02d}   {indice_referencia:<15.7f} {indice_mejorado:<15.7f} {diferencia:<12.7f}")
            
            indices_mejorados.append({
                "año": año,
                "mes": mes,
                "mes_nombre": meses_nombres[mes],
                "indice_aplicado": indice_mejorado
            })
    
    # Guardar índices mejorados
    json_mejorado = {
        "fecha_jubilacion": "11/10/2027",
        "rango_analisis": {
            "desde": "01/11/2017",
            "hasta": "31/08/2025"
        },
        "total_registros": len(indices_mejorados),
        "metodo_calculo": "sistema_ipc_mensual_mejorado",
        "mejoras_aplicadas": [
            "Cálculo mensual en lugar de anual",
            "Distribución uniforme del IPC anual",
            "Fecha límite precisa (24 meses antes)",
            "Cálculo acumulativo mes a mes"
        ],
        "indices_revalorizacion": indices_mejorados
    }
    
    # Guardar archivo
    archivo_mejorado = Path(__file__).parent.parent / 'resultados' / 'indices_simulacion_mejorado.json'
    with open(archivo_mejorado, 'w', encoding='utf-8') as f:
        json.dump(json_mejorado, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Índices mejorados guardados en: {archivo_mejorado}")
    
    return indices_mejorados


def proponer_mejoras_sistema():
    """Propone mejoras específicas al sistema actual."""
    
    print("\n💡 PROPUESTAS DE MEJORA AL SISTEMA")
    print("=" * 50)
    
    mejoras = [
        {
            "titulo": "1. Implementar cálculo mensual",
            "descripcion": "Cambiar de cálculo anual a mensual para mayor precisión",
            "impacto": "Alto - Reduce diferencias significativamente"
        },
        {
            "titulo": "2. Mejorar distribución de IPC",
            "descripcion": "Distribuir el IPC anual uniformemente en 12 meses",
            "impacto": "Medio - Mejora la granularidad temporal"
        },
        {
            "titulo": "3. Fecha límite precisa",
            "descripcion": "Usar fecha exacta (24 meses antes) en lugar de años completos",
            "impacto": "Alto - Coincide con la normativa real"
        },
        {
            "titulo": "4. Validación con datos reales",
            "descripcion": "Comparar sistemáticamente con casos reales del PDF",
            "impacto": "Alto - Garantiza precisión del sistema"
        },
        {
            "titulo": "5. IPC mensual histórico",
            "descripcion": "Incorporar datos de IPC mensual del INE si están disponibles",
            "impacto": "Muy Alto - Máxima precisión posible"
        }
    ]
    
    for mejora in mejoras:
        print(f"\n{mejora['titulo']}")
        print(f"   Descripción: {mejora['descripcion']}")
        print(f"   Impacto: {mejora['impacto']}")
    
    return mejoras


def main():
    """Función principal."""
    print("Analizando y mejorando la precisión de los índices de revalorización...")
    
    try:
        # 1. Analizar patrones de diferencias
        diferencias_por_año = analizar_patron_diferencias()
        
        # 2. Generar índices mejorados
        indices_mejorados = generar_indices_mejorados()
        
        # 3. Proponer mejoras al sistema
        mejoras = proponer_mejoras_sistema()
        
        print("\n🎉 ANÁLISIS Y MEJORAS COMPLETADAS")
        print("\nPróximos pasos:")
        print("1. Revisar el archivo 'indices_simulacion_mejorado.json'")
        print("2. Ejecutar comparación con el nuevo archivo")
        print("3. Implementar las mejoras propuestas en el sistema principal")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 ERROR EN EL ANÁLISIS: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
