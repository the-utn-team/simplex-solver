"""
Controlador para el Cálculo Simplex (Issue #7).
Carga los datos de los JSON, los traduce para Scipy y muestra la solución.
"""
import numpy as np
from scipy.optimize import linprog
from app.services import StorageService

class SolverController:
    """Controlador para el flujo de cálculo de la solución."""

    def __init__(self):
        self.storage = StorageService()
        self.objective_data = None
        self.constraints_data = None
        self.variables = [] # Lista ordenada de variables (ej: ['x1', 'x2'])

    def run(self):
        """
        Ejecuta el flujo principal del cálculo:
        1. Carga los datos de los JSON.
        2. Prepara el modelo para Scipy.
        3. Ejecuta el solver.
        4. Muestra y guarda los resultados.
        """
        print("=== 3. Solución del Problema ===")
        
        try:
            if not self._load_data_from_json():
                return
            
            print("Preparando modelo para el solver...\n")
            c, A_ub, b_ub, A_eq, b_eq, bounds = self._prepare_model_for_scipy(
                self.objective_data, self.constraints_data, self.variables
            )

            # Opciones para el solver (corrección Bug #1)
            solver_options = {
                "presolve": True,
                "time_limit": 10
            }

            # Ejecutar el solver (corrección Bug #1)
            result = linprog(
                c, 
                A_ub=A_ub, 
                b_ub=b_ub, 
                A_eq=A_eq, 
                b_eq=b_eq, 
                bounds=bounds, 
                method='highs-ds', # Usamos Dual Simplex
                options=solver_options
            )

            # 4. Mostrar y GUARDAR los resultados
            self._display_and_save_results(result, self.objective_data['type'])

        except FileNotFoundError as e:
            print(f"Error al cargar archivos JSON: {e}")
            print("No se pudieron cargar los datos. Abortando.")
        except KeyError as e:
            print(f"Error inesperado: No se encontró la llave {e} en los archivos JSON.")
            print("Parece que los archivos JSON no tienen el formato esperado.")
        except Exception as e:
            print(f"Ha ocurrido un error inesperado durante el cálculo: {e}")

    def _load_data_from_json(self) -> bool:
        """
        Carga la función objetivo y las restricciones desde los archivos JSON
        usando el StorageService.
        """
        print("Cargando datos...")
        self.objective_data = self.storage.load_objective_function()
        self.constraints_data = self.storage.load_constraints()

        if not self.objective_data or not self.constraints_data:
            print("No se encontraron datos de la función objetivo o de las restricciones.")
            return False
            
        self.variables = sorted(list(self.objective_data['coefficients'].keys()))
        
        print(f"Datos cargados. Variables del modelo: {self.variables}")
        return True

    def _prepare_model_for_scipy(self, objective_data: dict, constraints_data: list, variables: list):
        """
        Traduce los datos de los JSON al formato de matrices que 
        entiende scipy.optimize.linprog.
        """
        
        # --- 1. Vector de Coeficientes de la F.O. (c) ---
        objective_type = objective_data['type']
        coefficients = objective_data['coefficients']
        
        c = [coefficients.get(var, 0) for var in variables]
        
        if objective_type == 'maximize':
            c = [-val for val in c]

        # --- 2. Matrices de Restricciones (A_ub, b_ub, A_eq, b_eq) ---
        A_ub = [] # Coeficientes de Inecuaciones (<=)
        b_ub = [] # Lado derecho (RHS) de Inecuaciones (<=)
        A_eq = [] # Coeficientes de Ecuaciones (=)
        b_eq = [] # Lado derecho (RHS) de Ecuaciones (=)

        for const in constraints_data:
            A_row = [const['coefficients'].get(var, 0) for var in variables]
            operator = const['operator']
            rhs_value = const['rhs'] 

            if operator == '<=':
                A_ub.append(A_row)
                b_ub.append(rhs_value)
                
            elif operator == '>=':
                # Scipy no soporta >=. Lo convertimos a <=
                # (A >= b)  es lo mismo que  (-A <= -b)
                A_ub.append([-x for x in A_row])
                b_ub.append(-rhs_value)
                
            elif operator == '=':
                A_eq.append(A_row)
                b_eq.append(rhs_value)

        # --- 3. Límites (Bounds) ---
        # Asumimos no-negatividad por defecto (x >= 0)
        bounds = [(0, None) for _ in variables]

        # Convertir a None si están vacías, como Scipy espera
        A_ub_np = None if not A_ub else np.array(A_ub)
        b_ub_np = None if not b_ub else np.array(b_ub)
        A_eq_np = None if not A_eq else np.array(A_eq)
        b_eq_np = None if not b_eq else np.array(b_eq)

        return np.array(c), A_ub_np, b_ub_np, A_eq_np, b_eq_np, bounds

    # --- INICIO DE CAMBIOS (NUEVA FUNCIONALIDAD) ---
    # Renombrada de _display_results a _display_and_save_results
    def _display_and_save_results(self, result, objective_type: str):
        """Muestra la solución de forma amigable y guarda el reporte completo."""
        
        print("----------------------------------")
        print("         SOLUCIÓN ÓPTIMA          ")
        print("----------------------------------")
        
        # Diccionarios para el reporte JSON
        problem_definition = {
            "funcion_objetivo": self.objective_data, # Contiene 'type' y 'coefficients'
            "restricciones": self.constraints_data   # Lista de dicts de restricciones
        }
        solution_found = {}

        if result.success:
            print("¡Se encontró una solución factible! ✅\n")
            print("Valores de las variables:")
            
            solution_vars = {}
            for i, var_name in enumerate(self.variables):
                var_value = result.x[i]
                solution_vars[var_name] = var_value
                print(f"   {var_name} = {var_value:.4f}")
            
            print("\nValor de la Función Objetivo (Z):")
            final_z = -result.fun if objective_type == 'maximize' else result.fun
            print(f"   Z = {final_z:.4f}")
            
            # Llenar el dict de solución para el JSON
            solution_found = {
                "status": "Solucion Factible",
                "mensaje_solver": result.message,
                "valores_variables": solution_vars, # Guardamos los valores precisos
                "valor_optimo_z": final_z
            }
            
        else:
            status_message = "Sin Solucion Factible" if result.status == 2 else "Error"
            print(f"{status_message} ❌")
            if result.status != 2:
                print(f"(Estado: {result.message})")

            # Llenar el dict de solución para el JSON
            solution_found = {
                "status": status_message,
                "mensaje_solver": result.message,
                "valores_variables": None,
                "valor_optimo_z": None
            }
        
        # --- Guardar el reporte final ---
        final_report = {
            "problema_definicion": problem_definition,
            "solucion_encontrada": solution_found
        }
        
        try:
            filename = self.storage.save_solution(final_report)
            print(f"\nReporte de solución guardado en: {filename}")
        except Exception as e:
            print(f"\nAdvertencia: No se pudo guardar el reporte de solución: {e}")
        # --- FIN DE CAMBIOS ---

