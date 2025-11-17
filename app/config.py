"""
Módulo de Configuración.
Almacena constantes y configuraciones de la aplicación.
"""
# --- INICIO DE CAMBIOS ---
import os

# 1. Definimos la ruta absoluta a la RAÍZ de tu proyecto (ej: "C:\...\simplex-solver")
# os.path.dirname(__file__) es la ruta a la carpeta actual ('app')
# os.path.abspath(...) obtiene la ruta completa
# os.path.join(..., "..") sube un nivel, saliendo de 'app' a la raíz
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 2. Definimos el directorio de salida como una RUTA ABSOLUTA
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
# --- FIN DE CAMBIOS ---


# Prefijos para los archivos de salida
PREFIX_FUNCION_OBJETIVO = "funcion_objetivo"
PREFIX_RESTRICCIONES = "restricciones"
PREFIX_SOLUCION = "solucion_"
PREFIX_PROBLEMA = "problema_"
PREFIX_PDF = "reporte_solucion_"