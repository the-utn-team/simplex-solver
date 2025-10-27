import pytest
from app.core.objective_function_input import ObjectiveFunctionInput

def test_valid_input():
    parser = ObjectiveFunctionInput()
    result = parser.parse_function("Z = 3x1 - 5x2 + 0x3")
    assert result == {"x1": 3.0, "x2": -5.0, "x3": 0.0}

def test_invalid_format():
    parser = ObjectiveFunctionInput()
    with pytest.raises(ValueError, match="Formato inválido"):
        parser.parse_function("Z = 3a + b")

def test_non_consecutive_variables():
    parser = ObjectiveFunctionInput()
    with pytest.raises(ValueError, match="consecutivas"):
        parser.parse_function("Z = 3x1 + 5x3")  # Falta x2
