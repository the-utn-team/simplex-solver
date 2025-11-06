"""
Controlador para la interfaz gráfica.
Define un conjunto de rutas relacionadas con la interfaz del usuario.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, json, jsonify
from app.controllers.solver_controller import SolverController
from app.services import StorageService
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

        # Cantidad de variables = cantidad de coeficientes de la función objetivo
        num_vars = len(objective_list)
        num_constraints = len(constraint_signs)

        objective = {
            "type": problem_type,
            "coefficients": {f"x{i+1}": float(objective_list[i]) for i in range(num_vars)}
        }

        # Crear lista de restricciones
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

        # Estructura completa del problema
        problem_data = {
            "funcion_objetivo": objective,
            "restricciones": restricciones
        }

        # Guardar el problema para usarlo luego en el solver
        storage.save_problem({"problema_definicion": problem_data})

        flash("Problema cargado correctamente.", "success")
        return render_template("preview.html", problem_data=problem_data)

    return render_template("new_problem.html")


@ui_bp.route('/load')
def load_problem():
    """
    Vista para cargar un problema desde un archivo (.txt o .json).
    """
    if request.method == "POST":
        file = request.files.get("problem_file")

        if not file:
            flash("Selecciona un archivo antes de continuar.", "error")
            return redirect(url_for("ui.load_problem"))

        # Guardar archivo en carpeta 'uploads'
        os.makedirs("uploads", exist_ok=True)
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        flash(f"Archivo '{file.filename}' cargado correctamente.", "success")
        return redirect(url_for("ui.index"))

    return render_template("load_problem.html")


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


        # Guardar el problema en JSON para el solver
        storage = StorageService()
        storage.save_problem({"problema_definicion": problem_data})

        return render_template("preview.html", problem_data=problem_data)

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
        # Ejecutar el controlador principal del solver
        solver = SolverController()
        solver.run()  # Internamente carga los JSON guardados

        # Cargar el reporte final generado
        storage = StorageService()
        solution_report = storage.load_solution()

        if not solution_report:
            flash("No se encontró el reporte de solución.", "error")
            return redirect(url_for("ui.index"))

        return render_template("solution.html", solucion=solution_report)

    except Exception as e:
        flash(f"Error durante la resolución: {e}", "error")
        return redirect(url_for("ui.index"))
