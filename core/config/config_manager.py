"""
Gestor de configuraciones del sistema.
Carga configuraciones desde archivos YAML.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from core.config.paths import CONFIG_DIR


class ConfigManager:
    """
    Gestor de configuraciones que carga datos desde archivos YAML.
    """
    
    def __init__(self):
        """Inicializa el gestor de configuraciones."""
        self._cache = {}
        self._cargar_todas_configuraciones()
    
    def _cargar_todas_configuraciones(self):
        """Carga todas las configuraciones desde archivos YAML."""
        try:
            self._cache['parametros_computo'] = self._cargar_yaml('parametros_computo_anual.yaml')
            self._cache['indices_revalorizacion'] = self._cargar_yaml('indices_revalorizacion.yaml')
            self._cache['topes_cotizacion'] = self._cargar_yaml('topes_cotizacion.yaml')
        except Exception as e:
            print(f"Error cargando configuraciones: {e}")
            # Inicializar con valores por defecto si hay error
            self._cache = {
                'parametros_computo': {},
                'indices_revalorizacion': {},
                'topes_cotizacion': {}
            }
    
    def _cargar_yaml(self, nombre_archivo: str) -> Dict[str, Any]:
        """
        Carga un archivo YAML desde el directorio de configuración.
        
        Args:
            nombre_archivo: Nombre del archivo YAML a cargar
            
        Returns:
            Diccionario con los datos del archivo YAML
        """
        archivo_path = CONFIG_DIR / "config_files" / nombre_archivo
        
        if not archivo_path.exists():
            print(f"Archivo no encontrado: {archivo_path}")
            return {}
            
        try:
            with open(archivo_path, 'r', encoding='utf-8') as file:
                datos = yaml.safe_load(file) or {}
                
            # Manejar estructuras anidadas según el tipo de archivo
            if nombre_archivo == 'parametros_computo_anual.yaml':
                return datos.get('parametros_computo_anual', datos)
            elif nombre_archivo == 'indices_revalorizacion.yaml':
                return datos.get('indices_revalorizacion', datos)
            elif nombre_archivo == 'topes_cotizacion.yaml':
                return datos.get('topes_cotizacion', datos)
            else:
                return datos
                
        except Exception as e:
            print(f"Error leyendo {nombre_archivo}: {e}")
            return {}
    
    def cargar_parametros_computo(self) -> Dict[int, Any]:
        """
        Carga los parámetros de cómputo anual.
        
        Returns:
            Dict con parámetros indexados por año
        """
        return self._cache.get('parametros_computo', {})
    
    def cargar_indices_revalorizacion(self) -> Dict[str, float]:
        """
        Carga los índices de revalorización.
        
        Returns:
            Dict con índices indexados por "mm/yyyy"
        """
        return self._cache.get('indices_revalorizacion', {})
    
    def cargar_topes_cotizacion(self) -> Dict[int, Dict[str, float]]:
        """
        Carga los topes de cotización (bases mínimas y máximas).
        
        Returns:
            Dict con topes indexados por año
        """
        return self._cache.get('topes_cotizacion', {})
    
    def reload(self):
        """Recarga todas las configuraciones desde los archivos."""
        self._cache.clear()
        self._cargar_todas_configuraciones()


# Instancia global del gestor de configuraciones
config = ConfigManager()
