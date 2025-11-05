# web_app.py
"""
Punto de entrada para la interfaz web de Simplex Solver.
"""

from app.controllers.routers import init_app

def main():
    """Inicializa y ejecuta el servidor Flask."""
    app = init_app()
    app.run(debug=True)

if __name__ == "__main__":
    main()
