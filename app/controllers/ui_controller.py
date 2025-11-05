"""
Controlador para la interfaz gráfica.
Define un conjunto de rutas relacionadas con la interfaz del usuario.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import os

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    """
    Vista principal del sistema.
    Muestra el nombre del proyecto y las opciones iniciales.
    """
    return render_template('index.html')

@ui_bp.route('/new')
def new_problem():
    """
    Vista para crear un nuevo problema de programación lineal.
    Permite ingresar los coeficientes de la función objetivo y restricciones.
    """
    if request.method == "POST":
        objective = request.form.get("objective")
        constraints = request.form.get("constraints")
        problem_type = request.form.get("problem_type")

        # Validación simple
        if not objective or not constraints:
            flash("Por favor completa todos los campos.", "error")
            return redirect(url_for("ui.new_problem"))

        # Simulación: guardar datos (más adelante se integrará con el solver)
        print("Tipo de problema:", problem_type)
        print("Función objetivo:", objective)
        print("Restricciones:", constraints)

        flash("Problema creado correctamente.", "success")
        return redirect(url_for("ui.index"))

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