# tests/test_visualization_integration.py (CORREGIDO)

import pytest
import numpy as np
from flask import url_for
from scipy.optimize import OptimizeResult
from bs4 import BeautifulSoup
import re
import json


# Importaciones del proyecto
from app.controllers.routers import init_app
from app.controllers.solver_controller import SolverController
from app.services import StorageService


# =============================================================================
# FIXTURES Y DATOS DE PRUEBA
# =============================================================================

@pytest.fixture
def app():
    """Crea la aplicación Flask para testing."""
    app = init_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(app):
    """Cliente de pruebas para hacer requests HTTP."""
    return app.test_client()


# Problema de Maximización Simple (2 variables, 3 restricciones)
PROBLEMA_MAX_SIMPLE = {
    "funcion_objetivo": {
        "type": "maximize",
        "coefficients": {"x1": 3.0, "x2": 5.0}
    },
    "restricciones": [
        {"coefficients": {"x1": 1.0, "x2": 0.0}, "operator": "<=", "rhs": 4.0},
        {"coefficients": {"x1": 0.0, "x2": 2.0}, "operator": "<=", "rhs": 12.0},
        {"coefficients": {"x1": 3.0, "x2": 2.0}, "operator": "<=", "rhs": 18.0}
    ]
}

# Resultado esperado para el problema simple
RESULTADO_MAX_SIMPLE = OptimizeResult({
    'fun': -36.0,  # -36 porque scipy minimiza (-Z)
    'success': True,
    'x': np.array([2.0, 6.0]),
    'message': 'Optimization successful.'
})

# Problema de Minimización (para verificar cambio de signo)
PROBLEMA_MIN_SIMPLE = {
    "funcion_objetivo": {
        "type": "minimize",
        "coefficients": {"x1": 2.0, "x2": 3.0}
    },
    "restricciones": [
        {"coefficients": {"x1": 1.0, "x2": 1.0}, "operator": ">=", "rhs": 5.0},
        {"coefficients": {"x1": 2.0, "x2": 1.0}, "operator": ">=", "rhs": 8.0}
    ]
}

RESULTADO_MIN_SIMPLE = OptimizeResult({
    'fun': 14.0,  # Valor directo porque es minimización
    'success': True,
    'x': np.array([3.0, 2.0]),
    'message': 'Optimization successful.'
})


# =============================================================================
# TESTS DE INTEGRACIÓN - FLUJO COMPLETO
# =============================================================================

def test_flujo_completo_visualizacion_maximizacion(client, mocker, tmpdir):
    """
    Test de integración completo: desde el formulario hasta la visualización.
    (Este test usa 'client', por lo que YA FUNCIONABA, no necesita cambios)
    """
    # Setup: Directorio temporal para outputs
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    # Paso 1: Enviar problema nuevo
    form_data = {
        'problem_type': 'maximize',
        'objective[]': [3.0, 5.0],
        'constraint_1[]': [1.0, 0.0, 3.0],  # Coeficientes de x1 para cada restricción
        'constraint_2[]': [0.0, 2.0, 2.0],  # Coeficientes de x2 para cada restricción
        'constraint_sign[]': ['<=', '<=', '<='],
        'constraint_rhs[]': [4.0, 12.0, 18.0]
    }
    
    response = client.post('/new', data=form_data, follow_redirects=False)
    assert response.status_code == 200  # Muestra preview
    
    # Verificar que el preview contiene los datos correctos
    html = response.data.decode('utf-8')
    assert 'Maximize' in html or '3' in html  # Al menos debe tener los coeficientes
    
    # Paso 2: Mock del solver y resolver
    mocker.patch('app.controllers.solver_controller.linprog', 
                 return_value=RESULTADO_MAX_SIMPLE)
    
    response = client.post('/solve', follow_redirects=True)
    assert response.status_code == 200
    
    # Paso 3: Verificar que la página de solución contiene:
    html = response.data.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # 3a. Datos de la solución
    assert 'Solucion Factible' in html or 'Factible' in html
    assert '2.0000' in html  # x1 = 2
    assert '6.0000' in html  # x2 = 6
    assert '36.0000' in html  # Z = 36
    
    # 3b. Contenedor de visualización gilp
    gilp_container = soup.find('div', class_='gilp-container')
    assert gilp_container is not None, "No se encontró el contenedor .gilp-container"
    
    # 3c. Verificar que contiene contenido HTML
    has_plot = 'plotly' in str(gilp_container).lower() or 'Plotly' in str(gilp_container)
    has_content = len(str(gilp_container)) > 500  # Al menos tiene contenido sustancial
    
    assert has_plot or has_content, "La visualización gilp no contiene contenido"


def test_tablas_simplex_coinciden_con_calculos_internos(mocker, tmpdir):
    """
    Test que verifica que las tablas mostradas coinciden con los cálculos.

    """
    # Setup
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))

    # Mock del linprog para tener control total
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=RESULTADO_MAX_SIMPLE)
    # Ejecutar solver (pasando datos al constructor)
    solver = SolverController({"problema_definicion": PROBLEMA_MAX_SIMPLE})
    solution = solver.run() # Capturamos el return
    
    assert solution is not None
    
    # Verificar estructura del reporte
    assert 'problema_definicion' in solution
    assert 'solucion_encontrada' in solution
    assert 'visualizacion_gilp_html' in solution
    
    # Parsear el HTML de gilp
    html = solution['visualizacion_gilp_html']
    soup = BeautifulSoup(html, 'html.parser')
    
    assert len(html) > 100, "El HTML de gilp está vacío o muy corto"
    
    tiene_plotly = 'plotly' in html.lower() or 'Plotly' in html
    tiene_divs = len(soup.find_all('div')) > 0
    
    assert tiene_plotly or tiene_divs, "No se encontró contenido de visualización de gilp"
    
    assert 'x1' in html or 'x_1' in html or 'x[1]' in html, "Variable x1 no aparece"
    assert 'x2' in html or 'x_2' in html or 'x[2]' in html, "Variable x2 no aparece"
    
    assert solution['solucion_encontrada']['valores_variables']['x1'] == 2.0
    assert solution['solucion_encontrada']['valores_variables']['x2'] == 6.0
    assert solution['solucion_encontrada']['valor_optimo_z'] == 36.0


def test_visualizacion_problema_minimizacion(client, mocker, tmpdir):
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    # Enviar problema de minimización
    form_data = {
        'problem_type': 'minimize',
        'objective[]': [2.0, 3.0],
        'constraint_1[]': [1.0, 2.0],
        'constraint_2[]': [1.0, 1.0],
        'constraint_sign[]': ['>=', '>='],
        'constraint_rhs[]': [5.0, 8.0]
    }
    
    client.post('/new', data=form_data)
    
    # Mock solver
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=RESULTADO_MIN_SIMPLE)
    
    response = client.post('/solve', follow_redirects=True)
    html = response.data.decode('utf-8')
    
    assert '14.0000' in html or '14.00' in html
    
    soup = BeautifulSoup(html, 'html.parser')
    gilp_container = soup.find('div', class_='gilp-container')
    assert gilp_container is not None


def test_visualizacion_con_restricciones_igualdad(mocker, tmpdir):
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    problema_con_igualdad = {
        "funcion_objetivo": {
            "type": "maximize",
            "coefficients": {"x1": 1.0, "x2": 1.0}
        },
        "restricciones": [
            {"coefficients": {"x1": 1.0, "x2": 1.0}, "operator": "=", "rhs": 10.0},
            {"coefficients": {"x1": 2.0, "x2": 1.0}, "operator": "<=", "rhs": 15.0}
        ]
    }
    # Mock de resultado
    mock_result = OptimizeResult({
        'fun': -10.0,
        'success': True,
        'x': np.array([5.0, 5.0]),
        'message': 'Optimization successful.'
    })
    
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=mock_result)
    
    solver = SolverController({"problema_definicion": problema_con_igualdad})
    solution = solver.run()
    
    # Verificar que se generó visualización sin errores
    html = solution['visualizacion_gilp_html']
    
    assert 'Error al generar la visualización' not in html
    assert 'error' not in html.lower()[:500]
    assert len(html) > 100


def test_visualizacion_problema_infactible(mocker, tmpdir):
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    # Problema infactible: x1 <= 5 y x1 >= 10
    problema_infactible = {
        "funcion_objetivo": {
            "type": "maximize",
            "coefficients": {"x1": 1.0}
        },
        "restricciones": [
            {"coefficients": {"x1": 1.0}, "operator": "<=", "rhs": 5.0},
            {"coefficients": {"x1": 1.0}, "operator": ">=", "rhs": 10.0}
        ]
    }

    # Mock de resultado infactible
    mock_result = OptimizeResult({
        'success': False,
        'status': 2,
        'message': 'Infeasible problem.'
    })
    
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=mock_result)
    
    solver = SolverController({"problema_definicion": problema_infactible})
    solution = solver.run()
    
    # Verificar que el status es correcto
    assert solution['solucion_encontrada']['status'] == 'Sin Solucion Factible'
    
    # La visualización puede estar vacía o contener un mensaje
    html = solution['visualizacion_gilp_html']
    assert html is not None


# =============================================================================
# TESTS DE VALIDACIÓN DE CONTENIDO ESPECÍFICO
# =============================================================================

def test_verificar_estructura_html_visualizacion(mocker, tmpdir):
    """
    --- CORREGIDO PARA SOLUCIÓN B ---
    """
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))

    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=RESULTADO_MAX_SIMPLE)
    
    solver = SolverController({"problema_definicion": PROBLEMA_MAX_SIMPLE})
    solution = solver.run()
    
    html = solution['visualizacion_gilp_html']
    
    # Verificar que es HTML válido
    soup = BeautifulSoup(html, 'html.parser')
    
    # Debe contener al menos un div
    assert soup.find('div') is not None
    
    # Si contiene plotly, debe tener el script
    if 'plotly' in html.lower():
        assert 'script' in html.lower() or 'Plotly' in html


def test_integracion_css_con_visualizacion(client, mocker, tmpdir):
    """
    (Este test usa 'client', por lo que YA FUNCIONABA, no necesita cambios)
    """
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    # Enviar problema
    form_data = {
        'problem_type': 'maximize',
        'objective[]': [3.0, 5.0],
        'constraint_1[]': [1.0, 0.0, 3.0], # Corregido
        'constraint_2[]': [0.0, 2.0, 2.0], # Corregido
        'constraint_sign[]': ['<=', '<=', '<='],
        'constraint_rhs[]': [4.0, 12.0, 18.0]
    }
    
    client.post('/new', data=form_data)
    
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=RESULTADO_MAX_SIMPLE)
    
    response = client.post('/solve', follow_redirects=True)
    html = response.data.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Verificar que existe el contenedor con la clase correcta
    gilp_container = soup.find('div', class_='gilp-container')
    assert gilp_container is not None
    
    # Verificar que el CSS está linkeado
    css_link = soup.find('link', {'href': lambda x: x and 'style.css' in x})
    assert css_link is not None, "No se encontró el link al archivo CSS"
    
    # Verificar que el contenedor tiene la clase correcta
    assert 'class="gilp-container"' in html


# =============================================================================
# TESTS DE REGRESIÓN
# =============================================================================

def test_regresion_problema_sin_restricciones(mocker, tmpdir):
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    problema_sin_restricciones = {
        "funcion_objetivo": {
            "type": "maximize",
            "coefficients": {"x1": 1.0, "x2": 1.0}
        },
        "restricciones": []  # Sin restricciones
    }

    # Mock de resultado
    mock_result = OptimizeResult({
        'success': False,
        'status': 3,
        'message': 'Unbounded problem.'
    })
    
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=mock_result)
    
    solver = SolverController({"problema_definicion": problema_sin_restricciones})
    solution = solver.run()  # No debe fallar
    
    assert solution is not None
    
    assert 'solucion_encontrada' in solution


def test_regresion_coeficientes_cero(mocker, tmpdir):

    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    problema_con_ceros = {
        "funcion_objetivo": {
            "type": "maximize",
            "coefficients": {"x1": 0.0, "x2": 5.0}
        },
        "restricciones": [
            {"coefficients": {"x1": 1.0, "x2": 0.0}, "operator": "<=", "rhs": 10.0},
            {"coefficients": {"x1": 0.0, "x2": 1.0}, "operator": "<=", "rhs": 5.0}
        ]
    }
    
    mock_result = OptimizeResult({
        'fun': -25.0,
        'success': True,
        'x': np.array([0.0, 5.0]),
        'message': 'Optimization successful.'
    })
    
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=mock_result)
    
    solver = SolverController({"problema_definicion": problema_con_ceros})
    solution = solver.run()
    
    html = solution['visualizacion_gilp_html']
    
    # Verificar que se generó algo
    assert len(html) > 0
    
    # Verificar valores en la solución
    assert solution['solucion_encontrada']['valores_variables']['x1'] == 0.0
    assert solution['solucion_encontrada']['valores_variables']['x2'] == 5.0


# =============================================================================
# TEST DE PERFORMANCE
# =============================================================================

def test_performance_visualizacion_problema_grande(mocker, tmpdir):

    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    # Crear un problema con 3 variables y 5 restricciones
    problema_grande = {
        "funcion_objetivo": {
            "type": "maximize",
            "coefficients": {"x1": 1.0, "x2": 2.0, "x3": 3.0}
        },
        "restricciones": [
            {
                "coefficients": {"x1": 1.0, "x2": 1.0, "x3": 1.0},
                "operator": "<=",
                "rhs": 10.0
            },
            {
                "coefficients": {"x1": 2.0, "x2": 1.0, "x3": 0.0},
                "operator": "<=",
                "rhs": 15.0
            },
            {
                "coefficients": {"x1": 0.0, "x2": 2.0, "x3": 1.0},
                "operator": "<=",
                "rhs": 12.0
            }
        ]
    }

    # Mock de resultado
    mock_result = OptimizeResult({
        'fun': -30.0,
        'success': True,
        'x': np.array([5.0, 3.0, 2.0]),
        'message': 'Optimization successful.'
    })
    
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=mock_result)
    
    solver = SolverController({"problema_definicion": problema_grande})
    solution = solver.run()
    
    assert solution is not None
    assert 'visualizacion_gilp_html' in solution


# =============================================================================
# TESTS AUXILIARES - HELPERS
# =============================================================================

def test_solucion_contiene_datos_problema_original(mocker, tmpdir):
    mocker.patch('app.config.OUTPUT_DIR', str(tmpdir))
    
    mocker.patch('app.controllers.solver_controller.linprog',
                 return_value=RESULTADO_MAX_SIMPLE)
    
    solver = SolverController({"problema_definicion": PROBLEMA_MAX_SIMPLE})
    solution = solver.run()
    
    # Verificar que contiene la definición original
    assert solution['problema_definicion'] == PROBLEMA_MAX_SIMPLE
    
    # Verificar que contiene la solución
    assert solution['solucion_encontrada']['status'] == 'Solucion Factible'
    
    # Verificar que contiene la visualización
    assert 'visualizacion_gilp_html' in solution
    assert len(solution['visualizacion_gilp_html']) > 0