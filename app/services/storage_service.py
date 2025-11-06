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
    PREFIX_SOLUCION 
)

class StorageService:
    """Servicio reutilizable para manejar persistencia en archivos JSON."""

    def __init__(self):
        """Asegura que el directorio de salida exista."""
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    # --- LÓGICA DE GUARDADO (Tu código original) ---

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
    def save_json(data: Any, prefix: str) -> str:
        """Guarda datos en un nuevo archivo JSON secuencial."""
        filename = StorageService._get_next_filename(prefix=prefix)
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

    # --- LÓGICA DE CARGA (Añadida para Issue #7) ---

    @staticmethod
    def _get_latest_filename(prefix: str) -> str:
        """Encuentra el archivo con el número más alto para un prefijo dado."""
        if not os.path.exists(OUTPUT_DIR):
            return None

        # --- INICIO DE LA CORRECCIÓN ---
        # El error estaba aquí. Esta es la forma correcta y robusta
        # de crear el patrón regex para que coincida con "prefijo" + "numeros" + ".json"
        
        # 1. Escapamos el prefijo por si tiene caracteres especiales
        escaped_prefix = re.escape(prefix) 
        
        # 2. Creamos el patrón
        # ^ -> inicio de la cadena
        # (\d+) -> captura 1 o más dígitos (el número)
        # \.json$ -> termina con ".json"
        pattern = re.compile(f"^{escaped_prefix}(\\d+)\\.json$")
        # --- FIN DE LA CORRECCIÓN ---
        
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
        
        return None # No se encontró ningún archivo

    @staticmethod
    def load_json(prefix: str) -> Any:
        """Carga los datos del archivo JSON MÁS RECIENTE."""
        filename = StorageService._get_latest_filename(prefix)
        
        if not filename or not os.path.exists(filename):
            # Este es el error que estás viendo
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

    def load_problem(self) -> dict:
        """Carga el problema completo (función objetivo + restricciones)."""
        return self.load_json(prefix="problema_")

    @staticmethod
    def save_problem(problem_data: dict) -> str:
        """Guarda la definición del problema (FO + restricciones)."""
        return StorageService.save_json(problem_data, prefix="problema_")

    @staticmethod
    def load_solution() -> dict:
        """Carga la última solución guardada."""
        return StorageService.load_json(prefix=PREFIX_SOLUCION)
