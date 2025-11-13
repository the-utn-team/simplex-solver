"""
Tests para el SolverController (Issue #7 y guardado de reporte).
Estos tests usan 'mocker' para simular:
1. La carga de archivos (StorageService.load_problem...)
2. La ejecución de Scipy (linprog)
3. El guardado del reporte (StorageService.save_solution)

Esto nos permite testear que el controlador llame a 'save_solution'
con el diccionario 'final_report' estructurado correctamente.
"""

import pytest
import numpy as np
from scipy.optimize import OptimizeResult
from gilp import LP, simplex_visual  # Import explícito de gilp
from app.controllers.solver_controller import SolverController

# --- Datos de Prueba (Mock Data) ---

# Problema 1 (Minimizar) - Corregido al resultado real del solver
# Z = 50x1 + 80x2
MOCK_OBJECTIVE_MIN = {
    'type': 'minimize',
    'coefficients': {'x1': 50.0, 'x2': 80.0}
}
MOCK_CONSTRAINTS_MIN = [
    {'coefficients': {'x1': 4.0, 'x2': 1.0}, 'operator': '>=', 'rhs': 4.0},
    {'coefficients': {'x1': 1.0, 'x2': 6.0}, 'operator': '>=', 'rhs': 6.0},
    {'coefficients': {'x1': 4.0, 'x2': 6.0}, 'operator': '>=', 'rhs': 12.0}
]
MOCK_SCIPY_RESULT_MIN = OptimizeResult({
    # Este es el valor que encontramos con method='highs-ds'
    'fun': 108.69565217391305, 
    'success': True,
    'x': np.array([0.782608695652174, 0.8695652173913043]),
    'message': 'Optimization successful.'
})


# Problema 2 (Maximizar) 
# Z = 15x1 + 18x2
MOCK_OBJECTIVE_MAX = {
    'type': 'maximize',
    'coefficients': {'x1': 15.0, 'x2': 18.0}
}
MOCK_CONSTRAINTS_MAX = [
    {'coefficients': {'x1': 4.0, 'x2': 2.0}, 'operator': '<=', 'rhs': 2000.0},
    {'coefficients': {'x1': 2.0, 'x2': 6.0}, 'operator': '<=', 'rhs': 2400.0},
    {'coefficients': {'x1': 20.0, 'x2': 28.0}, 'operator': '<=', 'rhs': 14000.0}
]
MOCK_SCIPY_RESULT_MAX = OptimizeResult({
    # Este es el valor que encontramos con method='highs-ds'
    'fun': -9833.333333333334, 
    'success': True,
    'x': np.array([388.8888888888889, 222.22222222222223]),
    'message': 'Optimization successful.'
})

# --- Fixture ---

@pytest.fixture
def controller(mocker):
    """Crea una instancia del SolverController con StorageService 'mockeado'."""
    # Mockear (simular) la LECTURA 
    problema_completo = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MAX,
            "restricciones": MOCK_CONSTRAINTS_MAX
        }
    }
    mocker.patch('app.services.StorageService.load_problem', return_value=problema_completo)
    return SolverController()

# --- Tests ---

def test_prepare_model_for_scipy_maximize(controller):
    """
    Testea la 'traducción' de un problema de Maximización.
    """
    controller._load_data_from_json() 
    variables = controller.variables 
    
    c, A_ub, b_ub, A_eq, b_eq, bounds = controller._prepare_model_for_scipy(
        MOCK_OBJECTIVE_MAX, MOCK_CONSTRAINTS_MAX, variables
    )
    
    expected_c = np.array([-15.0, -18.0])
    expected_A_ub = np.array([
        [4.0, 2.0],
        [2.0, 6.0],
        [20.0, 28.0]
    ])
    
    np.testing.assert_array_equal(c, expected_c)
    np.testing.assert_array_equal(A_ub, expected_A_ub)
    assert A_eq is None
    assert bounds == [(0, None), (0, None)]

def test_prepare_model_for_scipy_minimize(controller):
    """
    Testea la 'traducción' de un problema de Minimización.
    """
    controller.objective_data = MOCK_OBJECTIVE_MIN
    controller.constraints_data = MOCK_CONSTRAINTS_MIN
    controller.variables = ['x1', 'x2']
    
    c, A_ub, b_ub, A_eq, b_eq, bounds = controller._prepare_model_for_scipy(
        MOCK_OBJECTIVE_MIN, MOCK_CONSTRAINTS_MIN, controller.variables
    )
    
    expected_c = np.array([50.0, 80.0])
    expected_A_ub = np.array([ # >= se convierte en <= con negativos
        [-4.0, -1.0],
        [-1.0, -6.0],
        [-4.0, -6.0]
    ])
    
    np.testing.assert_array_equal(c, expected_c)
    np.testing.assert_array_equal(A_ub, expected_A_ub)


# --- INICIO DE CORRECCIÓN EN TESTS ---

def test_run_success_maximize(mocker, capsys):
    """
    Testea el flujo 'run' completo para MAXIMIZAR.
    Verifica:
    1. El 'print' en consola.
    2. Que se llame a 'save_solution' con el reporte correcto.
    """
    # 1. Mockear Lectura - Usamos load_problem
    problema_completo = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MAX,
            "restricciones": MOCK_CONSTRAINTS_MAX
        }
    }
    mocker.patch('app.services.StorageService.load_problem', return_value=problema_completo)
    
    # 2. Mockear Cálculo (Scipy.linprog)
    mocker.patch('app.controllers.solver_controller.linprog', return_value=MOCK_SCIPY_RESULT_MAX)
    
    # 3. Mockear ESCRITURA (StorageService)
    mock_save = mocker.patch('app.services.StorageService.save_solution', return_value="outputs/solucion_mock.json")
    
    # 4. Ejecutar
    controller = SolverController()
    controller.run()
    
    # 5. Verificar el print
    captured = capsys.readouterr()
    output = captured.out
    
    assert "¡Se encontró una solución factible!" in output
    assert "x1 = 388.8889" in output 
    assert "x2 = 222.2222" in output
    assert "Z = 9833.3333" in output
    assert "Reporte de solución guardado en: outputs/solucion_mock.json" in output

    # 6. Verificar el guardado
    mock_save.assert_called_once()
    
    # Obtenemos los argumentos con los que fue llamado
    # call_args[0] es la tupla de argumentos. [0] es el primer argumento.
    saved_report = mock_save.call_args[0][0]
    
    # Verificamos que el reporte tenga la estructura correcta
    assert saved_report['problema_definicion']['funcion_objetivo'] == MOCK_OBJECTIVE_MAX
    assert saved_report['problema_definicion']['restricciones'] == MOCK_CONSTRAINTS_MAX
    assert saved_report['solucion_encontrada']['status'] == "Solucion Factible"
    # Usamos pytest.approx para comparar floats
    assert saved_report['solucion_encontrada']['valor_optimo_z'] == pytest.approx(9833.333333)
    assert saved_report['solucion_encontrada']['valores_variables']['x1'] == pytest.approx(388.888888)

def test_run_success_minimize(mocker, capsys):
    """Testea el flujo 'run' completo para MINIMIZAR y verifica el guardado."""
    # 1. Mocks de Lectura 
    problema_completo_min = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MIN,
            "restricciones": MOCK_CONSTRAINTS_MIN
        }
    }
    mocker.patch('app.services.StorageService.load_problem', return_value=problema_completo_min)
    
    # 2. Mock de Cálculo
    mocker.patch('app.controllers.solver_controller.linprog', return_value=MOCK_SCIPY_RESULT_MIN)
    
    # 3. Mock de Escritura
    mock_save = mocker.patch('app.services.StorageService.save_solution', return_value="outputs/solucion_mock.json")
    
    # 4. Ejecutar
    controller = SolverController()
    controller.run()
    
    # 5. Verificar Print
    captured = capsys.readouterr()
    output = captured.out
    assert "Z = 108.6957" in output
    
    # 6. Verificar Guardado
    mock_save.assert_called_once()
    saved_report = mock_save.call_args[0][0]
    
    assert saved_report['problema_definicion']['funcion_objetivo'] == MOCK_OBJECTIVE_MIN
    assert saved_report['solucion_encontrada']['status'] == "Solucion Factible"
    assert saved_report['solucion_encontrada']['valor_optimo_z'] == pytest.approx(108.695652)

def test_run_infeasible(mocker, capsys):
    """Testea el 'print' y el 'guardado' cuando no hay solución."""
    # 1. Mocks de Lectura 
    problema_completo = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MAX,
            "restricciones": MOCK_CONSTRAINTS_MAX
        }
    }
    mocker.patch('app.services.StorageService.load_problem', return_value=problema_completo)
    
    # 2. Mock de Cálculo (para que falle)
    mock_fail_result = OptimizeResult({'success': False, 'status': 2, 'message': 'Infeasible.'})
    mocker.patch('app.controllers.solver_controller.linprog', return_value=mock_fail_result)

    # 3. Mock de Escritura
    mock_save = mocker.patch('app.services.StorageService.save_solution', return_value="outputs/solucion_mock.json")

    # 4. Ejecutar
    controller = SolverController()
    controller.run()
    
    # 5. Verificar Print
    captured = capsys.readouterr()
    output = captured.out
    assert "Sin Solucion Factible " in output

    # 6. Verificar Guardado
    mock_save.assert_called_once()
    saved_report = mock_save.call_args[0][0]
    
    assert saved_report['problema_definicion']['funcion_objetivo'] == MOCK_OBJECTIVE_MAX
    assert saved_report['solucion_encontrada']['status'] == "Sin Solucion Factible"
    assert saved_report['solucion_encontrada']['valor_optimo_z'] is None

def test_run_load_data_fails(mocker, capsys):
    """
    Testea que 'save_solution' NO se llame si la carga falla.
    """
    # 1. Mock de Lectura (para que falle)
    mocker.patch('app.services.StorageService.load_problem', return_value=None)
    
    # 2. Mock de Escritura
    mock_save = mocker.patch('app.services.StorageService.save_solution')

    # 3. Ejecutar
    controller = SolverController()
    controller.run()
    
    # 4. Verificar Print
    captured = capsys.readouterr()
    output = captured.out
    assert "No se encontró el archivo 'problem_definition.json' o no tiene el formato esperado." in output  # Cambio: Ajustado al mensaje real de tu código
    
    # 5. Verificar que NO se guardó
    mock_save.assert_not_called()