"""
Cliente para consumir la API desde Streamlit u otras aplicaciones.
"""

import json
import requests
from typing import Dict, List, Optional
from pathlib import Path


class BasesAPIClient:
    """Cliente para interactuar con la API de bases de cotización."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializa el cliente.
        
        Args:
            base_url: URL base de la API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """
        Verifica si la API está funcionando.
        
        Returns:
            bool: True si la API responde correctamente
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def extract_bases(self, pdf_file_path: Path) -> Dict:
        """
        Extrae bases de cotización de un archivo PDF.
        
        Args:
            pdf_file_path: Ruta al archivo PDF
            
        Returns:
            Dict: Respuesta con las bases extraídas
            
        Raises:
            requests.HTTPError: Si hay errores en la API
        """
        url = f"{self.base_url}/api/extract"
        
        with open(pdf_file_path, 'rb') as pdf_file:
            files = {'file': (pdf_file_path.name, pdf_file, 'application/pdf')}
            
            response = self.session.post(url, files=files)
            response.raise_for_status()
            
            return response.json()
    
    def simulate_bases(self, bases_extraidas: List[Dict], fecha_jubilacion: str, 
                      regimen_acceso: str = "GENERAL", sexo: str = "MASCULINO") -> Dict:
        """
        Simula y calcula la base reguladora.
        
        Args:
            bases_extraidas: Lista de bases extraídas
            fecha_jubilacion: Fecha de jubilación en formato MM/AAAA
            regimen_acceso: Régimen de acceso
            sexo: Sexo del cotizante (MASCULINO o FEMENINO)
            
        Returns:
            Dict: Respuesta con la simulación completa
            
        Raises:
            requests.HTTPError: Si hay errores en la API
        """
        url = f"{self.base_url}/api/simulate"
        
        payload = {
            "bases_extraidas": bases_extraidas,
            "fecha_jubilacion": fecha_jubilacion,
            "regimen_acceso": regimen_acceso,
            "sexo": sexo
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    

    
    def get_simulation_config(self) -> Dict:
        """
        Obtiene la configuración disponible para simulaciones.
        
        Returns:
            Dict: Configuración de parámetros
        """
        url = f"{self.base_url}/api/simulate/config"
        
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def process_complete_workflow(self, pdf_file_path: Path, fecha_jubilacion: str,
                                 regimen_acceso: str = "GENERAL", sexo: str = "MASCULINO") -> Dict:
        """
        Ejecuta el flujo completo: extracción + simulación.
        
        Args:
            pdf_file_path: Ruta al archivo PDF
            fecha_jubilacion: Fecha de jubilación
            regimen_acceso: Régimen de acceso
            sexo: Sexo del cotizante (MASCULINO o FEMENINO)
            
        Returns:
            Dict: Resultado completo con extracción y simulación
        """
        # Paso 1: Extraer bases
        extract_result = self.extract_bases(pdf_file_path)
        
        if not extract_result.get('success'):
            raise ValueError(f"Error en extracción: {extract_result.get('message', 'Error desconocido')}")
        
        # Paso 2: Simular
        bases_data = [base.dict() if hasattr(base, 'dict') else base 
                     for base in extract_result['bases']]
        
        simulate_result = self.simulate_bases(bases_data, fecha_jubilacion, regimen_acceso, sexo)
        
        # Combinar resultados
        return {
            "extraction": extract_result,
            "simulation": simulate_result,
            "workflow_success": True
        } 