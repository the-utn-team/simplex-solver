"""
Controlador para el Cálculo Simplex (Issue #7).
Carga los datos de los JSON, los traduce para Scipy y muestra la solución.
"""
import numpy as np
from scipy.optimize import linprog
from app.services import StorageService
# Importaciones necesarias para la visualización
from gilp import LP, simplex_visual
import tempfile
import os

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
        3. Genera la visualización de Gilp.
        4. Ejecuta el solver.
        5. Muestra y guarda los resultados.
        """
        print("=== 3. Solución del Problema ===")
        
        try:
            if not self._load_data_from_json():
                return
            
            print("Preparando modelo para el solver (Scipy)...")
            c, A_ub, b_ub, A_eq, b_eq, bounds = self._prepare_model_for_scipy(
                self.objective_data, self.constraints_data, self.variables
            )

            print("Generando visualización (gilp)...")
            gilp_html_str = self._generate_gilp_visualization()

            # Opciones para el solver (corrección Bug #1)
            solver_options = {
                "presolve": True,
                "time_limit": 10
            }

            # 4. Ejecutar el solver (corrección Bug #1)
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

            # 5. Mostrar y GUARDAR los resultados
            self._display_and_save_results(result, self.objective_data['type'], gilp_html_str)

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
        Carga la definición completa del problema desde el archivo JSON
        principal que genera el UIController.
        """
        print("Cargando datos...")
        
        problem_data = self.storage.load_problem() 

        if not problem_data or "problema_definicion" not in problem_data:
            print("No se encontró el archivo 'problem_definition.json' o no tiene el formato esperado.")
            return False

        definition = problem_data["problema_definicion"]
        
        self.objective_data = definition.get("funcion_objetivo")
        self.constraints_data = definition.get("restricciones")

        if not self.objective_data or not self.constraints_data:
            print("No se encontraron datos de la función objetivo o de las restricciones en el JSON.")
            return False
            
        self.variables = sorted(list(self.objective_data['coefficients'].keys()))
        
        print(f"Datos cargados. Variables del modelo: {self.variables}")
        return True

    def _prepare_model_for_scipy(self, objective_data: dict, constraints_data: list, variables: list):
        """
        Traduce los datos de los JSON al formato de matrices que 
        entiende scipy.optimize.linprog.
        """
        
        objective_type = objective_data['type']
        coefficients = objective_data['coefficients']
        
        c = [coefficients.get(var, 0) for var in variables]
        
        if objective_type == 'maximize':
            c = [-val for val in c]

        A_ub = [] 
        b_ub = [] 
        A_eq = [] 
        b_eq = [] 

        for const in constraints_data:
            A_row = [const['coefficients'].get(var, 0) for var in variables]
            operator = const['operator']
            rhs_value = const['rhs'] 

            if operator == '<=':
                A_ub.append(A_row)
                b_ub.append(rhs_value)
                
            elif operator == '>=':
                # (A >= b)  es lo mismo que  (-A <= -b)
                A_ub.append([-x for x in A_row])
                b_ub.append(-rhs_value)
                
            elif operator == '=':
                A_eq.append(A_row)
                b_eq.append(rhs_value)

        bounds = [(0, None) for _ in variables]

        A_ub_np = None if not A_ub else np.array(A_ub)
        b_ub_np = None if not b_ub else np.array(b_ub)
        A_eq_np = None if not A_eq else np.array(A_eq)
        b_eq_np = None if not b_eq else np.array(b_eq)

        return np.array(c), A_ub_np, b_ub_np, A_eq_np, b_eq_np, bounds

    def _generate_gilp_visualization(self) -> str:
        """
        Usa gilp para crear la visualización de tablas intermedias y la retorna como un string HTML.
        Convierte restricciones '>=' y '==' a '<=' para que gilp pueda procesarlas.
        """
        try:
            # 1. Preparar 'c' para gilp
            c_gilp = []
            if self.objective_data['type'] == 'maximize':
                c_gilp = [self.objective_data['coefficients'].get(var, 0) for var in self.variables]
            else: # minimize
                c_gilp = [-self.objective_data['coefficients'].get(var, 0) for var in self.variables]
            
            # 2. Preparar 'A' y 'b' para gilp
            A_gilp = []
            b_gilp = []

            for const in self.constraints_data:
                A_row = [const['coefficients'].get(var, 0) for var in self.variables]
                operator = const['operator']
                rhs_value = const['rhs']

                if operator == '<=':
                    A_gilp.append(A_row)
                    b_gilp.append(rhs_value)
                
                elif operator == '>=':
                    # Convertimos (A >= b) en (-A <= -b)
                    A_gilp.append([-x for x in A_row])
                    b_gilp.append(-rhs_value)
                
                elif operator == '=':
                    # --- INICIO DE CORRECCIÓN ---
                    # Convertimos (A = b) en dos restricciones:
                    # 1. (A <= b)
                    A_gilp.append(A_row)
                    b_gilp.append(rhs_value)
                    # 2. (A >= b)  ->  (-A <= -b)
                    A_gilp.append([-x for x in A_row])
                    b_gilp.append(-rhs_value)
                    # --- FIN DE CORRECCIÓN ---
            
            if not A_gilp:
                print("gilp: No se encontraron restricciones para visualizar.")
                return "(Visualización no disponible)"

            # 3. Crear el LP de gilp (Versión Simple)
            lp = LP(
                A=A_gilp,
                b=b_gilp,
                c=c_gilp
            )
            
            # 4. Crear la visualización
            visual = simplex_visual(lp=lp)
            
            # 5. Escribir a un archivo temporal para leer el HTML
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.html', encoding='utf-8') as f:
                temp_filename = f.name
                visual.write_html(temp_filename, include_mathjax=False, include_plotlyjs=True)
            
            # 6. Leer el contenido del archivo HTML
            with open(temp_filename, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 7. Limpiar el archivo temporal
            os.remove(temp_filename)
            
            print("Visualización gilp generada correctamente.")
            return html_content

        except Exception as e:
            print(f"Error generando la visualización de gilp: {e}")
            return f"""
            <div style='border: 1px solid red; padding: 10px; background-color: #fff0f0; border-radius: 8px;'>
                <strong>Error al generar la visualización:</strong>
                <p>{e}</p>
                <p>La solución de Scipy es correcta, pero gilp no pudo procesar este problema.</p>
            </div>
            """
    
    def _display_and_save_results(self, result, objective_type: str, gilp_html_output: str):
        """Muestra la solución de forma amigable y guarda el reporte completo."""
        
        print("----------------------------------")
        print("         SOLUCIÓN ÓPTIMA          ")
        print("----------------------------------")
        
        problem_definition = {
            "funcion_objetivo": self.objective_data,
            "restricciones": self.constraints_data
        }
        solution_found = {}

        if result.success:
            print("¡Se encontró una solución factible! \n")
            print("Valores de las variables:")
            
            solution_vars = {}
            for i, var_name in enumerate(self.variables):
                var_value = result.x[i]
                solution_vars[var_name] = var_value
                print(f"   {var_name} = {var_value:.4f}")
            
            print("\nValor de la Función Objetivo (Z):")
            final_z = -result.fun if objective_type == 'maximize' else result.fun
            print(f"   Z = {final_z:.4f}")
            
            solution_found = {
                "status": "Solucion Factible",
                "mensaje_solver": result.message,
                "valores_variables": solution_vars, 
                "valor_optimo_z": final_z
            }
            
        else:
            status_message = "Sin Solucion Factible" if result.status == 2 else "Error"
            print(f"{status_message} ")
            if result.status != 2:
                print(f"(Estado: {result.message})")

            solution_found = {
                "status": status_message,
                "mensaje_solver": result.message,
                "valores_variables": None,
                "valor_optimo_z": None
            }
        
        # --- Guardar el reporte final ---
        final_report = {
            "problema_definicion": problem_definition,
            "solucion_encontrada": solution_found,
            "visualizacion_gilp_html": gilp_html_output
        }
        
        try:
            filename = self.storage.save_solution(final_report)
            print(f"\nReporte de solución guardado en: {filename}")
        except Exception as e:
            print(f"\nAdvertencia: No se pudo guardar el reporte de solución: {e}")