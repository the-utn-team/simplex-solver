## web_app.py
#"""
#Punto de entrada para la interfaz web de Simplex Solver.
#"""
#
#from app.controllers.routers import init_app
#
#def main():
#    """Inicializa y ejecuta el servidor Flask."""
#    app = init_app()
#    app.run(debug=True)
#
#if __name__ == "__main__":
#    main()
"""
Punto de entrada para la interfaz web de Simplex Solver.
Este archivo es usado por Gunicorn en Docker y
para ejecución local de desarrollo.
"""

from app.controllers.routers import init_app

# --- CAMBIO IMPORTANTE ---
# Gunicorn buscará automáticamente esta variable.
app = init_app()
# -------------------------

def main():
    """
    Función de punto de entrada para ejecución local.
    NO USAR ESTO EN PRODUCCIÓN.
    """
    print("Iniciando servidor de desarrollo de Flask (debug=True)...")
    # El app.run() ahora usa la variable 'app' que creamos arriba
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()