# 📊 Guía para Testear Índices de Revalorización

Esta guía te explica paso a paso cómo validar que el sistema de cálculo de índices de revalorización funciona correctamente comparándolo con datos oficiales.

## 🎯 Objetivo

Verificar que nuestro sistema calcula los índices de revalorización con la misma precisión que los datos oficiales de la Seguridad Social.

## 📋 Proceso Completo

### 1️⃣ **Extraer Índices del PDF Oficial**

Utilizamos el contenido de una simulación oficial de la Seguridad Social para obtener los índices de referencia.

**Archivo necesario:** `MM_content.txt` (contenido extraído del PDF oficial)

**Script:** `procesar_mm_content.py`

```bash
cd tests/indices_rev
python procesar_mm_content.py
```

**¿Qué hace?**
- Lee el archivo `MM_content.txt` 
- Extrae los índices de la sección "PERÍODO CON REVALORIZACIÓN"
- Genera `../resultados/indices_revalorizacion.json` con los datos oficiales

**Resultado:** JSON con índices oficiales organizados por año-mes.

---

### 2️⃣ **Generar Índices con Nuestro Sistema**

Ejecutamos nuestro simulador para calcular los mismos índices usando nuestro algoritmo.

**Script:** `test_simulacion_jubilacion_2027.py`

```bash
cd tests/indices_rev
python test_simulacion_jubilacion_2027.py
```

**¿Qué hace?**
- Simula una jubilación el 11/10/2027 (misma fecha del PDF oficial)
- Calcula índices para cada mes desde noviembre 2017 hasta agosto 2025
- Genera `../resultados/indices_simulacion.json` con nuestros cálculos

**Resultado:** JSON con índices calculados por nuestro sistema.

---

### 3️⃣ **Comparar Ambos Resultados**

Comparamos los índices oficiales vs nuestros cálculos para medir la precisión.

**Script:** `comparar_indices.py`

```bash
cd tests/indices_rev
python comparar_indices.py
```

**¿Qué hace?**
- Carga ambos archivos JSON
- Compara índice por índice con redondeo a 2 decimales
- Calcula estadísticas de precisión
- Genera reporte detallado

**Resultados generados:**
- `../resultados/reporte_comparacion_indices.txt` - Reporte completo
- `../resultados/comparacion_indices.csv` - Datos para análisis

---

## 📊 Interpretación de Resultados

### Métricas de Precisión

- **Coincidencias exactas**: Índices idénticos (redondeados a 2 decimales)
- **Diferencias menores (<1%)**: Diferencias aceptables
- **Diferencias mayores (≥1%)**: Requieren revisión
- **Precisión general**: % de coincidencias + diferencias menores

### Estados de Comparación

| Estado | Significado | Acción |
|--------|-------------|---------|
| ✅ IGUAL | Índices idénticos | Perfecto |
| ⚠️ MENOR | Diferencia < 1% | Aceptable |
| ❌ MAYOR | Diferencia ≥ 1% | Revisar |

### Objetivos de Calidad

- **Excelente**: Precisión ≥ 90%
- **Bueno**: Precisión ≥ 70%
- **Requiere mejora**: Precisión < 70%

---

## 🔧 Solución de Problemas

### Error: "No se encontró el archivo"

```bash
# Verificar que estás en la carpeta correcta
cd tests/indices_rev
ls -la  # En Windows: dir

# Verificar que existe MM_content.txt
cat MM_content.txt | head -10
```

### Error: "División por cero"

Significa que no se están cargando los datos de IPC. Verificar:

```bash
# Comprobar archivo de configuración IPC
cat ../../core/config/config_files/ipc_anual.yaml
```

### Precisión baja

Si la precisión es menor al 70%:

1. **Revisar datos de IPC**: ¿Están actualizados los datos históricos?
2. **Verificar fechas**: ¿La fecha de jubilación coincide con el PDF?
3. **Analizar diferencias**: ¿Hay un patrón en los errores?

---

## 📁 Estructura de Archivos

```
tests/indices_rev/
├── README.md                     # Esta guía
├── MM_content.txt               # Contenido del PDF oficial
├── procesar_mm_content.py       # Extrae índices del PDF
├── test_simulacion_jubilacion_2027.py  # Calcula con nuestro sistema
├── comparar_indices.py          # Compara resultados
└── mejorar_precision_indices.py # Herramientas de análisis

tests/resultados/
├── indices_revalorizacion.json  # Índices oficiales (del PDF)
├── indices_simulacion.json      # Índices calculados (nuestro sistema)
├── reporte_comparacion_indices.txt  # Reporte detallado
└── comparacion_indices.csv      # Datos para análisis
```

---

## 🚀 Ejecución Rápida

Para ejecutar todo el proceso de una vez:

```bash
cd tests/indices_rev

# Paso 1: Extraer del PDF
python procesar_mm_content.py

# Paso 2: Calcular con nuestro sistema
python test_simulacion_jubilacion_2027.py

# Paso 3: Comparar resultados
python comparar_indices.py

# Ver resultados
cat ../resultados/reporte_comparacion_indices.txt
```

---

## 📈 Ejemplo de Resultado Exitoso

```
📊 RESUMEN EJECUTIVO
--------------------------------------------------
Total de comparaciones realizadas: 94
Coincidencias exactas: 30 (31.9%)
Diferencias menores (<1%): 33 (35.1%)
Diferencias mayores (≥1%): 31 (33.0%)
PRECISIÓN GENERAL: 67.0%

🎯 CONCLUSIONES
✅ Buena concordancia con algunas diferencias menores
⚠️ Revisar casos con diferencias mayores al 1%
```

---

## 🔄 Mejora Continua

1. **Analizar patrones** en las diferencias mayores
2. **Ajustar algoritmo** si es necesario
3. **Actualizar datos de IPC** periódicamente
4. **Validar** con nuevos casos oficiales

---

## ❓ Preguntas Frecuentes

**P: ¿Qué precisión es aceptable?**
R: Una precisión del 70% o superior es buena. Más del 90% es excelente.

**P: ¿Por qué hay diferencias?**
R: Pequeñas diferencias son normales debido a:
- Redondeos en los cálculos
- Diferencias en los datos de IPC utilizados
- Métodos de distribución mensual del IPC anual

**P: ¿Cómo mejorar la precisión?**
R: 
- Usar datos de IPC más precisos (mensuales vs anuales)
- Ajustar el algoritmo de cálculo
- Verificar la normativa aplicable

---

*Última actualización: Octubre 2025*
