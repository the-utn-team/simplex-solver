"""
Controlador para el ingreso de la Función Objetivo.
Maneja el I/O (input/print) del usuario.
"""
from app.core import ObjectiveFunctionParser
from app.services import StorageService

class ObjectiveFunctionController:
    
    def __init__(self):
        self.parser = ObjectiveFunctionParser()
        self.storage = StorageService()
        self.coefficients = None

    def run(self) -> dict:
        """
        Ejecuta el flujo de ingreso de la función objetivo.
        Retorna los coeficientes si es exitoso, o None si falla.
        """
        print("=== 1. Ingreso de Función Objetivo ===")
        print("Ejemplo: Z = -2x1 + 3x2 + 0x3")
        print("----------------------------------")
        
        while True:
            expresion = input("Ingrese la función objetivo: ").strip()
            try:
                self.coefficients = self.parser.parse(expresion)
                print("Función válida. Coeficientes detectados:")
                for var, val in self.coefficients.items():
                    print(f"  {var}: {val}")
                
                # Guardar usando el servicio
                filename = self.storage.save_objective_function(self.coefficients)
                print(f"Función objetivo guardada en {filename}\n")
                return self.coefficients # Retorna los coeficientes para el app.py
                
            except ValueError as e:
                print(f"Error: {e}")
                print("Por favor, intente de nuevo.\n")