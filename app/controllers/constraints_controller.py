"""
Controlador para el ingreso de Restricciones.
Maneja el I/O (input/print) del usuario.
"""
import re # <-- IMPORTANTE: Importamos re
from typing import List, Dict
from app.core import ConstraintsParser, Constraint, ConstraintsValidator
from app.services import StorageService

class ConstraintsController:
    """Controlador para el flujo de ingreso de restricciones."""

    def __init__(self):
        self.constraints: List[Constraint] = []
        self.storage = StorageService()

    def run(self, expected_vars: set):
        """
        Ejecuta el flujo de ingreso de restricciones.
        Valida contra las variables de la función objetivo.
        """
        print("=== 2. Ingreso de Restricciones ===")
        print("Operadores permitidos: <=, >=, =")
        
        # --- INICIO DE CAMBIOS (ISSUE #5) ---
        print("Ejemplo: 2x1 + 1x2 <= 20")
        print("\nNOTA: No es necesario ingresar las restricciones de no-negatividad")
        print("(ej: x1 >= 0), el sistema las asume por defecto.")
        # --- FIN DE CAMBIOS (ISSUE #5) ---

        print(f"\nEl modelo tiene las variables: {sorted(list(expected_vars))}")
        print("Introduce tus restricciones. Escribe 'fin' para terminar.")
        print("----------------------------------")

        while True:
            expresion = input("Restricción: ").strip()
            
            if expresion.lower() == 'fin':
                # Validar que al menos haya una restricción antes de salir
                if not self.constraints:
                    print("Advertencia: No se ingresó ninguna restricción. Saliendo...")
                    break # Permite salir sin restricciones
                else:
                    break
            
            # --- INICIO DE CAMBIOS (ISSUE #5) ---
            # 1. Validar campo vacío (Criterio de Aceptación)
            if not expresion:
                print("Error: La restricción no puede estar vacía. Intente de nuevo.")
                print("----------------------------------")
                continue

            # 2. Pre-validar si es una restricción de no-negatividad (ej: x1 >= 0, x2 >= 0)
            # Usamos Regex para cachar esto ANTES de que el parser dé un error
            # Patrón: (espacios)x(digitos)(espacios) >= (espacios)0(espacios)
            non_negativity_pattern = r'^\s*x\d+\s*>=\s*0\s*$'
            if re.match(non_negativity_pattern, expresion):
                try:
                    # Lanza un error amigable que será cachado abajo
                    raise ValueError(f"No es necesario ingresar '{expresion}'. El sistema ya asume eso por defecto.")
                except ValueError as e:
                    print(f"Error: {e}")
                    print("Por favor, intente de nuevo o escriba 'fin' para salir.\n")
                    print("----------------------------------")
                    continue # Vuelve al inicio del bucle
            # --- FIN DE CAMBIOS (ISSUE #5) ---

            try:
                # 3. Parsear (Ahora solo fallará por otras razones)
                constraint = ConstraintsParser.parse(expresion)
                
                # NOTA: La lógica 'is_non_negativity' que estaba aquí se ha reemplazado
                # por el Regex de arriba, que es más efectivo para este caso.

                # 4. Validar consistencia con la función objetivo
                constraint_vars = set(constraint.coefficients.keys())
                
                # Validar que las variables de la restricción estén en la F.O.
                unknown_vars = constraint_vars - expected_vars
                if unknown_vars:
                    raise ValueError(f"Variables desconocidas: {unknown_vars}. El modelo solo usa {expected_vars}.")

                self.constraints.append(constraint)
                print(f"Restricción agregada: {expresion}\n")

            except ValueError as e:
                print(f"Error: {e}")
                print("Por favor, intente de nuevo o escriba 'fin' para salir.\n")
                print("----------------------------------")


        # Fin del bucle
        if not self.constraints:
            print("\nNo se ingresaron restricciones.")
            return

        print(f"\nSe han ingresado {len(self.constraints)} restricciones.")
        
        # 3. Validar consistencia del set
        try:
            # Convertimos a 0 las variables faltantes para el validador
            self._fill_missing_vars(expected_vars)
            
            # Validar que todas las restricciones (con 0s) tengan el mismo set de variables
            ConstraintsValidator.validate_set_consistency(self.constraints)
            
            # Solo guardar si valida OK
            constraints_data = [c.to_dict() for c in self.constraints]
            filename = self.storage.save_constraints(constraints_data)
            if filename:
                print(f"Restricciones guardadas exitosamente en {filename}")
        except ValueError as e:
            print(f"Error de consistencia interna: {e}")
            return

    def _fill_missing_vars(self, expected_vars: set):
        """Helper para rellenar con ceros las variables que no están en una restricción."""
        for constraint in self.constraints:
            for var in expected_vars:
                if var not in constraint.coefficients:
                    constraint.coefficients[var] = 0.0

