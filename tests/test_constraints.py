"""
Tests Unitarios para app.core.constraints
"""
import pytest
from app.core import ConstraintsParser, Constraint, ConstraintsValidator

# --- Tests para ConstraintsParser ---

@pytest.mark.parametrize("expression, expected_coefs, operator, rhs", [
    ("2x1 + 3x2 <= 10", {"x1": 2.0, "x2": 3.0}, "<=", 10.0),
    ("1.5x1 - 0.5x2 >= 5.5", {"x1": 1.5, "x2": -0.5}, ">=", 5.5),
    ("x1 = 3", {"x1": 1.0}, "=", 3.0),
    ("-x1 + x2 <= 100", {"x1": -1.0, "x2": 1.0}, "<=", 100.0),
    ("x1 + 2x2 + 3x3 = 10", {"x1": 1.0, "x2": 2.0, "x3": 3.0}, "=", 10.0),
    ("5x1 - 2x2 >= -50", {"x1": 5.0, "x2": -2.0}, ">=", -50.0),
    ("2*x1 + 3*x2 <= 10", {"x1": 2.0, "x2": 3.0}, "<=", 10.0), # Test con *
])
def test_parse_valid_expressions(expression, expected_coefs, operator, rhs):
    """Escenario: Ingreso válido de restricciones (Criterio de Aceptación 1)"""
    constraint = ConstraintsParser.parse(expression)
    assert constraint.coefficients == expected_coefs
    assert constraint.operator == operator
    assert constraint.rhs == rhs

@pytest.mark.parametrize("expression, error_message", [
    ("", "no puede estar vacía"),
    ("   ", "no puede estar vacía"),
    ("2x1 + 3x2 < 10", "operador válido"),
    ("2x1 + 3x2 >> 10", "operador válido"),
    ("2x1 + 3x2 =< 10", "número válido"),
    ("2x1 + 3x2 <= 10 >= 5", "número válido"),
    ("2x1 + 3x2", "Formato inválido"),
    ("<= 10", "lado izquierdo de la restricción está vacío"),
    ("2x1 + 3x2 <=", "número válido"),
    ("2x1 + 3x2 <= Diez", "número válido"),
    ("2a + 3b <= 10", "Formato inválido en el lado izquierdo"),
    ("2x1 + 3x1 <= 10", "Variable duplicada: x1"),
    ("2x1 + 3x2 + 5 <= 10", "términos no reconocidos"),
])
def test_parse_invalid_expressions(expression, error_message):
    """Escenario: Ingreso inválido o incompleto (Criterio de Aceptación 2)"""
    with pytest.raises(ValueError, match=error_message):
        ConstraintsParser.parse(expression)

# --- Tests para ConstraintsValidator ---

def test_validator_consecutive_valid():
    ConstraintsValidator.validate_consecutive_variables({"x1": 1.0, "x2": 2.0}) # OK

def test_validator_consecutive_invalid_gap():
    with pytest.raises(ValueError, match="Falta la variable x2"):
        ConstraintsValidator.validate_consecutive_variables({"x1": 1.0, "x3": 3.0})

def test_validator_consecutive_invalid_start():
    with pytest.raises(ValueError, match="debe comenzar en x1"):
        ConstraintsValidator.validate_consecutive_variables({"x2": 1.0, "x3": 3.0})

def test_validator_set_consistency_valid():
    c1 = ConstraintsParser.parse("2x1 + 3x2 <= 10")
    c2 = ConstraintsParser.parse("1x1 - 1x2 >= 5")
    assert ConstraintsValidator.validate_set_consistency([c1, c2]) == True

def test_validator_set_consistency_invalid():
    # Simulamos un caso donde post-fill aún difieren (e.g., si fill no se hace o falla lógicamente)
    c1 = Constraint(coefficients={"x1": 1.0, "x2": 1.0}, operator="<=", rhs=10)
    c2 = Constraint(coefficients={"x1": 1.0, "x3": 1.0}, operator=">=", rhs=5)    # Difiere incluso si fill, pero asumimos no fill para testear raw
    with pytest.raises(ValueError, match="Inconsistencia de variables"):
        ConstraintsValidator.validate_set_consistency([c1, c2])

# --- Tests para Constraint (to_dict/from_dict) ---

def test_constraint_serialization():
    data = {"coefficients": {"x1": 1.0, "x2": -2.0}, "operator": ">=", "rhs": 10.0}
    constraint = Constraint.from_dict(data)
    assert constraint.coefficients == data["coefficients"]
    assert constraint.operator == data["operator"]
    assert constraint.rhs == data["rhs"]
    assert constraint.to_dict() == data


# Edge cases adicionales para parsing
@pytest.mark.parametrize("expression, expected_coefs, operator, rhs", [
    ("2x1 + .5x2 = 0", {"x1": 2.0, "x2": 0.5}, "=", 0.0),   # Decimal implícito y RHS=0
    ("-0.0x1 <= 0", {"x1": -0.0}, "<=", 0.0),    # Coef 0.0 implícito
])
def test_parse_edge_cases(expression, expected_coefs, operator, rhs):
    constraint = ConstraintsParser.parse(expression)
    assert constraint.coefficients == expected_coefs
    assert constraint.operator == operator
    assert constraint.rhs == rhs

# Test para sets vacíos en validator
def test_validator_set_consistency_empty():
    assert ConstraintsValidator.validate_set_consistency([]) == True    # Vacío OK