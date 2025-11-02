import pytest
from app.controllers import ObjectiveFunctionController, ConstraintsController
from app.core import Constraint

@pytest.fixture
def mock_storage_save(mocker):
    """Mock para StorageService.save_* que retorna un filename ficticio."""
    mocker.patch('app.services.StorageService.save_objective_function', return_value="fake_obj.json")
    mocker.patch('app.services.StorageService.save_constraints', return_value="fake_const.json")

def test_objective_controller_valid_input(mocker, mock_storage_save):
    """Test flujo válido: Input correcto, parsea y guarda."""
    # --- INICIO DE CORRECCIÓN ---
    # Añadimos "max" para la primera pregunta (Issue #6)
    mocker.patch('builtins.input', side_effect=["max", "Z = 2x1 - 3x2 + 0x3"])
    # --- FIN DE CORRECCIÓN ---
    controller = ObjectiveFunctionController()
    coeffs = controller.run()
    assert coeffs == {"x1": 2.0, "x2": -3.0, "x3": 0.0}

def test_objective_controller_invalid_then_valid(mocker, mock_storage_save):
    """Test flujo inválido seguido de válido: Reintenta."""
    # --- INICIO DE CORRECCIÓN ---
    # Añadimos "min" (o "max") después de la entrada inválida
    mocker.patch('builtins.input', side_effect=["invalid", "min", "Z = 1x1 + 2x2"])
    # --- FIN DE CORRECCIÓN ---
    controller = ObjectiveFunctionController()
    coeffs = controller.run()
    assert coeffs == {"x1": 1.0, "x2": 2.0}

def test_constraints_controller_valid_inputs(mocker, mock_storage_save):
    """Test flujo válido: Múltiples constraints, valida y guarda."""
    expected_vars = {"x1", "x2"}
    mocker.patch('builtins.input', side_effect=["2x1 + 3x2 <= 10", "1x1 >= 5", "fin"])
    controller = ConstraintsController()
    controller.run(expected_vars=expected_vars)
    assert len(controller.constraints) == 2
    assert controller.constraints[0].operator == "<="
    assert controller.constraints[1].operator == ">="

def test_constraints_controller_invalid_input(mocker, mock_storage_save):
    """Test input inválido: No agrega, continua loop."""
    expected_vars = {"x1"}
    mocker.patch('builtins.input', side_effect=["invalid", "x1 <= 10", "fin"])
    controller = ConstraintsController()
    controller.run(expected_vars=expected_vars)
    assert len(controller.constraints) == 1    # Solo el válido

def test_constraints_controller_no_constraints(mocker, mock_storage_save):
    """Test sin constraints: Sale sin guardar."""
    expected_vars = {"x1"}
    mocker.patch('builtins.input', side_effect=["fin"])
    controller = ConstraintsController()
    controller.run(expected_vars=expected_vars)
    assert len(controller.constraints) == 0

def test_constraints_controller_inconsistency_error(mocker, mock_storage_save):
    """Test error post-bucle: No guarda si inconsistente."""
    expected_vars = {"x1", "x2"}
    mocker.patch('builtins.input', side_effect=["1x1 + 2x2 <= 10", "3x1 >= 5", "fin"])    # Fix: Inputs válidos (segundo falta x2, pero fill lo agrega; ambos se append)
    mocker.patch('app.core.ConstraintsValidator.validate_set_consistency', side_effect=ValueError("Inconsistencia"))
    controller = ConstraintsController()
    controller.run(expected_vars=expected_vars)
    assert len(controller.constraints) == 2    # Ahora sí se agregan 2