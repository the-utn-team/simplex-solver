"""
Punto de Entrada Principal de la Aplicación Simplex Solver.
"""
from app.controllers import ObjectiveFunctionController, ConstraintsController

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
    
    print("\n===================================")
    print("  Proceso de ingreso finalizado.   ")
    print("===================================")


if __name__ == "__main__":
    main()
    