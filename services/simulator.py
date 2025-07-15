"""
Simulador de períodos para el cálculo de bases de cotización.
Maneja la separación de bases por períodos según la normativa vigente 2025.
"""

import json
from datetime import datetime
from typing import Dict, List
from dateutil.relativedelta import relativedelta
from models.bases_cotizacion import BaseCotizacion, BasesCotizacion
from core.config.config_manager import config


class SimuladorPeriodos:
    """
    Clase para simular y separar bases de cotización por períodos
    según la normativa vigente 2025.
    """
    
    def __init__(
        self,
        bases_extraidas: Dict,
        fecha_jubilacion: str,
        regimen_acceso: str = "GENERAL",
        sexo: str = "MASCULINO"
    ):
        """
        Inicializa el simulador de períodos.
        
        Args:
            bases_extraidas: Diccionario con las bases extraídas del JSON
            fecha_jubilacion: Fecha de jubilación en formato "mm/AAAA"
            regimen_acceso: Régimen de acceso ("GENERAL" o "AUTONOMO")
            sexo: Sexo del cotizante ("MASCULINO" o "FEMENINO")
        """
        self.regimen_acceso = regimen_acceso.upper()
        self.sexo = sexo.upper()
        
        # Inicializar contador de lagunas
        self.contador_lagunas = 0
        
        # Para hombres: determinar si cumplen condiciones especiales (por implementar)
        # Por ahora, todos los hombres se consideran sin condiciones especiales
        self.cumple_condiciones_hombre = False
        
        # Validar y procesar datos de entrada
        self._validar_datos_entrada(bases_extraidas, fecha_jubilacion)
        
        # Cargar configuraciones (antes de procesar bases para pluriactividad)
        self.parametros_computo = config.cargar_parametros_computo()
        self.indices_revalorizacion = config.cargar_indices_revalorizacion()
        self.topes_cotizacion = config.cargar_topes_cotizacion()
        
        # Procesar fecha de jubilación
        self.fecha_jubilacion = self._procesar_fecha_jubilacion(fecha_jubilacion)
        
        # Cargar bases de cotización (después de cargar configuraciones)
        self.bases = self._procesar_bases_extraidas(bases_extraidas)
        
        # Obtener parámetros de cómputo para el año de jubilación
        self.parametros_año_jubilacion = self.get_parametros_computo()
        
        # Bases procesadas
        self.bases_procesadas = []
        
    def _validar_datos_entrada(self, bases_extraidas: Dict, fecha_jubilacion: str):
        """
        Valida los datos de entrada.
        
        Args:
            bases_extraidas: Diccionario con las bases extraídas
            fecha_jubilacion: Fecha de jubilación
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        if not isinstance(bases_extraidas, dict):
            raise ValueError("bases_extraidas debe ser un diccionario")
            
        if "bases" not in bases_extraidas:
            raise ValueError("bases_extraidas debe contener la clave 'bases'")
            
        if not isinstance(bases_extraidas["bases"], list):
            raise ValueError("bases debe ser una lista")
            
        if not bases_extraidas["bases"]:
            raise ValueError("La lista de bases no puede estar vacía")
            
        # Validar formato de fecha
        try:
            datetime.strptime(fecha_jubilacion, "%m/%Y")
        except ValueError:
            raise ValueError(f"Formato de fecha inválido: {fecha_jubilacion}. Use mm/AAAA")
            
        # Validar régimen
        if self.regimen_acceso not in ["GENERAL", "AUTONOMO"]:
            raise ValueError(f"Régimen inválido: {self.regimen_acceso}")
                   
    def _procesar_bases_extraidas(self, bases_extraidas: Dict) -> List[BaseCotizacion]:
        """
        Procesa las bases extraídas del JSON, manejando pluriactividad.
        
        Args:
            bases_extraidas: Diccionario con las bases extraídas
            
        Returns:
            Lista de objetos BaseCotizacion validados y agregados
        """
        # 1. Validar y agrupar bases por mes_anyo
        bases_por_mes = {}
        for base_data in bases_extraidas["bases"]:
            try:
                # Validar que la base sea positiva
                if base_data.get("base", 0) < 0:
                    raise ValueError(f"Base negativa encontrada: {base_data.get('base')}")
                
                mes_anyo = base_data["mes_anyo"]
                if mes_anyo not in bases_por_mes:
                    bases_por_mes[mes_anyo] = []
                bases_por_mes[mes_anyo].append(base_data)
                
            except Exception as e:
                raise ValueError(f"Error procesando base {base_data}: {str(e)}")
        
        # 2. Procesar cada mes (con o sin pluriactividad)
        bases_procesadas = []
        for mes_anyo, bases_mes in bases_por_mes.items():
            if len(bases_mes) == 1:
                # Solo una base, procesamiento normal
                base_data = bases_mes[0]
                base = BaseCotizacion(
                    mes_anyo=base_data["mes_anyo"],
                    base=base_data["base"],
                    empresa=base_data["empresa"],
                    regimen=base_data["regimen"]
                )
                bases_procesadas.append(base)
            else:
                # Múltiples bases (pluriactividad)
                if not self._validar_coherencia_pluriactividad(bases_mes):
                    raise ValueError(f"Combinación de regímenes inválida en {mes_anyo}: {[b['regimen'] for b in bases_mes]}")
                
                resultado_agregacion = self._agregar_bases_mes(bases_mes, mes_anyo)
                
                # Crear base agregada
                base_agregada = BaseCotizacion(
                    mes_anyo=mes_anyo,
                    base=resultado_agregacion["base_agregada_final"],
                    empresa=resultado_agregacion["empresa_agregada"],
                    regimen=resultado_agregacion["regimen_principal"]
                )
                
                # Añadir metadatos de pluriactividad
                base_agregada.metadatos_pluriactividad = {
                    "es_pluriactividad": True,
                    "bases_individuales": resultado_agregacion["bases_individuales"],
                    "base_bruta": resultado_agregacion["base_agregada_bruta"],
                    "tope_aplicado": resultado_agregacion["aplicado_tope"],
                    "empresas_detalle": resultado_agregacion["empresas_detalle"]
                }
                
                bases_procesadas.append(base_agregada)
                
        # 3. Ordenar por fecha (más reciente primero)
        bases_procesadas.sort(
            key=lambda x: datetime.strptime(x.mes_anyo, "%m/%Y"),
            reverse=True
        )
        
        return bases_procesadas
        
    def _procesar_fecha_jubilacion(self, fecha_jubilacion: str) -> datetime:
        """
        Procesa la fecha de jubilación.
        
        Args:
            fecha_jubilacion: Fecha en formato "mm/AAAA"
            
        Returns:
            Objeto datetime
        """
        return datetime.strptime(fecha_jubilacion, "%m/%Y")
        
    def get_parametros_computo(self) -> Dict:
        """
        Obtiene los parámetros de cómputo para el año de jubilación.
        
        Returns:
            Diccionario con los parámetros de cómputo
        """
        año_jubilacion = self.fecha_jubilacion.year
        
        if año_jubilacion not in self.parametros_computo:
            # Buscar el año más cercano disponible
            años_disponibles = sorted(self.parametros_computo.keys())
            año_mas_cercano = min(años_disponibles, key=lambda x: abs(x - año_jubilacion))
            parametros = self.parametros_computo[año_mas_cercano]
        else:
            parametros = self.parametros_computo[año_jubilacion]
            
        return {
            "bases_incluidas": parametros["bases_incluidas"],
            "periodo_meses": parametros["periodo_meses"],
            "divisor_base_reguladora": parametros["divisor_base_reguladora"]
        }
        
    def simular_periodo_futuro(self) -> List[BaseCotizacion]:
        """
        Simula bases futuras si faltan bases hasta la fecha de jubilación.
        Utiliza el promedio de los últimos 6 meses.
        
        Returns:
            Lista de bases simuladas
        """
        bases_simuladas = []
        
        if not self.bases:
            return bases_simuladas
            
        # Obtener la fecha de la última base
        ultima_base = max(self.bases, key=lambda x: datetime.strptime(x.mes_anyo, "%m/%Y"))
        fecha_ultima_base = datetime.strptime(ultima_base.mes_anyo, "%m/%Y")
        
        # Si la fecha de jubilación es anterior o igual a la última base, no simular
        if self.fecha_jubilacion <= fecha_ultima_base:
            return bases_simuladas
            
        # Calcular promedio de los últimos 6 meses
        bases_recientes = []
        for base in self.bases:
            fecha_base = datetime.strptime(base.mes_anyo, "%m/%Y")
            if fecha_base >= fecha_ultima_base - relativedelta(months=5):
                bases_recientes.append(base.base)
                
        if not bases_recientes:
            # Si no hay bases recientes, usar la última base disponible
            promedio = ultima_base.base
        else:
            promedio = sum(bases_recientes) / len(bases_recientes)
            
        # Simular bases mensuales desde la última base hasta un mes antes de la jubilación
        fecha_actual = fecha_ultima_base + relativedelta(months=1)
        fecha_limite_simulacion = self.fecha_jubilacion - relativedelta(months=1)
        
        while fecha_actual <= fecha_limite_simulacion:
            base_simulada = BaseCotizacion(
                mes_anyo=fecha_actual.strftime("%m/%Y"),
                base=round(promedio, 2),
                empresa="SIMULADA",
                regimen=self.regimen_acceso
            )
            bases_simuladas.append(base_simulada)
            fecha_actual += relativedelta(months=1)
            
        return bases_simuladas

    def _obtener_topes_año(self, año: int) -> Dict[str, float]:
        """
        Obtiene los topes de cotización para un año específico.
        
        Args:
            año: Año para el que obtener los topes
            
        Returns:
            Dict con base_minima_mensual y base_maxima_mensual
        """
        if año in self.topes_cotizacion:
            return self.topes_cotizacion[año]
        else:
            # Usar topes del año más cercano disponible
            años_disponibles = list(self.topes_cotizacion.keys())
            año_mas_cercano = min(años_disponibles, key=lambda x: abs(x - año))
            return self.topes_cotizacion[año_mas_cercano]
            
    def _obtener_base_minima_año(self, año: int) -> float:
        """
        Obtiene la base mínima para un año específico.
        
        Args:
            año: Año para el que obtener la base mínima
            
        Returns:
            Base mínima mensual del año
        """
        topes = self._obtener_topes_año(año)
        return topes["base_minima_mensual"]

    def _agregar_bases_mes(self, bases_mes: List[Dict], fecha: str) -> Dict:
        """
        Agrega las bases de un mes aplicando topes mínimos y máximos.
        
        Args:
            bases_mes: Lista de bases del mismo mes
            fecha: Fecha en formato "mm/AAAA"
        
        Returns:
            Dict con base agregada final y metadatos
        """
        # 1. Suma bruta de todas las bases
        suma_bruta = sum(base["base"] for base in bases_mes)
        
        # 2. Obtener topes para el año
        año = int(fecha.split("/")[1])
        tope_minimo = self._obtener_base_minima_año(año)
        topes = self._obtener_topes_año(año)
        tope_maximo = topes["base_maxima_mensual"]
        
        # 3. Aplicar topes
        base_final = suma_bruta
        tope_aplicado = "ninguno"
        
        if suma_bruta < tope_minimo:
            base_final = tope_minimo
            tope_aplicado = "minimo"
        elif suma_bruta > tope_maximo:
            base_final = tope_maximo
            tope_aplicado = "maximo"
        
        # 4. Determinar régimen principal (mayor base individual)
        regimen_principal = max(bases_mes, key=lambda x: x["base"])["regimen"]
        
        # 5. Concatenar empresas para identificación
        empresas = [base["empresa"] for base in bases_mes]
        empresa_agregada = f"PLURIACTIVIDAD_{len(bases_mes)}_EMPRESAS"
        
        return {
            "mes_anyo": fecha,
            "bases_individuales": bases_mes,
            "base_agregada_bruta": round(suma_bruta, 2),
            "base_agregada_final": round(base_final, 2),
            "aplicado_tope": tope_aplicado,
            "regimen_principal": regimen_principal,
            "empresa_agregada": empresa_agregada,
            "empresas_detalle": empresas
        }

    def _validar_coherencia_pluriactividad(self, bases_mes: List[Dict]) -> bool:
        """
        Valida que la combinación de regímenes sea legalmente posible.
        
        Args:
            bases_mes: Lista de bases del mismo mes
            
        Returns:
            bool: True si la combinación es válida
        """
        regimenes = [base["regimen"] for base in bases_mes]
        regimenes_unicos = set(regimenes)
        
        # Validaciones básicas:
        # - General + Autónomo: OK
        # - Múltiples empresas del mismo régimen: OK
        # Por ahora aceptamos todas las combinaciones
        # Se pueden añadir reglas más específicas aquí
        
        return True

    def calcular_base_laguna(self, fecha_laguna: str, n_laguna: int) -> float:
        """
        Imputa la base de cotización para la n-ésima laguna según LGSS art. 209.1 y DT 41ª.
        
        Diferencias por régimen:
        - RÉGIMEN GENERAL: Aplica bases mínimas según número de laguna y sexo
        - RÉGIMEN AUTÓNOMO: Base 0 durante todas las lagunas
        
        Args:
            fecha_laguna: Fecha de la laguna en formato "mm/AAAA"
            n_laguna: Número ordinal de la laguna (1 para la primera, 2 para la segunda, etc.)
            
        Returns:
            float: Base calculada para la laguna según normativa oficial
        """
        from datetime import datetime
        año = datetime.strptime(fecha_laguna, "%m/%Y").year
        
        # RÉGIMEN DE AUTÓNOMOS: Base 0 durante lagunas
        if self.regimen_acceso == "AUTONOMO":
            return 0.0
        
        # RÉGIMEN GENERAL: Aplicar normativa de bases mínimas
        # Obtener base mínima del año correspondiente
        base_min = self._obtener_base_minima_año(año)

        # Fase 1: Primeros 48 meses de lagunas → 100% base mínima
        if n_laguna <= 48:
            return base_min

        # Aplicación de la DT 41ª para mujeres (y hombres con condiciones especiales)
        aplica_dt41 = (
            self.sexo == "FEMENINO"
            or (self.sexo == "MASCULINO" and self.cumple_condiciones_hombre)
        )
        
        if aplica_dt41:
            if n_laguna <= 60:
                return base_min         # 100% base mínima para meses 49-60
            elif n_laguna <= 84:
                return round(0.8 * base_min, 2)   # 80% base mínima para meses 61-84
            else:
                return round(0.5 * base_min, 2)   # 50% base mínima para resto
        
        # Resto de hombres sin condiciones especiales
        return round(0.5 * base_min, 2)
        
    def obtener_bases_periodo_computo(self, usar_parametros_antiguos: bool = False) -> List[BaseCotizacion]:
        """
        Obtiene las bases del período de cómputo, incluyendo lagunas.
        Va hacia atrás desde un mes antes de la fecha de jubilación.
        
        Args:
            usar_parametros_antiguos: Si True, usa parámetros prereforma (300 bases)
        
        Returns:
            Lista de bases del período de cómputo
        """
        bases_periodo = []
        bases_todas = self.bases + self.simular_periodo_futuro()
        
        # Crear diccionario para búsqueda rápida por mes/año
        bases_dict = {}
        for base in bases_todas:
            bases_dict[base.mes_anyo] = base
        
        # Determinar cuántas bases incluir
        if usar_parametros_antiguos:
            bases_incluidas = 300  # Parámetros prereforma
        else:
            bases_incluidas = self.parametros_año_jubilacion["bases_incluidas"]
            
        # Ir hacia atrás desde un mes antes de la fecha de jubilación
        fecha_actual = self.fecha_jubilacion - relativedelta(months=1)
        meses_incluidos = 0
        
        # Reiniciar contador de lagunas para cada procesamiento
        contador_lagunas_local = 0
        
        while meses_incluidos < bases_incluidas:
            mes_anyo = fecha_actual.strftime("%m/%Y")
            
            if mes_anyo in bases_dict:
                # Base existe
                bases_periodo.append(bases_dict[mes_anyo])
            else:
                # Laguna - incrementar contador y calcular base según normativa oficial
                contador_lagunas_local += 1
                base_calculada = self.calcular_base_laguna(mes_anyo, contador_lagunas_local)
                base_laguna = BaseCotizacion(
                    mes_anyo=mes_anyo,
                    base=base_calculada,
                    empresa="LAGUNA",
                    regimen=self.regimen_acceso
                )
                bases_periodo.append(base_laguna)
                
            fecha_actual -= relativedelta(months=1)
            meses_incluidos += 1
            
        return bases_periodo
        
    def añadir_periodo(self, bases_periodo: List[BaseCotizacion]) -> List[Dict]:
        """
        Añade el atributo 'periodo' a las bases según si están en los 24 meses
        anteriores a la jubilación o no.
        
        Args:
            bases_periodo: Lista de bases del período de cómputo
            
        Returns:
            Lista de diccionarios con las bases y el atributo periodo
        """
        bases_con_periodo = []
        fecha_limite = self.fecha_jubilacion - relativedelta(months=24)
        
        for base in bases_periodo:
            fecha_base = datetime.strptime(base.mes_anyo, "%m/%Y")
            
            # Determinar si la base necesita revalorización
            if fecha_base >= fecha_limite:
                periodo = "no_revalorizado"
            else:
                periodo = "revalorizado"
                
            base_dict = {
                "mes_anyo": base.mes_anyo,
                "base": base.base,
                "empresa": base.empresa,
                "regimen": base.regimen,
                "periodo": periodo
            }
            
            # Añadir metadatos de pluriactividad si existen
            if hasattr(base, 'metadatos_pluriactividad') and base.metadatos_pluriactividad is not None:
                base_dict["pluriactividad"] = base.metadatos_pluriactividad
            
            bases_con_periodo.append(base_dict)
            
        return bases_con_periodo
        
    def revalorizar_bases(self, bases_con_periodo: List[Dict]) -> List[Dict]:
        """
        Revaloriza las bases que tienen el atributo periodo: 'revalorizado'.
        
        Args:
            bases_con_periodo: Lista de bases con el atributo periodo
            
        Returns:
            Lista de bases revalorizadas
        """
        bases_revalorizadas = []
        
        for base_dict in bases_con_periodo:
            base_procesada = base_dict.copy()
            
            if base_dict["periodo"] == "revalorizado":
                mes_anyo = base_dict["mes_anyo"]
                
                if mes_anyo in self.indices_revalorizacion:
                    indice = self.indices_revalorizacion[mes_anyo]
                    base_procesada["base"] = round(base_dict["base"] * indice, 2)
                    base_procesada["base_original"] = base_dict["base"]
                    base_procesada["indice_revalorizacion"] = indice
                else:
                    # Si no hay índice disponible, mantener base original
                    base_procesada["base_original"] = base_dict["base"]
                    base_procesada["indice_revalorizacion"] = 1.0
                    
            bases_revalorizadas.append(base_procesada)
            
        return bases_revalorizadas
        
    def _calcular_estadisticas_para_bases(self, bases_procesadas: List[Dict], divisor: int) -> Dict:
        """
        Calcula estadísticas para un conjunto específico de bases procesadas.
        
        Args:
            bases_procesadas: Lista de bases procesadas
            divisor: Divisor para calcular la base reguladora
        
        Returns:
            Diccionario con estadísticas
        """
        if not bases_procesadas:
            return {}
            
        bases_revalorizadas = [
            base for base in bases_procesadas 
            if base["periodo"] == "revalorizado"
        ]
        
        bases_no_revalorizadas = [
            base for base in bases_procesadas 
            if base["periodo"] == "no_revalorizado"
        ]
        
        suma_revalorizadas = sum(base["base"] for base in bases_revalorizadas)
        suma_no_revalorizadas = sum(base["base"] for base in bases_no_revalorizadas)
        suma_total = suma_revalorizadas + suma_no_revalorizadas
        
        return {
            "total_bases": len(bases_procesadas),
            "bases_revalorizadas": len(bases_revalorizadas),
            "bases_no_revalorizadas": len(bases_no_revalorizadas),
            "suma_periodo_revalorizado": round(suma_revalorizadas, 2),
            "suma_periodo_no_revalorizado": round(suma_no_revalorizadas, 2),
            "suma_total": round(suma_total, 2),
            "base_reguladora": round(suma_total / divisor, 2)
        }
        
    def _calcular_estadisticas(self) -> Dict:
        """
        Calcula estadísticas de las bases procesadas (método original para compatibilidad).
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.bases_procesadas:
            return {}
            
        return self._calcular_estadisticas_para_bases(
            self.bases_procesadas, 
            self.parametros_año_jubilacion["divisor_base_reguladora"]
        )
        
    def suma_periodo_revalorizado(self) -> float:
        """
        Calcula la suma de las bases del período revalorizado.
        
        Returns:
            Suma de bases revalorizadas
        """
        if not self.bases_procesadas:
            return 0.0
            
        return sum(
            base["base"] for base in self.bases_procesadas 
            if base["periodo"] == "revalorizado"
        )
        
    def suma_periodo_no_revalorizado(self) -> float:
        """
        Calcula la suma de las bases del período no revalorizado.
        
        Returns:
            Suma de bases no revalorizadas
        """
        if not self.bases_procesadas:
            return 0.0
            
        return sum(
            base["base"] for base in self.bases_procesadas 
            if base["periodo"] == "no_revalorizado"
        )
        
    def suma_total(self) -> float:
        """
        Calcula la suma total de todas las bases procesadas.
        
        Returns:
            Suma total de bases
        """
        return self.suma_periodo_revalorizado() + self.suma_periodo_no_revalorizado()
        
    def to_json(self) -> str:
        """
        Convierte el resultado a JSON.
        
        Returns:
            String JSON con las bases procesadas
        """
        resultado = self.procesar_bases_completo()
        return json.dumps(resultado, ensure_ascii=False, indent=2)

    def _procesar_calculo_reforma(self) -> tuple:
        """
        Procesa el cálculo con parámetros de reforma RD 2/2023.
        
        Returns:
            tuple: (bases_revalorizadas, estadisticas)
        """
        # 1. Obtener bases del período de cómputo con parámetros reforma
        bases_periodo_reforma = self.obtener_bases_periodo_computo(usar_parametros_antiguos=False)
        
        # 2. Añadir atributo período
        bases_con_periodo_reforma = self.añadir_periodo(bases_periodo_reforma)
        
        # 3. Revalorizar bases
        bases_revalorizadas_reforma = self.revalorizar_bases(bases_con_periodo_reforma)
        
        # 4. Ordenar por fecha (más reciente primero)
        bases_revalorizadas_reforma.sort(
            key=lambda x: datetime.strptime(x["mes_anyo"], "%m/%Y"),
            reverse=True
        )
        
        # 5. Calcular estadísticas con parámetros reforma
        estadisticas_reforma = self._calcular_estadisticas_para_bases(
            bases_revalorizadas_reforma, 
            self.parametros_año_jubilacion["divisor_base_reguladora"]
        )
        
        return bases_revalorizadas_reforma, estadisticas_reforma
        
    def _procesar_calculo_prereforma(self) -> tuple:
        """
        Procesa el cálculo con parámetros prereforma (300 bases / 350 divisor).
        
        Returns:
            tuple: (bases_revalorizadas, estadisticas)
        """
        # 1. Obtener bases del período de cómputo con parámetros prereforma
        bases_periodo_prereforma = self.obtener_bases_periodo_computo(usar_parametros_antiguos=True)
        
        # 2. Añadir atributo período
        bases_con_periodo_prereforma = self.añadir_periodo(bases_periodo_prereforma)
        
        # 3. Revalorizar bases
        bases_revalorizadas_prereforma = self.revalorizar_bases(bases_con_periodo_prereforma)
        
        # 4. Ordenar por fecha (más reciente primero)
        bases_revalorizadas_prereforma.sort(
            key=lambda x: datetime.strptime(x["mes_anyo"], "%m/%Y"),
            reverse=True
        )
        
        # 5. Calcular estadísticas con parámetros prereforma
        estadisticas_prereforma = self._calcular_estadisticas_para_bases(
            bases_revalorizadas_prereforma, 
            350  # Divisor prereforma
        )
        
        return bases_revalorizadas_prereforma, estadisticas_prereforma
        
    def _elegir_calculo_mas_favorable(self, 
                                    bases_reforma: List[Dict], 
                                    estadisticas_reforma: Dict,
                                    bases_prereforma: List[Dict], 
                                    estadisticas_prereforma: Dict) -> tuple:
        """
        Elige el cálculo más favorable entre reforma y prereforma.
        
        Args:
            bases_reforma: Bases del cálculo reforma
            estadisticas_reforma: Estadísticas del cálculo reforma
            bases_prereforma: Bases del cálculo prereforma
            estadisticas_prereforma: Estadísticas del cálculo prereforma
            
        Returns:
            tuple: (bases_elegidas, estadisticas_elegidas, calculo_elegido)
        """
        base_reguladora_reforma = estadisticas_reforma["base_reguladora"]
        base_reguladora_prereforma = estadisticas_prereforma["base_reguladora"]
        
        es_mas_favorable_reforma = base_reguladora_reforma >= base_reguladora_prereforma
        
        if es_mas_favorable_reforma:
            return bases_reforma, estadisticas_reforma, "reforma_rd2_2023"
        else:
            return bases_prereforma, estadisticas_prereforma, "prereforma"
            
    def _generar_resultado_completo(self, 
                                  bases_elegidas: List[Dict],
                                  estadisticas_elegidas: Dict,
                                  calculo_elegido: str,
                                  bases_reforma: List[Dict],
                                  estadisticas_reforma: Dict,
                                  bases_prereforma: List[Dict],
                                  estadisticas_prereforma: Dict) -> Dict:
        """
        Genera el diccionario de resultado completo con toda la información.
        
        Args:
            bases_elegidas: Bases del cálculo elegido
            estadisticas_elegidas: Estadísticas del cálculo elegido
            calculo_elegido: Nombre del cálculo elegido
            bases_reforma: Bases del cálculo reforma
            estadisticas_reforma: Estadísticas del cálculo reforma
            bases_prereforma: Bases del cálculo prereforma
            estadisticas_prereforma: Estadísticas del cálculo prereforma
            
        Returns:
            Dict: Resultado completo con toda la información
        """
        return {
            "bases_procesadas": bases_elegidas,
            "estadisticas": estadisticas_elegidas,
            "calculo_elegido": calculo_elegido,
            "comparativa_calculos": {
                "calculo_reforma_rd2_2023": {
                    "parametros": {
                        "bases_incluidas": self.parametros_año_jubilacion["bases_incluidas"],
                        "divisor": self.parametros_año_jubilacion["divisor_base_reguladora"],
                        "periodo_meses": self.parametros_año_jubilacion["periodo_meses"]
                    },
                    "estadisticas": estadisticas_reforma,
                    "total_bases": len(bases_reforma)
                },
                "calculo_prereforma": {
                    "parametros": {
                        "bases_incluidas": 300,
                        "divisor": 350,
                        "periodo_meses": 300
                    },
                    "estadisticas": estadisticas_prereforma,
                    "total_bases": len(bases_prereforma)
                }
            },
            "parametros_computo": self.parametros_año_jubilacion,
            "fecha_jubilacion": self.fecha_jubilacion.strftime("%m/%Y"),
            "regimen_acceso": self.regimen_acceso,
            "sexo": self.sexo
        }

    def procesar_bases_completo(self) -> Dict:
        """
        Ejecuta el proceso completo de simulación y procesamiento de bases.
        Realiza doble cálculo: reforma RD 2/2023 vs prereforma (300/350) y elige el más favorable.
        
        Returns:
            Diccionario con las bases procesadas, ambos cálculos y estadísticas
        """
        # CÁLCULO CON REFORMA RD 2/2023
        bases_reforma, estadisticas_reforma = self._procesar_calculo_reforma()
        
        # CÁLCULO PREREFORMA
        bases_prereforma, estadisticas_prereforma = self._procesar_calculo_prereforma()
        
        # ELEGIR EL CÁLCULO MÁS FAVORABLE
        bases_elegidas, estadisticas_elegidas, calculo_elegido = self._elegir_calculo_mas_favorable(
            bases_reforma, estadisticas_reforma,
            bases_prereforma, estadisticas_prereforma
        )
        
        # Asignar bases procesadas para compatibilidad con métodos existentes
        self.bases_procesadas = bases_elegidas
        
        # GENERAR RESULTADO COMPLETO
        return self._generar_resultado_completo(
            bases_elegidas, estadisticas_elegidas, calculo_elegido,
            bases_reforma, estadisticas_reforma,
            bases_prereforma, estadisticas_prereforma
        )
