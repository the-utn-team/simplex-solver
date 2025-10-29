"""
Módulo de Servicios: Lógica de persistencia (guardar/cargar archivos).
"""
import json
import os
from typing import Any, Dict, List
from app.config import OUTPUT_DIR, PREFIX_FUNCION_OBJETIVO, PREFIX_RESTRICCIONES  # Ajusta import si config está en app/

class StorageService:
    """Servicio reutilizable para manejar persistencia en archivos JSON."""

    def __init__(self):
        # Asegurar que el directorio existe
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    @staticmethod
    def _get_next_filename(prefix: str, extension: str = ".json") -> str:
        """Encuentra el siguiente nombre de archivo secuencial disponible."""
        number = 1
        while True:
            # Usamos os.path.join para construir rutas de forma segura
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
    def save_objective_function(coefficients: Dict[str, float]) -> str:
        """Guarda los coeficientes de la función objetivo en JSON."""
        return StorageService.save_json(
            coefficients, 
            prefix=PREFIX_FUNCION_OBJETIVO
        )