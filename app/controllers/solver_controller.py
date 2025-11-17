"""
Controlador para el Cálculo Simplex (Issue #7).
Carga los datos de los JSON, los traduce para Scipy y muestra la solución.
Estrategia Híbrida de Visualización:
1. Intenta generar la visualización con 'gilp' (Plan A).
2. Si 'gilp' falla, usa 'simple_simplex' (Plan B)
"""
import numpy as np
from scipy.optimize import linprog
from app.services import StorageService
import tempfile
import os
import json

# Plan A
from gilp import LP, simplex_visual

# Plan B (Fallback)
from simple_simplex import (
    create_tableau,
    add_constraint,
    add_objective,
    optimize_json_format
)


class SolverController:
    """Controlador para el flujo de cálculo de la solución."""

    def __init__(self):
        self.storage = StorageService()
        self.objective_data = None
        self.constraints_data = None
        self.variables = [] 

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
            if not self._load_data_from_json(): return
            print("Preparando modelo para el solver (Scipy)...")
            c, A_ub, b_ub, A_eq, b_eq, bounds = self._prepare_model_for_scipy(
                self.objective_data, self.constraints_data, self.variables
            )
            
            print("Generando visualización (Plan A: gilp)...")
            visualization_html_str = self._generate_gilp_visualization()

            # Opciones para el solver (corrección Bug #1)
            solver_options = {"presolve": True, "time_limit": 10}
            
            # 4. Ejecutar el solver (corrección Bug #1)
            result = linprog(
                c, 
                A_ub=A_ub, b_ub=b_ub, 
                A_eq=A_eq, b_eq=b_eq, 
                bounds=bounds, 
                method='highs-ds',
                options=solver_options
            )
            
            # 5. Mostrar y GUARDAR los resultados
            self._display_and_save_results(result, self.objective_data['type'], visualization_html_str)

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
        Plan A: Intenta usar 'gilp' para crear la visualización de tablas intermedias y la retorna como un string HTML.
        Si falla, llama al Plan B ('simple_simplex').
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
            # --- Plan A falló ---
            print(f"Error en 'gilp' (Plan A): {e}. Intentando Plan B (simple-simplex)...")
            return self._generate_simple_simplex_fallback(e)

    def _tableau_to_html(self, tableau_list: list, pivot_r: int, pivot_c: int) -> str:
        """
        Convierte una lista de listas en una tabla HTML.
        Resalta la celda pivote (pivot_r, pivot_c) en rojo.
        """
        # Estilos inline para la celda pivote
        pivot_style = 'style="background-color:#fff0f0; color:#d00; font-weight:bold;"'
        
        html = [
            '<table class="table table-bordered table-striped" style="border:1px solid #ccc; justify-content:center; float:none; margin-left:auto; margin-right:auto;">'
        ]
        
        # --- Encabezado de la Tabla (Columnas 0, 1, 2...) ---
        html.append('<thead><tr>')
        if tableau_list:
            # Celda vacía para la esquina superior izquierda
            html.append('<th></th>') 
            for c_idx in range(len(tableau_list[0])):
                html.append(f'<th>{c_idx}</th>')
        html.append('</tr></thead>')
        
        # --- Cuerpo de la Tabla (Filas 0, 1, 2...) ---
        html.append('<tbody>')
        for r_idx, row in enumerate(tableau_list):
            html.append('<tr>')
            # Celda de encabezado de fila
            html.append(f'<th>{r_idx}</th>')
            
            for c_idx, cell in enumerate(row):
                style = ""
                
                if r_idx == pivot_r and c_idx == pivot_c:
                    style = pivot_style
                
                html.append(f'<td {style}>{cell:.2f}</td>')
            html.append('</tr>')
        html.append('</tbody>')
        
        html.append('</table>')
        return "".join(html)

    def _generate_simple_simplex_fallback(self, gilp_error: Exception) -> str:
        """
        Plan B: Usa 'simple_simplex' para generar las tablas.
        Este método se llama cuando 'gilp' falla.
        """

        try:
            # 1. Traducir el problema al formato de simple_simplex
            num_vars = len(self.variables)
            num_constraints = len(self.constraints_data)
            
            tableau = create_tableau(
                number_of_variables=num_vars,
                number_of_constraints=num_constraints
            )

            # 2. Añadir restricciones
            for const in self.constraints_data:
                coeffs_list = [str(const['coefficients'].get(var, 0)) for var in self.variables]
                coeffs_str = ",".join(coeffs_list)
                op = const['operator']
                op_str = "L" if op == '<=' else ("G" if op == '>=' else "E")
                rhs_str = str(const['rhs'])
                constraint_string = f"{coeffs_str},{op_str},{rhs_str}"
                print(f"simple-simplex: add_constraint({constraint_string})")
                add_constraint(tableau, constraint_string)

            # 3. Añadir función objetivo
            obj_coeffs_list = [str(self.objective_data['coefficients'].get(var, 0)) for var in self.variables]
            obj_coeffs_str = ",".join(obj_coeffs_list)
            is_maximize = (self.objective_data['type'] == 'maximize')
            obj_type_str = "1" if is_maximize else "0"
            objective_string = f"{obj_coeffs_str},{obj_type_str}"
            print(f"simple-simplex: add_objective({objective_string})")
            add_objective(tableau, objective_string)

            # 4. Resolver y capturar el JSON COMPLETO
            resultado_json = optimize_json_format(tableau, maximize=is_maximize)

            # 5. Formatear como HTML
            html_output = [
            ]

            if "pivotSteps" in resultado_json:
                for step in resultado_json["pivotSteps"]:
                    step_num = step.get("step", "?")
                    pivot_row = step.get("pivotRowIndex") # Sin 'N/A'
                    pivot_col = step.get("pivotColIndex") # Sin 'N/A'
                    tableau_data = step.get("tableau", [])
                    
                    if step_num == 0 or pivot_row is None:
                        html_output.append("<h4>Tabla Inicial (Iteración 0)</h4>")
                    else:
                        html_output.append(f"<h4>Iteración {step_num} (Pivote en Fila: {pivot_row}, Col: {pivot_col})</h4>")
                    
                    html_output.append(self._tableau_to_html(tableau_data, pivot_row, pivot_col))
            else:
                 html_output.append("<p>(No se encontraron 'pivotSteps' en la respuesta de simple-simplex).</p>")
            
            print("Visualización de 'simple-simplex' generada correctamente (Plan B).")
            return "<br>".join(html_output)

        except Exception as e:
            # Si AMBOS fallan
            print(f"Error en fallback 'simple-simplex' (Plan B): {e}")
            return f"""
            <div style='border: 1px solid red; padding: 10px; background-color: #fff0f0; border-radius: 8px;'>
                <strong>Error al generar la visualización de respaldo:</strong>
                <p><b>Error de Gilp (Plan A):</b> {gilp_error}</p>
                <p><b>Error del solver 'simple-simplex' (Plan B):</b> {e}</p>
                <p>La solución de Scipy es correcta, pero ninguna visualización pudo procesar este problema.</p>
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