"""
Tests para el SolverController (Issue #7 y guardado de reporte).
Estos tests usan 'mocker' para simular:
1. La ejecución de Scipy (linprog)
2. El guardado del reporte (StorageService.save_solution)
"""

import pytest
import numpy as np
from scipy.optimize import OptimizeResult
from gilp import LP, simplex_visual
from app.controllers.solver_controller import SolverController

# --- Datos de Prueba (Mock Data) ---
# (No hay cambios aquí)
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
    'fun': 108.69565217391305, 
    'success': True,
    'x': np.array([0.782608695652174, 0.8695652173913043]),
    'message': 'Optimization successful.'
})

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
    'fun': -9833.333333333334, 
    'success': True,
    'x': np.array([388.8888888888889, 222.22222222222223]),
    'message': 'Optimization successful.'
})

def test_prepare_model_for_scipy_maximize():
    """
    Testea la 'traducción' de un problema de Maximización.
    """
    # Instanciamos el controller con los datos
    problema_completo = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MAX,
            "restricciones": MOCK_CONSTRAINTS_MAX
        }
    }
    controller = SolverController(problema_completo)
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

def test_prepare_model_for_scipy_minimize():
    """
    Testea la 'traducción' de un problema de Minimización.
    """
    # Instanciamos el controller con los datos
    problema_completo = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MIN,
            "restricciones": MOCK_CONSTRAINTS_MIN
        }
    }
    controller = SolverController(problema_completo)
    
    c, A_ub, b_ub, A_eq, b_eq, bounds = controller._prepare_model_for_scipy(
        MOCK_OBJECTIVE_MIN, MOCK_CONSTRAINTS_MIN, controller.variables
    )
    
    expected_c = np.array([50.0, 80.0])
    expected_A_ub = np.array([ 
        [-4.0, -1.0],
        [-1.0, -6.0],
        [-4.0, -6.0]
    ])
    
    np.testing.assert_array_equal(c, expected_c)
    np.testing.assert_array_equal(A_ub, expected_A_ub)


def test_run_success_maximize(mocker, capsys):
    """
    Testea el flujo 'run' completo para MAXIMIZAR.
    Verifica:
    1. El 'print' en consola.
    2. Que se llame a 'save_solution' con el reporte correcto.
    3. Que 'run' devuelva el reporte correcto.
    """
    # 1. Definir los datos
    problema_completo = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MAX,
            "restricciones": MOCK_CONSTRAINTS_MAX
        }
    }
    
    # 2. Mockear Cálculo (Scipy.linprog)
    mocker.patch('app.controllers.solver_controller.linprog', return_value=MOCK_SCIPY_RESULT_MAX)
    
    # 3. Mockear ESCRITURA (StorageService)
    mock_save = mocker.patch('app.services.StorageService.save_solution', return_value="outputs/solucion_mock.json")
    
    # 4. Ejecutar (pasando datos al constructor) y CAPTURAR RETURN
    controller = SolverController(problema_completo)
    final_report = controller.run()
    
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
    saved_report_call = mock_save.call_args[0][0]
    # 7. Verificar el return Y la llamada de guardado
    for report in [final_report, saved_report_call]:
        assert report is not None
        assert report['problema_definicion']['funcion_objetivo'] == MOCK_OBJECTIVE_MAX
        assert report['problema_definicion']['restricciones'] == MOCK_CONSTRAINTS_MAX
        assert report['solucion_encontrada']['status'] == "Solucion Factible"
        assert report['solucion_encontrada']['valor_optimo_z'] == pytest.approx(9833.333333)
        assert report['solucion_encontrada']['valores_variables']['x1'] == pytest.approx(388.888888)

def test_run_success_minimize(mocker, capsys):
    """Testea el flujo 'run' completo para MINIMIZAR y verifica el guardado."""
    # 1. Mocks de Lectura 
    problema_completo_min = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MIN,
            "restricciones": MOCK_CONSTRAINTS_MIN
        }
    }
    
    # 2. Mock de Cálculo
    mocker.patch('app.controllers.solver_controller.linprog', return_value=MOCK_SCIPY_RESULT_MIN)
    
    # 3. Mock de Escritura
    mock_save = mocker.patch('app.services.StorageService.save_solution', return_value="outputs/solucion_mock.json")
    
    # 4. Ejecutar y CAPTURAR RETURN
    controller = SolverController(problema_completo_min)
    final_report = controller.run()
    
    # 5. Verificar Print
    captured = capsys.readouterr()
    output = captured.out
    assert "Z = 108.6957" in output
    
    # 6. Verificar Guardado y Return
    mock_save.assert_called_once()
    saved_report_call = mock_save.call_args[0][0]
    
    for report in [final_report, saved_report_call]:
        assert report is not None
        assert report['problema_definicion']['funcion_objetivo'] == MOCK_OBJECTIVE_MIN
        assert report['solucion_encontrada']['status'] == "Solucion Factible"
        assert report['solucion_encontrada']['valor_optimo_z'] == pytest.approx(108.695652)

def test_run_infeasible(mocker, capsys):
    """Testea el 'print' y el 'guardado' cuando no hay solución."""
    # 1. Datos
    problema_completo = {
        "problema_definicion": {
            "funcion_objetivo": MOCK_OBJECTIVE_MAX,
            "restricciones": MOCK_CONSTRAINTS_MAX
        }
    }
    
    # 2. Mock de Cálculo (para que falle)
    mock_fail_result = OptimizeResult({'success': False, 'status': 2, 'message': 'Infeasible.'})
    mocker.patch('app.controllers.solver_controller.linprog', return_value=mock_fail_result)

    # 3. Mock de Escritura
    mock_save = mocker.patch('app.services.StorageService.save_solution', return_value="outputs/solucion_mock.json")

    # 4. Ejecutar y CAPTURAR RETURN
    controller = SolverController(problema_completo)
    final_report = controller.run()
    
    # 5. Verificar Print
    captured = capsys.readouterr()
    output = captured.out
    assert "Sin Solucion Factible " in output

    # 6. Verificar Guardado y Return
    mock_save.assert_called_once()
    saved_report_call = mock_save.call_args[0][0]
    
    for report in [final_report, saved_report_call]:
        assert report is not None
        assert report['problema_definicion']['funcion_objetivo'] == MOCK_OBJECTIVE_MAX
        assert report['solucion_encontrada']['status'] == "Sin Solucion Factible"
        assert report['solucion_encontrada']['valor_optimo_z'] is None

def test_run_load_data_fails(mocker, capsys):
    """
    Testea que 'save_solution' NO se llame si la carga falla
    (datos vacíos pasados al constructor).
    """
    # 1. Mock de Escritura
    mock_save = mocker.patch('app.services.StorageService.save_solution')

    # 2. Ejecutar (pasando datos vacíos)
    controller = SolverController(problem_data_wrapper={})
    final_report = controller.run()
    
    # 3. Verificar Print
    captured = capsys.readouterr()
    output = captured.out
    assert "Error: El solver no recibió datos válidos en la inicialización." in output
    
    # 4. Verificar que NO se guardó
    mock_save.assert_not_called()
    
    # 5. Verificar que run devolvió None
    assert final_report is None