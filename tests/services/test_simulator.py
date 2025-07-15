"""
Tests para el SimuladorPeriodos.
"""

import json
import pytest
from datetime import datetime
from pipeline.simulador_periodos import SimuladorPeriodos
from utils.errors import ValidationError


class TestSimuladorPeriodos:
    """Tests para la clase SimuladorPeriodos."""
    
    def setup_method(self):
        """Configuración inicial para cada test."""
        self.bases_ejemplo = {
            "bases": [
                {
                    "mes_anyo": "01/2025",
                    "base": 1500.50,
                    "empresa": "Empresa A",
                    "regimen": "GENERAL"
                },
                {
                    "mes_anyo": "12/2024",
                    "base": 1450.75,
                    "empresa": "Empresa A",
                    "regimen": "GENERAL"
                },
                {
                    "mes_anyo": "11/2024",
                    "base": 1400.25,
                    "empresa": "Empresa B",
                    "regimen": "GENERAL"
                },
                {
                    "mes_anyo": "10/2024",
                    "base": 1350.00,
                    "empresa": "Empresa B",
                    "regimen": "GENERAL"
                },
                {
                    "mes_anyo": "09/2024",
                    "base": 1300.50,
                    "empresa": "Empresa C",
                    "regimen": "GENERAL"
                }
            ]
        }
        
    def test_inicializacion_correcta(self):
        """Test de inicialización correcta."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025",
            regimen_acceso="GENERAL"
        )
        
        assert simulador.regimen_acceso == "GENERAL"
        assert simulador.fecha_jubilacion.strftime("%m/%Y") == "06/2025"
        assert len(simulador.bases) == 5
        
    def test_validacion_datos_entrada_invalidos(self):
        """Test de validación con datos inválidos."""
        # Bases extraídas no es diccionario
        with pytest.raises(ValidationError, match="debe ser un diccionario"):
            SimuladorPeriodos(
                bases_extraidas="no es diccionario",
                fecha_jubilacion="06/2025"
            )
            
        # Fecha inválida
        with pytest.raises(ValidationError, match="Formato de fecha inválido"):
            SimuladorPeriodos(
                bases_extraidas=self.bases_ejemplo,
                fecha_jubilacion="2025/06"
            )
            
        # Régimen inválido
        with pytest.raises(ValidationError, match="Régimen inválido"):
            SimuladorPeriodos(
                bases_extraidas=self.bases_ejemplo,
                fecha_jubilacion="06/2025",
                regimen_acceso="INVALIDO"
            )
            
    def test_bases_negativas(self):
        """Test con bases negativas."""
        bases_negativas = {
            "bases": [
                {
                    "mes_anyo": "01/2025",
                    "base": -100.0,
                    "empresa": "Empresa A",
                    "regimen": "GENERAL"
                }
            ]
        }
        
        with pytest.raises(ValidationError, match="Base negativa encontrada"):
            SimuladorPeriodos(
                bases_extraidas=bases_negativas,
                fecha_jubilacion="06/2025"
            )
            
    def test_get_parametros_computo(self):
        """Test obtención de parámetros de cómputo."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        parametros = simulador.get_parametros_computo()
        
        assert "bases_incluidas" in parametros
        assert "periodo_meses" in parametros
        assert "divisor_base_reguladora" in parametros
        assert parametros["bases_incluidas"] == 300  # Para 2025 según configuración
        
    def test_simular_periodo_futuro(self):
        """Test simulación de período futuro."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        bases_simuladas = simulador.simular_periodo_futuro()
        
        # Debe simular bases desde 02/2025 hasta 06/2025
        assert len(bases_simuladas) == 5  # Feb, Mar, Abr, May, Jun
        
        # Verificar que todas las bases simuladas tienen empresa "SIMULADA"
        for base in bases_simuladas:
            assert base.empresa == "SIMULADA"
            assert base.regimen == "GENERAL"
            
    def test_obtener_bases_periodo_computo(self):
        """Test obtención de bases del período de cómputo."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        bases_periodo = simulador.obtener_bases_periodo_computo()
        
        # Debe obtener 300 bases (parámetro para 2025)
        assert len(bases_periodo) == 300
        
        # Verificar que incluye lagunas
        lagunas = [base for base in bases_periodo if base.empresa == "LAGUNA"]
        assert len(lagunas) > 0
        
    def test_añadir_periodo(self):
        """Test añadir atributo período."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        bases_periodo = simulador.obtener_bases_periodo_computo()
        bases_con_periodo = simulador.añadir_periodo(bases_periodo)
        
        # Verificar que todas las bases tienen el atributo período
        for base in bases_con_periodo:
            assert "periodo" in base
            assert base["periodo"] in ["revalorizado", "no_revalorizado"]
            
    def test_revalorizar_bases(self):
        """Test revalorización de bases."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        bases_periodo = simulador.obtener_bases_periodo_computo()
        bases_con_periodo = simulador.añadir_periodo(bases_periodo)
        bases_revalorizadas = simulador.revalorizar_bases(bases_con_periodo)
        
        # Verificar que las bases revalorizadas tienen los campos adicionales
        for base in bases_revalorizadas:
            if base["periodo"] == "revalorizado":
                assert "base_original" in base
                assert "indice_revalorizacion" in base
                
    def test_procesar_bases_completo(self):
        """Test proceso completo."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        resultado = simulador.procesar_bases_completo()
        
        # Verificar estructura del resultado
        assert "bases_procesadas" in resultado
        assert "estadisticas" in resultado
        assert "parametros_computo" in resultado
        assert "fecha_jubilacion" in resultado
        assert "regimen_acceso" in resultado
        
        # Verificar estadísticas
        estadisticas = resultado["estadisticas"]
        assert "total_bases" in estadisticas
        assert "bases_revalorizadas" in estadisticas
        assert "bases_no_revalorizadas" in estadisticas
        assert "suma_total" in estadisticas
        assert "base_reguladora" in estadisticas
        
    def test_metodos_suma(self):
        """Test métodos de suma."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        # Procesar bases
        simulador.procesar_bases_completo()
        
        suma_revalorizado = simulador.suma_periodo_revalorizado()
        suma_no_revalorizado = simulador.suma_periodo_no_revalorizado()
        suma_total = simulador.suma_total()
        
        assert suma_revalorizado >= 0
        assert suma_no_revalorizado >= 0
        assert suma_total == suma_revalorizado + suma_no_revalorizado
        
    def test_to_json(self):
        """Test conversión a JSON."""
        simulador = SimuladorPeriodos(
            bases_extraidas=self.bases_ejemplo,
            fecha_jubilacion="06/2025"
        )
        
        json_resultado = simulador.to_json()
        
        # Verificar que es JSON válido
        resultado_dict = json.loads(json_resultado)
        assert isinstance(resultado_dict, dict)
        assert "bases_procesadas" in resultado_dict


if __name__ == "__main__":
    pytest.main([__file__]) 