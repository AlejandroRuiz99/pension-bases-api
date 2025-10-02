#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para procesar MM_content.txt y generar JSON con datos de revalorización
desde la fecha de jubilación hasta 10 años atrás.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def extraer_fecha_jubilacion(contenido):
    """Extrae la fecha de jubilación del contenido."""
    patron = r'Fecha jubilación:\s*(\d{2}/\d{2}/\d{4})'
    match = re.search(patron, contenido)
    if match:
        fecha_str = match.group(1)
        return datetime.strptime(fecha_str, '%d/%m/%Y')
    return None

def procesar_periodo_revalorizacion(contenido):
    """Procesa la sección de PERÍODO CON REVALORIZACIÓN."""
    datos = []
    
    # Buscar la sección de revalorización
    inicio_seccion = contenido.find("PERÍODO CON REVALORIZACIÓN")
    if inicio_seccion == -1:
        print("No se encontró la sección de PERÍODO CON REVALORIZACIÓN")
        return datos
    
    # Extraer las líneas de datos de revalorización
    lineas = contenido[inicio_seccion:].split('\n')
    
    # Patrón para extraer datos: Mes - Año BASE Índice BaseReval
    patron = r'([A-Za-z]{3})\s*-\s*(\d{2})\s+[\d,\.]+\s+([\d,\.]+)\s+[\d,\.]+'
    
    for linea in lineas:
        matches = re.findall(patron, linea)
        for match in matches:
            mes_abrev, año, indice = match
            
            # Convertir mes abreviado a número
            meses = {
                'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
            }
            
            mes_num = meses.get(mes_abrev)
            if mes_num:
                año_completo = 2000 + int(año)
                indice_float = float(indice.replace(',', '.'))
                
                datos.append({
                    'año': año_completo,
                    'mes': mes_num,
                    'mes_nombre': mes_abrev,
                    'indice_aplicado': indice_float
                })
    
    return datos

def filtrar_por_rango_fechas(datos, fecha_jubilacion):
    """Filtra los datos para incluir solo desde 10 años antes de la jubilación hasta la jubilación."""
    if not fecha_jubilacion:
        return datos
    
    fecha_inicio = fecha_jubilacion - timedelta(days=365*10)  # 10 años atrás
    
    datos_filtrados = []
    for dato in datos:
        fecha_dato = datetime(dato['año'], dato['mes'], 1)
        if fecha_inicio <= fecha_dato <= fecha_jubilacion:
            datos_filtrados.append(dato)
    
    return datos_filtrados

def main():
    """Función principal del script."""
    # Rutas de archivos
    archivo_entrada = Path(__file__).parent / 'MM_content.txt'
    carpeta_resultados = Path(__file__).parent.parent / 'resultados'
    archivo_salida = carpeta_resultados / 'indices_revalorizacion.json'
    
    # Crear carpeta de resultados si no existe
    carpeta_resultados.mkdir(exist_ok=True)
    
    # Leer el archivo de entrada
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_entrada}")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return
    
    # Extraer fecha de jubilación
    fecha_jubilacion = extraer_fecha_jubilacion(contenido)
    if fecha_jubilacion:
        print(f"Fecha de jubilación encontrada: {fecha_jubilacion.strftime('%d/%m/%Y')}")
    else:
        print("No se pudo extraer la fecha de jubilación")
        return
    
    # Procesar datos de revalorización
    datos_revalorizacion = procesar_periodo_revalorizacion(contenido)
    print(f"Se encontraron {len(datos_revalorizacion)} registros de revalorización")
    
    # Filtrar por rango de fechas (10 años atrás hasta jubilación)
    datos_filtrados = filtrar_por_rango_fechas(datos_revalorizacion, fecha_jubilacion)
    print(f"Se filtraron {len(datos_filtrados)} registros en el rango de fechas")
    
    # Ordenar por año y mes
    datos_filtrados.sort(key=lambda x: (x['año'], x['mes']))
    
    # Crear estructura JSON final
    resultado = {
        'fecha_jubilacion': fecha_jubilacion.strftime('%d/%m/%Y'),
        'rango_analisis': {
            'desde': (fecha_jubilacion - timedelta(days=365*10)).strftime('%d/%m/%Y'),
            'hasta': fecha_jubilacion.strftime('%d/%m/%Y')
        },
        'total_registros': len(datos_filtrados),
        'indices_revalorizacion': datos_filtrados
    }
    
    # Guardar resultado en JSON
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        print(f"Resultado guardado en: {archivo_salida}")
        
        # Mostrar algunos ejemplos
        print("\nPrimeros 5 registros:")
        for i, dato in enumerate(datos_filtrados[:5]):
            print(f"  {dato['año']}-{dato['mes']:02d} ({dato['mes_nombre']}): {dato['indice_aplicado']}")
        
        if len(datos_filtrados) > 5:
            print(f"\n... y {len(datos_filtrados) - 5} registros más")
            
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

if __name__ == "__main__":
    main()
