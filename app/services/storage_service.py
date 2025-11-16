"""
Módulo de Servicios: Lógica de persistencia (guardar/cargar archivos).

Funcionalidad:
- Guarda la F.O., Restricciones y Solución en archivos JSON secuenciales.
- Carga la F.O. y Restricciones MÁS RECIENTES para el solver.
"""
import json
import os
import re # Para encontrar el archivo más reciente
from typing import Any, Dict, List
# Asume que config.py está en el directorio 'app' o en el PYTHONPATH
from app.config import (
    OUTPUT_DIR, 
    PREFIX_FUNCION_OBJETIVO, 
    PREFIX_RESTRICCIONES,
    PREFIX_SOLUCION,
    # --- INICIO DE CAMBIOS ---
    PREFIX_PROBLEMA, # Importamos el prefijo del problema
    PREFIX_PDF         # Importamos el nuevo prefijo del PDF
    # --- FIN DE CAMBIOS ---
)

class StorageService:
    """Servicio reutilizable para manejar persistencia en archivos JSON."""

    def __init__(self):
        """Asegura que el directorio de salida exista."""
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    # --- LÓGICA DE NOMBRES DE ARCHIVO ---

    @staticmethod
    def _get_next_filename(prefix: str, extension: str = ".json") -> str:
        """Encuentra el siguiente nombre de archivo secuencial disponible."""
        number = 1
        while True:
            filename = os.path.join(OUTPUT_DIR, f"{prefix}{number}{extension}")
            if not os.path.exists(filename):
                return filename
            number += 1

    @staticmethod
    def _get_latest_filename(prefix: str, extension: str = ".json") -> str: # <-- CAMBIO: Añadido extension
        """Encuentra el archivo con el número más alto para un prefijo dado."""
        if not os.path.exists(OUTPUT_DIR):
            return None
            
        escaped_prefix = re.escape(prefix) 
        # --- INICIO DE CAMBIOS ---
        # Corregido para que coincida con la extensión exacta
        escaped_extension = re.escape(extension)
        pattern = re.compile(f"^{escaped_prefix}(\\d+){escaped_extension}$")
        # --- FIN DE CAMBIOS ---
        
        latest_num = -1
        latest_file = None

        for f in os.listdir(OUTPUT_DIR):
            match = pattern.match(f)
            if match:
                num = int(match.group(1))
                if num > latest_num:
                    latest_num = num
                    latest_file = f
        
        if latest_file:
            return os.path.join(OUTPUT_DIR, latest_file)
        
        return None

    # --- LÓGICA DE GUARDADO DE JSON ---

    @staticmethod
    def save_json(data: Any, prefix: str, extension: str = ".json") -> str: # <-- CAMBIO: Añadido extension
        """Guarda datos en un nuevo archivo JSON secuencial."""
        # --- INICIO DE CAMBIOS ---
        # Pasamos la extensión al helper
        filename = StorageService._get_next_filename(prefix=prefix, extension=extension)
        # --- FIN DE CAMBIOS ---
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return filename
        except IOError as e:
            print(f"Error al guardar el archivo {filename}: {e}")
            return None

    @staticmethod
    def save_constraints(constraints: List[Dict]) -> str:
        """Guarda una lista de diccionarios de restricciones en JSON."""
        return StorageService.save_json(
            constraints, 
            prefix=PREFIX_RESTRICCIONES
        )

    @staticmethod
    def save_objective_function(objective_data: Dict) -> str:
        """Guarda los datos de la función objetivo en JSON."""
        return StorageService.save_json(
            objective_data, 
            prefix=PREFIX_FUNCION_OBJETIVO
        )
    
    @staticmethod
    def save_solution(report_data: Dict) -> str:
        """Guarda el reporte de la solución final en JSON."""
        return StorageService.save_json(
            report_data,
            prefix=PREFIX_SOLUCION
        )
    
    # --- INICIO DE CAMBIOS ---
    # Convertido a staticmethod para que ui_controller pueda llamarlo
    @staticmethod
    def save_problem(problem_data: dict) -> str:
        """Guarda la definición del problema (FO + restricciones)."""
        return StorageService.save_json(problem_data, prefix=PREFIX_PROBLEMA)
    # --- FIN DE CAMBIOS ---

    # --- LÓGICA DE CARGA DE JSON ---

    @staticmethod
    def load_json(prefix: str) -> Any:
        """Carga los datos del archivo JSON MÁS RECIENTE."""
        # --- INICIO DE CAMBIOS ---
        # Pasamos la extensión .json
        filename = StorageService._get_latest_filename(prefix, extension=".json")
        # --- FIN DE CAMBIOS ---
        
        if not filename or not os.path.exists(filename):
            raise FileNotFoundError(f"No se encontró ningún archivo con prefijo '{prefix}' en {OUTPUT_DIR}.")
            
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            print(f"Error: El archivo {filename} está corrupto o mal formateado.")
            return None
        except IOError as e:
            print(f"Error al leer el archivo {filename}: {e}")
            return None

    @staticmethod
    def load_constraints() -> List[Dict]:
        """Carga las restricciones más recientes."""
        return StorageService.load_json(prefix=PREFIX_RESTRICCIONES)

    @staticmethod
    def load_objective_function() -> Dict:
        """Carga la función objetivo más reciente."""
        return StorageService.load_json(prefix=PREFIX_FUNCION_OBJETIVO)

    # --- INICIO DE CAMBIOS ---
    # Convertido a staticmethod
    @staticmethod
    def load_problem() -> dict:
        """Carga el problema completo (función objetivo + restricciones)."""
        return StorageService.load_json(prefix=PREFIX_PROBLEMA)
    # --- FIN DE CAMBIOS ---

    @staticmethod
    def load_solution() -> dict:
        """Carga la última solución guardada."""
        return StorageService.load_json(prefix=PREFIX_SOLUCION)

    # --- INICIO DE CAMBIOS (exportación en pdf) ---
    @staticmethod
    def get_new_pdf_path() -> str:
        """Obtiene la ruta completa para el *próximo* archivo PDF."""
        return StorageService._get_next_filename(prefix=PREFIX_PDF, extension=".pdf")
    # --- FIN DE CAMBIOS ---