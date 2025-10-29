"""
Controlador para el ingreso de Restricciones.
Maneja el I/O (input/print) del usuario.
"""
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
        print(f"El modelo tiene las variables: {sorted(list(expected_vars))}")
        print("Introduce tus restricciones. Escribe 'fin' para terminar.")
        print("----------------------------------")

        while True:
            expresion = input("Restricción: ").strip()
            
            if expresion.lower() == 'fin':
                break
            if not expresion:
                continue

            try:
                # 1. Parsear
                constraint = ConstraintsParser.parse(expresion)
                
                # 2. Validar consistencia con la función objetivo
                constraint_vars = set(constraint.coefficients.keys())
                if not constraint_vars.issubset(expected_vars):
                    raise ValueError(f"Variables inconsistentes. El modelo usa {expected_vars} pero se encontró {constraint_vars}.")

                self.constraints.append(constraint)
                print(f"Restricción agregada: {expresion}\n")

            except ValueError as e:
                print(f"Error: {e}")
                print("Por favor, intente de nuevo o escriba 'fin' para salir.\n")

        # Fin del bucle
        if not self.constraints:
            print("\nNo se ingresaron restricciones.")
            return

        print(f"\nSe han ingresado {len(self.constraints)} restricciones.")
        
        # 3. Validar consistencia del set (lo que agregamos en la respuesta anterior)
        #    Aunque la validación contra expected_vars ya hace la mayor parte.
        try:
            # Convertimos a 0 las variables faltantes para el validador
            self._fill_missing_vars(expected_vars)
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