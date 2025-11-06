"""
Controlador para la interfaz gráfica.
Define un conjunto de rutas relacionadas con la interfaz del usuario.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, json, jsonify
import os

ui_bp = Blueprint('ui', __name__)


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

        # Crear diccionario de la función objetivo
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
        problema = {
            "funcion_objetivo": objective,
            "restricciones": restricciones
        }

        # (Temporal) Mostrar en consola para verificar
        import json
        print(json.dumps(problema, indent=4, ensure_ascii=False))

        # TODO: aquí se podría guardar o enviar al solver
        flash("Problema cargado correctamente.", "success")
        return render_template("preview.html", problem_data=problema)

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
def preview():
    """
    Muestra la vista previa del problema antes de resolverlo.
    """

    # Simula recepción del problema desde el formulario o JSON
    problem_data = json.loads(request.form.get("problem_data"))

    return render_template("preview.html", problem_data=problem_data)


@ui_bp.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
    data = request.get_json()  # si el formulario se envía como JSON
    print("Datos recibidos:", data)
    return jsonify({"status": "ok", "data_recibida": data}), 200


@ui_bp.route('/solve', methods=['POST'])
def solve_problem():
    """
    Procesa el problema recibido desde la vista previa y ejecuta el solver (simulado por ahora).
    """
    import json

    # Obtener datos enviados
    data_raw = request.form.get("problem_data")
    if not data_raw:
        return "<p>Error: No se recibieron datos del problema.</p>", 400

    problem_data = json.loads(data_raw)

    # Por ahora, solo mostramos por consola
    print("Problema recibido para resolver:")
    print(json.dumps(problem_data, indent=4))

    flash("Problema enviado correctamente al solver (simulado).", "success")
    return redirect(url_for("ui.index"))
