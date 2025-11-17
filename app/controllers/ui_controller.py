"""
Controlador para la interfaz gráfica.
Define un conjunto de rutas relacionadas con la interfaz del usuario.
"""

from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, json, jsonify, send_file
)
from app.controllers.solver_controller import SolverController
from app.services import StorageService
from app.config import PREFIX_PROBLEMA
from app.services.pdf_report_service import PdfReportService 
import os 


ui_bp = Blueprint('ui', __name__)
storage = StorageService()

@ui_bp.route('/')
def index():
    """
    Vista principal del sistema.
    Muestra el nombre del proyecto y las opciones iniciales.
    """
    return render_template('index.html')


@ui_bp.route('/new', methods=['GET', 'POST'])
def new_problem():
    """
    Vista para crear un nuevo problema de programación lineal.
    Convierte los datos del formulario en el formato JSON esperado por el solver.
    """
    if request.method == 'POST':
        problem_type = request.form.get('problem_type', 'maximize')
        objective_list = request.form.getlist('objective[]')
        constraint_signs = request.form.getlist('constraint_sign[]')
        constraint_rhs = request.form.getlist('constraint_rhs[]')

        num_vars = len(objective_list)
        num_constraints = len(constraint_signs)

        objective = {
            "type": problem_type,
            "coefficients": {f"x{i+1}": float(objective_list[i] if objective_list[i] else 0.0) for i in range(num_vars)}
        }

        restricciones = []
        for i in range(num_constraints):
            coefs = {}
            for j in range(num_vars):
                val = request.form.getlist(f'constraint_{j+1}[]')[i]
                coefs[f"x{j+1}"] = float(val) if val else 0.0
            restricciones.append({
                "coefficients": coefs,
                "operator": constraint_signs[i],
                "rhs": float(constraint_rhs[i]) if constraint_rhs[i] else 0.0
            })

        problem_data = {
            "funcion_objetivo": objective,
            "restricciones": restricciones
        }

        storage.save_problem({"problema_definicion": problem_data})

        return render_template("preview.html", problem_data=problem_data, from_page="new")

    return render_template("new_problem.html")


@ui_bp.route('/load', methods=['GET', 'POST'])
def load_problem():
    """
    Permite subir un archivo .json (formato exportado por la app).
    Al enviar el archivo, valida JSON, guarda el problema y muestra la vista previa.
    """
    if request.method == 'POST':
        file = request.files.get('problem_file')
        if not file:
            flash("Selecciona un archivo antes de continuar.", "error")
            return redirect(url_for("ui.load_problem"))

        try:
            content = json.load(file)
        except Exception as e:
            flash(f"Archivo JSON inválido: {e}", "error")
            return redirect(url_for("ui.load_problem"))

        problem = content.get("problema_definicion")
        if not problem:
            flash("El archivo no contiene 'problema_definicion'. Asegurate de subir el JSON exportado por la aplicación.", "error")
            return redirect(url_for("ui.load_problem"))

        ok, msg = validate_problem_structure(problem)
        if not ok:
            flash(msg, "error")
            return redirect(url_for("ui.load_problem"))

        storage.save_problem({"problema_definicion": problem})
        return render_template("preview.html", problem_data=problem, from_page="load")

    return render_template("load_problem.html")


def validate_problem_structure(problem: dict) -> tuple[bool, str]:
    """
    Valida que el JSON subido cumpla con la estructura mínima esperada.
    """
    if not isinstance(problem, dict):
        return False, "El problema debe ser un objeto JSON."

    fo = problem.get("funcion_objetivo")
    if not fo:
        return False, "Falta 'funcion_objetivo'."

    if fo.get("type") not in ("maximize", "minimize"):
        return False, "El tipo debe ser 'maximize' o 'minimize'."

    coef = fo.get("coefficients")
    if not isinstance(coef, dict) or not coef:
        return False, "Los coeficientes de la función objetivo deben ser un objeto no vacío."

    if not all(isinstance(v, (int, float)) for v in coef.values()):
        return False, "Todos los coeficientes de la función objetivo deben ser numéricos."

    restricciones = problem.get("restricciones")
    if not isinstance(restricciones, list) or not restricciones:
        return False, "Debe existir una lista de restricciones."

    for r in restricciones:
        if r.get("operator") not in ("<=", ">=", "="):
            return False, "Cada restricción debe tener operator '<=', '>=' o '='."

        if not isinstance(r.get("rhs"), (int, float)):
            return False, "Cada restricción debe tener un RHS numérico."

        coefs_r = r.get("coefficients")
        if not isinstance(coefs_r, dict) or not coefs_r:
            return False, "Cada restricción debe tener coeficientes."

        if not all(isinstance(v, (int, float)) for v in coefs_r.values()):
            return False, "Los coeficientes de cada restricción deben ser numéricos."

    return True, ""


@ui_bp.route('/preview', methods=['POST'])
def preview_problem():
    """
    Recibe los datos del problema (desde /new),
    los guarda y muestra la vista previa.
    """
    try:
        problem_data = {
            "funcion_objetivo": {
                "type": request.form.get("tipo", "maximize"),
                "coefficients": json.loads(request.form.get("coeficientes", "{}"))
            },
        "restricciones": json.loads(request.form.get("restricciones", "[]"))
        }

        storage.save_problem({"problema_definicion": problem_data})

        return render_template("preview.html", problem_data=problem_data, from_page="new")

    except Exception as e:
        flash(f"Error al procesar el problema: {e}", "error")
        return redirect(url_for("ui.new_problem"))


@ui_bp.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
    data = request.get_json()  # si el formulario se envía como JSON
    print("Datos recibidos:", data)
    return jsonify({"status": "ok", "data_recibida": data}), 200


@ui_bp.route('/solve', methods=['POST'])
def solve_problem():
    """
    Ejecuta el solver y muestra los resultados.
    """
    try:
        solver = SolverController()
        solver.run()  # Internamente carga los JSON guardados

        solution_report = storage.load_solution()

        if not solution_report:
            flash("No se encontró el reporte de solución.", "error")
            return redirect(url_for("ui.index"))

        return render_template("solution.html", solucion=solution_report)

    except Exception as e:
        flash(f"Error durante la resolución: {e}", "error")
        return redirect(url_for("ui.index"))

# --- INICIO DE CAMBIOS (NUEVA FUNCIONALIDAD) ---

@ui_bp.route('/exportar-pdf', methods=['GET'])
def exportar_pdf():
    """
    Genera un reporte en PDF de la última solución (incluyendo tablas)
    y lo envía al usuario para su descarga.
    """
    try:
        # 1. Cargar el último reporte de solución (el JSON)
        solution_report = StorageService.load_solution()
        if not solution_report:
            flash("No se encontró una solución para exportar.", "error")
            return redirect(url_for("ui.index"))

        # 2. Obtener un nombre para el nuevo archivo PDF
        pdf_filepath = StorageService.get_new_pdf_path()

        # 3. Inicializar el servicio de PDF
        pdf_service = PdfReportService(solution_report, pdf_filepath)
        
        # 4. Generar el PDF
        pdf_service.generate()

        # 5. Enviar el archivo generado al usuario
        return send_file(
            pdf_filepath,
            as_attachment=True,
            download_name=os.path.basename(pdf_filepath) # ej: "reporte_solucion_3.pdf"
        )

    except FileNotFoundError as e:
        flash(f"Error al cargar el reporte: {e}", "error")
        # --- INICIO DE CORRECCIÓN (¡EL BUG ESTABA AQUÍ!) ---
        return redirect(url_for("ui.index")) # Redirigir a una ruta GET segura
        # --- FIN DE CORRECCIÓN ---
    except Exception as e:
        flash(f"Error al generar el PDF: {e}", "error")
        # --- INICIO DE CORRECCIÓN (¡Y AQUÍ!) ---
        return redirect(url_for("ui.index")) # Redirigir a una ruta GET segura
        # --- FIN DE CORRECCIÓN ---

# --- FIN DE CAMBIOS ---

@ui_bp.route("/descargar-problema-json")
def descargar_problema_json():
    filepath = StorageService._get_latest_filename(PREFIX_PROBLEMA, extension=".json")

    if not filepath:
        return "No hay un archivo de problema disponible para descargar.", 404

    return send_file(filepath, as_attachment=True)