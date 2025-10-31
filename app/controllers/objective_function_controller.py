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
        # --- INICIO DE CAMBIOS (ISSUE #6) ---
        self.optimization_type = None # Guardará 'maximize' o 'minimize'
        # --- FIN DE CAMBIOS (ISSUE #6) ---

    def run(self) -> dict:
        """
        Ejecuta el flujo de ingreso de la función objetivo.
        Retorna los coeficientes si es exitoso, o None si falla.
        """
        print("=== 1. Ingreso de Función Objetivo ===")
        
        # --- INICIO DE CAMBIOS (ISSUE #6) ---
        # Criterio de Aceptación 2: Falta de selección
        print("¿Desea Maximizar (max) o Minimizar (min)?")
        print("----------------------------------")
        
        while True:
            choice = input("Seleccione el tipo de optimización: ").strip().lower()
            
            if choice in ['max', 'maximizar']:
                self.optimization_type = 'maximize'
                print("Seleccionado: Maximizar\n")
                print("----------------------------------")
                break # Sale del bucle de selección
            elif choice in ['min', 'minimizar']:
                self.optimization_type = 'minimize'
                print("Seleccionado: Minimizar\n")
                print("----------------------------------")
                break # Sale del bucle de selección
            elif not choice:
                # AC 2: Error por campo vacío
                print("Error: No ha seleccionado un tipo. Debe elegir 'max' o 'min'.")
            else:
                # AC 2: Error por selección inválida
                print(f"Error: Opción '{choice}' no válida. Intente de nuevo.")
            
            print("----------------------------------")
        # --- FIN DE CAMBIOS (ISSUE #6) ---
        
        print("Ejemplo: Z = -2x1 + 3x2 + 0x3")
        print("----------------------------------")
        
        while True:
            expresion = input("Ingrese la función objetivo: ").strip()
            
            # --- INICIO DE CAMBIOS (ISSUE #5 - Mejora) ---
            # Validar que la expresión no esté vacía
            if not expresion:
                print("Error: La función objetivo no puede estar vacía. Intente de nuevo.")
                print("----------------------------------")
                continue
            # --- FIN DE CAMBIOS (ISSUE #5 - Mejora) ---

            try:
                self.coefficients = self.parser.parse(expresion)
                print("Función válida. Coeficientes detectados:")
                for var, val in self.coefficients.items():
                    print(f"   {var}: {val}")
                
                # --- INICIO DE CAMBIOS (ISSUE #6) ---
                # Criterio de Aceptación 1: Guardar la elección
                
                # 1. Combinar la elección (max/min) y los coeficientes
                objective_data = {
                    'type': self.optimization_type,
                    'coefficients': self.coefficients
                }
                
                # 2. Guardar el diccionario completo usando el servicio
                filename = self.storage.save_objective_function(objective_data)
                # --- FIN DE CAMBIOS (ISSUE #6) ---
                
                print(f"Función objetivo guardada en {filename}\n")
                return self.coefficients # Retorna los coeficientes (como antes)
                
            except ValueError as e:
                print(f"Error: {e}")
                print("Por favor, intente de nuevo.\n")
                print("----------------------------------") # Añadido para consistencia

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
        # --- INICIO DE CAMBIOS (ISSUE #6) ---
        self.optimization_type = None # Guardará 'maximize' o 'minimize'
        # --- FIN DE CAMBIOS (ISSUE #6) ---

    def run(self) -> dict:
        """
        Ejecuta el flujo de ingreso de la función objetivo.
        Retorna los coeficientes si es exitoso, o None si falla.
        """
        print("=== 1. Ingreso de Función Objetivo ===")
        
        # --- INICIO DE CAMBIOS (ISSUE #6) ---
        # Criterio de Aceptación 2: Falta de selección
        print("¿Desea Maximizar (max) o Minimizar (min)?")
        print("----------------------------------")
        
        while True:
            choice = input("Seleccione el tipo de optimización: ").strip().lower()
            
            if choice in ['max', 'maximizar']:
                self.optimization_type = 'maximize'
                print("Seleccionado: Maximizar\n")
                print("----------------------------------")
                break # Sale del bucle de selección
            elif choice in ['min', 'minimizar']:
                self.optimization_type = 'minimize'
                print("Seleccionado: Minimizar\n")
                print("----------------------------------")
                break # Sale del bucle de selección
            elif not choice:
                # AC 2: Error por campo vacío
                print("Error: No ha seleccionado un tipo. Debe elegir 'max' o 'min'.")
            else:
                # AC 2: Error por selección inválida
                print(f"Error: Opción '{choice}' no válida. Intente de nuevo.")
            
            print("----------------------------------")
        # --- FIN DE CAMBIOS (ISSUE #6) ---
        
        print("Ejemplo: Z = -2x1 + 3x2 + 0x3")
        print("----------------------------------")
        
        while True:
            expresion = input("Ingrese la función objetivo: ").strip()
            
            # --- INICIO DE CAMBIOS (ISSUE #5 - Mejora) ---
            # Validar que la expresión no esté vacía
            if not expresion:
                print("Error: La función objetivo no puede estar vacía. Intente de nuevo.")
                print("----------------------------------")
                continue
            # --- FIN DE CAMBIOS (ISSUE #5 - Mejora) ---

            try:
                self.coefficients = self.parser.parse(expresion)
                print("Función válida. Coeficientes detectados:")
                for var, val in self.coefficients.items():
                    print(f"   {var}: {val}")
                
                # --- INICIO DE CAMBIOS (ISSUE #6) ---
                # Criterio de Aceptación 1: Guardar la elección
                
                # 1. Combinar la elección (max/min) y los coeficientes
                objective_data = {
                    'type': self.optimization_type,
                    'coefficients': self.coefficients
                }
                
                # 2. Guardar el diccionario completo usando el servicio
                filename = self.storage.save_objective_function(objective_data)
                # --- FIN DE CAMBIOS (ISSUE #6) ---
                
                print(f"Función objetivo guardada en {filename}\n")
                return self.coefficients # Retorna los coeficientes (como antes)
                
            except ValueError as e:
                print(f"Error: {e}")
                print("Por favor, intente de nuevo.\n")
                print("----------------------------------") # Añadido para consistencia

