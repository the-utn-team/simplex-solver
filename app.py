"""
Punto de Entrada Principal de la Aplicación Simplex Solver.
"""
# 1. IMPORTAMOS EL NUEVO SOLVER JUNTO A LOS OTROS
from app.controllers import ObjectiveFunctionController, ConstraintsController, SolverController

def main():
    """Ejecuta el flujo principal de la aplicación."""
    print("===================================")
    print("   BIENVENIDO AL SOLVER SIMPLEX    ")
    print("===================================\n")
    
    # --- Flujo 1: Función Objetivo ---
    obj_controller = ObjectiveFunctionController()
    coefficients = obj_controller.run()
    
    if not coefficients:
        print("No se pudo definir la función objetivo. Saliendo.")
        return

    # Extraer las variables (ej: {'x1', 'x2', 'x3'})
    expected_vars = set(coefficients.keys())

    # --- Flujo 2: Restricciones ---
    const_controller = ConstraintsController()
    const_controller.run(expected_vars=expected_vars)
    
    # --- Flujo 3: Calcular Solución (NUEVO - ISSUE #7) ---
    try:
        solver = SolverController()
        solver.run()
    except ImportError:
        print("\n================= ERROR =================")
        print("No se pudo encontrar la librería 'scipy'.")
        print("Por favor, instálala ejecutando:")
        print("pip install -r requirements.txt")
        print("=========================================")
        return
    except Exception as e:
        print(f"\nHa ocurrido un error inesperado durante el cálculo: {e}")
        return

    # --- FIN ---
    print("\n===================================")
    print("    Proceso de cálculo finalizado.   ")
    print("===================================\n")


if __name__ == "__main__":
    main()
