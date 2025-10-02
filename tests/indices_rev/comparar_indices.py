#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar los índices de revalorización entre:
- indices_revalorizacion.json (extraído de MM_content.txt)
- indices_simulacion.json (calculado por el sistema)

Genera una tabla de comparación detallada con diferencias.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def cargar_json(archivo_path):
    """Carga un archivo JSON."""
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {archivo_path}")
        return None
    except Exception as e:
        print(f"❌ Error cargando {archivo_path}: {e}")
        return None


def crear_clave_periodo(año, mes):
    """Crea una clave única para año-mes."""
    return f"{año}-{mes:02d}"


def generar_tabla_comparacion():
    """Genera la tabla de comparación entre los dos JSONs."""
    
    print("=" * 100)
    print("📊 COMPARACIÓN DE ÍNDICES DE REVALORIZACIÓN")
    print("=" * 100)
    
    # Rutas de los archivos
    carpeta_resultados = Path(__file__).parent.parent / 'resultados'
    archivo_pdf = carpeta_resultados / 'indices_revalorizacion.json'
    archivo_simulacion = carpeta_resultados / 'indices_simulacion.json'
    
    # Cargar datos
    print("\n📂 1. CARGANDO ARCHIVOS...")
    datos_pdf = cargar_json(archivo_pdf)
    datos_simulacion = cargar_json(archivo_simulacion)
    
    if not datos_pdf or not datos_simulacion:
        print("❌ No se pudieron cargar los archivos necesarios")
        return False
    
    print(f"✅ Cargado indices_revalorizacion.json: {datos_pdf['total_registros']} registros")
    print(f"✅ Cargado indices_simulacion.json: {datos_simulacion['total_registros']} registros")
    
    # Crear diccionarios indexados por año-mes para fácil comparación
    indices_pdf = {}
    for item in datos_pdf['indices_revalorizacion']:
        clave = crear_clave_periodo(item['año'], item['mes'])
        indices_pdf[clave] = item['indice_aplicado']
    
    indices_simulacion = {}
    for item in datos_simulacion['indices_revalorizacion']:
        clave = crear_clave_periodo(item['año'], item['mes'])
        indices_simulacion[clave] = item['indice_aplicado']
    
    # Obtener todos los períodos únicos
    todos_periodos = set(indices_pdf.keys()) | set(indices_simulacion.keys())
    periodos_ordenados = sorted(todos_periodos)
    
    print(f"\n📋 2. ANÁLISIS DE PERÍODOS:")
    print(f"   • Períodos en PDF: {len(indices_pdf)}")
    print(f"   • Períodos en Simulación: {len(indices_simulacion)}")
    print(f"   • Períodos únicos totales: {len(todos_periodos)}")
    
    # Generar tabla de comparación
    print(f"\n📊 3. TABLA DE COMPARACIÓN:")
    print("=" * 100)
    print(f"{'Año':<6} {'Mes':<4} {'Mes Nom':<8} {'I_PDF':<15} {'I_Simulación':<15} {'Diferencia':<15} {'Dif %':<10} {'Estado':<10}")
    print("=" * 100)
    
    # Mapeo de números de mes a nombres
    meses_nombres = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    
    # Estadísticas
    total_comparaciones = 0
    coincidencias_exactas = 0
    diferencias_menores = 0  # < 1%
    diferencias_mayores = 0  # >= 1%
    solo_en_pdf = 0
    solo_en_simulacion = 0
    
    comparaciones_detalle = []
    
    for periodo in periodos_ordenados:
        año, mes = periodo.split('-')
        año = int(año)
        mes = int(mes)
        mes_nombre = meses_nombres.get(mes, f"M{mes}")
        
        i_pdf = indices_pdf.get(periodo)
        i_simulacion = indices_simulacion.get(periodo)
        
        if i_pdf is not None and i_simulacion is not None:
            # Ambos tienen el índice
            # Redondear índices a 2 decimales para comparación
            i_pdf_redondeado = round(i_pdf, 2)
            i_simulacion_redondeado = round(i_simulacion, 2)
            
            # Calcular diferencia con valores redondeados
            diferencia = abs(i_pdf_redondeado - i_simulacion_redondeado)
            diferencia_porcentual = (diferencia / i_pdf_redondeado) * 100 if i_pdf_redondeado != 0 else 0
            
            if diferencia == 0:  # Iguales con 2 decimales
                estado = "✅ IGUAL"
                coincidencias_exactas += 1
            elif diferencia_porcentual < 1.0:
                estado = "⚠️ MENOR"
                diferencias_menores += 1
            else:
                estado = "❌ MAYOR"
                diferencias_mayores += 1
            
            print(f"{año:<6} {mes:<4} {mes_nombre:<8} {i_pdf_redondeado:<15.2f} {i_simulacion_redondeado:<15.2f} {diferencia:<15.2f} {diferencia_porcentual:<10.3f} {estado}")
            
            comparaciones_detalle.append({
                'año': año,
                'mes': mes,
                'mes_nombre': mes_nombre,
                'i_pdf': i_pdf_redondeado,
                'i_simulacion': i_simulacion_redondeado,
                'diferencia': diferencia,
                'diferencia_pct': diferencia_porcentual,
                'estado': estado
            })
            
            total_comparaciones += 1
            
        elif i_pdf is not None:
            # Solo en PDF
            print(f"{año:<6} {mes:<4} {mes_nombre:<8} {i_pdf:<15.7f} {'N/D':<15} {'N/D':<15} {'N/D':<10} {'📄 SOLO PDF'}")
            solo_en_pdf += 1
            
        elif i_simulacion is not None:
            # Solo en simulación
            print(f"{año:<6} {mes:<4} {mes_nombre:<8} {'N/D':<15} {i_simulacion:<15.7f} {'N/D':<15} {'N/D':<10} {'🔧 SOLO SIM'}")
            solo_en_simulacion += 1
    
    print("=" * 100)
    
    # Resumen estadístico
    print(f"\n📈 4. RESUMEN ESTADÍSTICO:")
    print(f"   • Total de comparaciones: {total_comparaciones}")
    print(f"   • Coincidencias exactas: {coincidencias_exactas} ({(coincidencias_exactas/total_comparaciones)*100:.1f}%)")
    print(f"   • Diferencias menores (<1%): {diferencias_menores} ({(diferencias_menores/total_comparaciones)*100:.1f}%)")
    print(f"   • Diferencias mayores (≥1%): {diferencias_mayores} ({(diferencias_mayores/total_comparaciones)*100:.1f}%)")
    print(f"   • Solo en PDF: {solo_en_pdf}")
    print(f"   • Solo en Simulación: {solo_en_simulacion}")
    
    # Precisión general
    precision_total = ((coincidencias_exactas + diferencias_menores) / total_comparaciones) * 100 if total_comparaciones > 0 else 0
    print(f"\n🎯 PRECISIÓN GENERAL: {precision_total:.1f}%")
    
    # Análisis de las mayores diferencias
    if diferencias_mayores > 0:
        print(f"\n⚠️ 5. MAYORES DIFERENCIAS (≥1%):")
        diferencias_significativas = [c for c in comparaciones_detalle if c['diferencia_pct'] >= 1.0]
        diferencias_significativas.sort(key=lambda x: x['diferencia_pct'], reverse=True)
        
        print(f"{'Período':<10} {'Dif %':<10} {'I_PDF':<15} {'I_Simulación':<15}")
        print("-" * 55)
        
        for diff in diferencias_significativas[:10]:  # Top 10 diferencias
            periodo_str = f"{diff['año']}-{diff['mes']:02d}"
            print(f"{periodo_str:<10} {diff['diferencia_pct']:<10.3f} {diff['i_pdf']:<15.2f} {diff['i_simulacion']:<15.2f}")
    
    # Guardar tabla en archivo TXT formateado
    print(f"\n💾 6. GUARDANDO REPORTE COMPLETO...")
    archivo_txt = carpeta_resultados / 'reporte_comparacion_indices.txt'
    archivo_csv = carpeta_resultados / 'comparacion_indices.csv'
    
    try:
        # Generar reporte TXT formateado
        with open(archivo_txt, 'w', encoding='utf-8') as f:
            # Encabezado del reporte
            f.write("=" * 120 + "\n")
            f.write("                    REPORTE DE COMPARACIÓN DE ÍNDICES DE REVALORIZACIÓN\n")
            f.write("=" * 120 + "\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Archivo PDF (referencia): indices_revalorizacion.json ({datos_pdf['total_registros']} registros)\n")
            f.write(f"Archivo Simulación: indices_simulacion.json ({datos_simulacion['total_registros']} registros)\n")
            f.write("=" * 120 + "\n\n")
            
            # Resumen ejecutivo
            f.write("📊 RESUMEN EJECUTIVO\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total de comparaciones realizadas: {total_comparaciones}\n")
            f.write(f"Coincidencias exactas: {coincidencias_exactas} ({(coincidencias_exactas/total_comparaciones)*100:.1f}%)\n")
            f.write(f"Diferencias menores (<1%): {diferencias_menores} ({(diferencias_menores/total_comparaciones)*100:.1f}%)\n")
            f.write(f"Diferencias mayores (≥1%): {diferencias_mayores} ({(diferencias_mayores/total_comparaciones)*100:.1f}%)\n")
            f.write(f"Solo en PDF: {solo_en_pdf}\n")
            f.write(f"Solo en Simulación: {solo_en_simulacion}\n")
            f.write(f"PRECISIÓN GENERAL: {precision_total:.1f}%\n\n")
            
            # Tabla detallada
            f.write("📋 TABLA DETALLADA DE COMPARACIÓN\n")
            f.write("=" * 120 + "\n")
            f.write(f"{'Año':<6} {'Mes':<4} {'Nombre':<8} {'Índice PDF':<15} {'Índice Simulación':<18} {'Diferencia':<15} {'Dif %':<10} {'Estado':<12}\n")
            f.write("=" * 120 + "\n")
            
            for comp in comparaciones_detalle:
                estado_limpio = comp['estado'].replace('✅ ', '').replace('⚠️ ', '').replace('❌ ', '')
                f.write(f"{comp['año']:<6} {comp['mes']:<4} {comp['mes_nombre']:<8} "
                       f"{comp['i_pdf']:<15.2f} {comp['i_simulacion']:<18.2f} "
                       f"{comp['diferencia']:<15.2f} {comp['diferencia_pct']:<10.3f} {estado_limpio:<12}\n")
            
            f.write("=" * 120 + "\n\n")
            
            # Análisis de mayores diferencias
            if diferencias_mayores > 0:
                f.write("⚠️ ANÁLISIS DE MAYORES DIFERENCIAS (≥1%)\n")
                f.write("-" * 60 + "\n")
                diferencias_significativas = [c for c in comparaciones_detalle if c['diferencia_pct'] >= 1.0]
                diferencias_significativas.sort(key=lambda x: x['diferencia_pct'], reverse=True)
                
                f.write(f"{'Período':<12} {'Dif %':<10} {'Índice PDF':<15} {'Índice Simulación':<18}\n")
                f.write("-" * 60 + "\n")
                
                for diff in diferencias_significativas:
                    periodo_str = f"{diff['año']}-{diff['mes']:02d} ({diff['mes_nombre']})"
                    f.write(f"{periodo_str:<12} {diff['diferencia_pct']:<10.3f} "
                           f"{diff['i_pdf']:<15.2f} {diff['i_simulacion']:<18.2f}\n")
                f.write("\n")
            
            # Conclusiones y recomendaciones
            f.write("🎯 CONCLUSIONES Y RECOMENDACIONES\n")
            f.write("-" * 50 + "\n")
            
            if precision_total >= 90:
                f.write("✅ RESULTADO: EXCELENTE\n")
                f.write("• El sistema de simulación calcula correctamente los índices de revalorización\n")
                f.write("• Hay una excelente concordancia entre los datos del PDF y la simulación\n")
                f.write("• No se requieren ajustes significativos\n")
            elif precision_total >= 70:
                f.write("⚠️ RESULTADO: BUENO CON OBSERVACIONES\n")
                f.write("• El sistema tiene una buena precisión general\n")
                f.write("• Se detectaron algunas diferencias menores que requieren revisión\n")
                f.write("• Recomendación: Revisar los casos con diferencias mayores al 1%\n")
            else:
                f.write("❌ RESULTADO: REQUIERE REVISIÓN\n")
                f.write("• Se detectaron diferencias significativas en los cálculos\n")
                f.write("• Es necesario revisar la implementación del algoritmo de revalorización\n")
                f.write("• Verificar los datos de IPC utilizados en el sistema\n")
            
            f.write("\n" + "=" * 120 + "\n")
            f.write("Fin del reporte\n")
        
        # También guardar CSV para análisis posterior
        with open(archivo_csv, 'w', encoding='utf-8') as f:
            # Encabezados
            f.write("Año,Mes,Mes_Nombre,I_PDF,I_Simulacion,Diferencia,Diferencia_Pct,Estado\n")
            
            # Datos
            for comp in comparaciones_detalle:
                f.write(f"{comp['año']},{comp['mes']},{comp['mes_nombre']},{comp['i_pdf']:.7f},"
                       f"{comp['i_simulacion']:.7f},{comp['diferencia']:.7f},{comp['diferencia_pct']:.3f},"
                       f"{comp['estado'].replace('✅ ', '').replace('⚠️ ', '').replace('❌ ', '')}\n")
        
        print(f"✅ Reporte completo guardado en: {archivo_txt}")
        print(f"✅ Datos CSV guardados en: {archivo_csv}")
        
    except Exception as e:
        print(f"❌ Error guardando archivos: {e}")
    
    # Conclusiones
    print(f"\n🎯 7. CONCLUSIONES:")
    if precision_total >= 90:
        print("   ✅ Excelente concordancia entre PDF y simulación")
        print("   ✅ El sistema calcula correctamente los índices")
        resultado = True
    elif precision_total >= 70:
        print("   ⚠️ Buena concordancia con algunas diferencias menores")
        print("   ⚠️ Revisar casos con diferencias mayores")
        resultado = True
    else:
        print("   ❌ Diferencias significativas detectadas")
        print("   ❌ Revisar la implementación del cálculo de índices")
        resultado = False
    
    print("=" * 100)
    
    return resultado


def main():
    """Función principal."""
    print("Comparando índices de revalorización...")
    
    try:
        resultado = generar_tabla_comparacion()
        
        if resultado:
            print("\n🎉 COMPARACIÓN COMPLETADA EXITOSAMENTE")
            return 0
        else:
            print("\n💥 SE DETECTARON DIFERENCIAS SIGNIFICATIVAS")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERROR EN LA COMPARACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
