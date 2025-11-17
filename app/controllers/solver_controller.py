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

from typing import Tuple, List, Any, Dict 
import json
import io

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

    def __init__(self, problem_data_wrapper: dict):
        """
        Inicializa el solver con los datos del problema desde la sesión.
        """
        self.storage = StorageService()
        
        # Los datos se cargan aquí, desde la memoria
        definition = problem_data_wrapper.get("problema_definicion", {})
        
        self.objective_data = definition.get("funcion_objetivo")
        self.constraints_data = definition.get("restricciones")

        if self.objective_data:
            self.variables = sorted(list(self.objective_data['coefficients'].keys()))
        else:
            self.variables = []
        
        print("SolverController inicializado con datos en memoria.")


    def run(self):
        """
        Ejecuta el flujo principal del cálculo:
        1. Carga los datos (YA HECHO EN __INIT__)
        2. Prepara el modelo para Scipy.
        3. Ejecuta el solver de Scipy.
        4. Si es factible, genera la visualización (Plan A o B).
        5. Muestra, guarda y DEVUELVE los resultados.
        """
        print("=== 3. Solución del Problema ===")
        
        # Verificamos que los datos se cargaron en __init__
        if self.objective_data is None or self.constraints_data is None:
            print("Error: El solver no recibió datos válidos en la inicialización.")
            return None
            
        try:
            print("Preparando modelo para el solver (Scipy)...")
            c, A_ub, b_ub, A_eq, b_eq, bounds = self._prepare_model_for_scipy(
                self.objective_data, self.constraints_data, self.variables
            )
            
            print("Ejecutando solver principal (Scipy)...")
            solver_options = {"presolve": True, "time_limit": 10} 
            
            result = linprog(
                c, 
                A_ub=A_ub, b_ub=b_ub, 
                A_eq=A_eq, b_eq=b_eq, 
                bounds=bounds, 
                method='highs-ds',
                options=solver_options
            )

            visualization_html_str = "" 

            if result.success:
                print("Generando visualización (Plan A: gilp)...")
                
                # 1. Generamos el HTML (Plan A o B, el que funcione)
                visualization_html_str, tablas_del_plan_b = self._generate_visualization_html_and_tables()
                
                # 2. Guardamos las tablas del Plan B (que sabemos que funcionan)
                visualization_tableaus_data = tablas_del_plan_b

            else:
                print("Problema infactible o no acotado. Omitiendo visualización.")
                visualization_html_str = "<p>Visualización no disponible (Problema infactible o no acotado).</p>"
                visualization_tableaus_data = [] # Añadimos esto para que no falle

            # Ahora capturamos el 'return'
            final_report = self._display_and_save_results(
                result, 
                self.objective_data['type'], 
                visualization_html_str,
                visualization_tableaus_data # Pasamos las tablas
            )
            return final_report

        except KeyError as e:
            print(f"Error inesperado: No se encontró la llave {e} en los archivos JSON.")
            print("Parece que los archivos JSON no tienen el formato esperado.")
            return None
        except Exception as e:
            print(f"Ha ocurrido un error inesperado durante el cálculo: {e}")
            import traceback # Importamos traceback
            traceback.print_exc() # Imprimimos el stack trace completo
            return None

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
                A_ub.append([-x for x in A_row])
                b_ub.append(-rhs_value)
                
            elif operator == '=':
                A_eq.append(A_row)
                b_eq.append(rhs_value)
                # Y también la convertimos para A_ub
                A_ub.append(A_row)
                b_ub.append(rhs_value)
                A_ub.append([-x for x in A_row])
                b_ub.append(-rhs_value)

        bounds = [(0, None) for _ in variables]

        A_ub_np = None if not A_ub else np.array(A_ub)
        b_ub_np = None if not b_ub else np.array(b_ub)
        A_eq_np = None if not A_eq else np.array(A_eq)
        b_eq_np = None if not b_eq else np.array(b_eq)

        return np.array(c), A_ub_np, b_ub_np, A_eq_np, b_eq_np, bounds

    def _generate_visualization_html_and_tables(self) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Estrategia híbrida:
        1. (Plan B) Ejecuta simple_simplex para OBTENER LOS DATOS DE LAS TABLAS.
        2. (Plan A) Intenta usar 'gilp' para la visualización HTML interactiva (con io.StringIO).
        3. Si 'gilp' falla, usa los datos del Plan B para generar un HTML estático.
        
        Retorna: (html_string, lista_de_tablas_extraidas)
        """
        
        # --- (PASO 1: EJECUTAMOS EL PLAN B PRIMERO) ---
        print("Ejecutando Plan B (simple_simplex) para extraer tablas...")
        plan_b_html = ""
        plan_b_tableaus = []
        try:
            resultado_json_plan_b = self._run_simple_simplex()
            plan_b_tableaus = self._extract_tableaus_from_simple_simplex(resultado_json_plan_b)
            
            html_output = []
            for table_data in plan_b_tableaus:
                title = table_data.get("title", "Tabla")
                table_list = table_data.get("table", [])
                pivot = table_data.get("pivot")
                pivot_r, pivot_c = (pivot[0], pivot[1]) if pivot else (None, None)
                
                html_output.append(f"<h4>{title}</h4>")
                html_output.append(self._tableau_to_html(table_list, pivot_r, pivot_c))
            
            plan_b_html = "<br>".join(html_output)
            print("Plan B (simple_simplex) completado exitosamente.")
            
        except Exception as e_plan_b:
            print(f"Error crítico en Plan B (simple_simplex): {e_plan_b}")
            plan_b_html = f"<p>Error en Plan B: {e_plan_b}</p>"
        
        # --- (PASO 2: EL PLAN A PARA EL HTML ) ---
        try:
            # Ahora intentamos el Plan A (gilp) solo para el HTML
            c_gilp = []
            if self.objective_data['type'] == 'maximize':
                c_gilp = [self.objective_data['coefficients'].get(var, 0) for var in self.variables]
            else: # minimize
                c_gilp = [-self.objective_data['coefficients'].get(var, 0) for var in self.variables]
            
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
                    A_gilp.append([-x for x in A_row])
                    b_gilp.append(-rhs_value)
                elif operator == '=':
                    A_gilp.append(A_row)
                    b_gilp.append(rhs_value)
                    A_gilp.append([-x for x in A_row])
                    b_gilp.append(-rhs_value)
            
            if not A_gilp:
                print("gilp: No se encontraron restricciones. Usando HTML de Plan B.")
                return plan_b_html, plan_b_tableaus # Devolvemos datos de Plan B

            lp = LP(A=A_gilp, b=b_gilp, c=c_gilp)
            visual = simplex_visual(lp=lp)
            
            f = io.StringIO()
            visual.write_html(f, include_mathjax=False, include_plotlyjs=True)
            html_content = f.getvalue()
            f.close()
            
            print("Visualización gilp (Plan A) generada (en memoria).")
            # Devolvemos el HTML de gilp (Plan A)
            # Pero los DATOS de simple_simplex (Plan B)
            return html_content, plan_b_tableaus

        except Exception as e_plan_a:
            # --- Plan A falló ---
            print(f"Error en 'gilp' (Plan A): {e_plan_a}. Usando HTML de Plan B.")
            # Devolvemos el HTML y los datos del Plan B
            return plan_b_html, plan_b_tableaus

    def _tableau_to_html(self, tableau_list: list, pivot_r: int, pivot_c: int) -> str:
        """
        Convierte una lista de listas en una tabla HTML.
        (Usamos la versión de 'main' (HEAD) que es más detallada)
        """
        if pivot_r is None: pivot_r = -1
        if pivot_c is None: pivot_c = -1
        pivot_style = 'style="background-color:#fff0f0; color:#d00; font-weight:bold;"'
        html = [
            '<table class="table table-bordered table-striped" style="border:1px solid #ccc; justify-content:center; float:none; margin-left:auto; margin-right:auto;">'
        ]
        
        for r_idx, row in enumerate(tableau_list):
            html.append('<tr>')
            for c_idx, cell in enumerate(row):
                cell_tag = 'th' if c_idx == 0 or r_idx == 0 else 'td'
                style = ""
                
                
                if r_idx == (pivot_r + 1) and c_idx == (pivot_c + 1): # +1 para saltar headers
                    style = pivot_style
                
                # Lógica de para formato
                cell_content = cell
                if isinstance(cell, float):
                    cell_content = f"{cell:.4f}"
                html.append(f'<{cell_tag} {style}>{cell_content}</{cell_tag}>')
            html.append('</tr>')
            
        html.append('</table>')
        return "".join(html)


    def _run_simple_simplex(self) -> dict:
        """
        Ejecuta el solver 'simple_simplex' y devuelve el JSON de resultados.
        """
        num_vars = len(self.variables)
        num_constraints = len(self.constraints_data)
        
        tableau = create_tableau(
            number_of_variables=num_vars,
            number_of_constraints=num_constraints
        )

        for const in self.constraints_data:
            coeffs_list = [str(const['coefficients'].get(var, 0)) for var in self.variables]
            coeffs_str = ",".join(coeffs_list)
            op = const['operator']
            op_str = "L" if op == '<=' else ("G" if op == '>=' else "E")
            rhs_str = str(const['rhs'])
            constraint_string = f"{coeffs_str},{op_str},{rhs_str}"
            add_constraint(tableau, constraint_string)

        obj_coeffs_list = [str(self.objective_data['coefficients'].get(var, 0)) for var in self.variables]
        obj_coeffs_str = ",".join(obj_coeffs_list)
        is_maximize = (self.objective_data['type'] == 'maximize')
        obj_type_str = "1" if is_maximize else "0"
        objective_string = f"{obj_coeffs_str},{obj_type_str}"
        add_objective(tableau, objective_string)

        resultado_json = optimize_json_format(tableau, maximize=is_maximize)
        return resultado_json


    def _extract_tableaus_from_simple_simplex(self, simplex_json: dict) -> List[Dict[str, Any]]:
        """
        Extrae la historia de tablas (pivotSteps) del JSON de 'simple_simplex'
        y la convierte a un formato simple (listas) para el JSON/PDF.
        (Esta es la lógica de 'main')
        """
        extracted_data = []
        if "pivotSteps" not in simplex_json:
            return extracted_data

        for step in simplex_json["pivotSteps"]:
            step_num = step.get("step", "?")
            pivot_row = step.get("pivotRowIndex") # Puede ser None
            pivot_col = step.get("pivotColIndex") # Puede ser None
            tableau_data = step.get("tableau", []) # Esta ya es una lista de listas
            
            if not tableau_data:
                continue

            num_cols = len(tableau_data[0])
            
            # Crear Headers
            headers = ["Base"] + [f"C{i}" for i in range(num_cols)]
            
            title = ""
            if step_num == 0 or pivot_row is None:
                title = "Iteración 0 (Tabla Inicial)"
            else:
                title = f"Iteración {step_num} (Pivote: Fila {pivot_row}, Col {pivot_col})"

            table_with_headers = [headers]
            for i, row in enumerate(tableau_data):
                rounded_row = [round(cell, 4) if isinstance(cell, (int, float)) else cell for cell in row]
                table_with_headers.append([f"F{i}"] + rounded_row)

            extracted_data.append({
                "iteration": step_num,
                "title": title,
                "table": table_with_headers,
                "pivot": (pivot_row, pivot_col) if pivot_row is not None and pivot_col is not None else None
            })
        return extracted_data


    def _display_and_save_results(self, result, objective_type: str, gilp_html_output: str, gilp_tableaus: list):
        """
        Muestra la solución de forma amigable, guarda el reporte completo y DEVUELVE el reporte.
        (Fusión de ambas lógicas)
        """
        
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
            "visualizacion_gilp_html": gilp_html_output,
            "tablas_intermedias": gilp_tableaus 
        }
        
        try:
            # Usamos el método estático como en 'main'
            filename = StorageService.save_solution(final_report)
            print(f"\nReporte de solución guardado en: {filename}")
        except Exception as e:
            print(f"\nAdvertencia: No se pudo guardar el reporte de solución: {e}")
        
        # Devolvemos el reporte para que la UI lo use
        return final_report