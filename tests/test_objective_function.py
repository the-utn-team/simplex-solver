import pytest
from app.core import ObjectiveFunctionParser # <-- Importa la clase pura

def test_valid_input():
    result = ObjectiveFunctionParser.parse("Z = 3x1 - 5x2 + 0x3")
    assert result == {"x1": 3.0, "x2": -5.0, "x3": 0.0}

def test_no_z():
    result = ObjectiveFunctionParser.parse("3x1 - 5x2")
    assert result == {"x1": 3.0, "x2": -5.0}

def test_negative_first():
    result = ObjectiveFunctionParser.parse("-3x1 + 5x2")
    assert result == {"x1": -3.0, "x2": 5.0}

def test_with_star():
    result = ObjectiveFunctionParser.parse("Z = 3*x1 - 5*x2 + 0*x3")
    assert result == {"x1": 3.0, "x2": -5.0, "x3": 0.0}

def test_invalid_format():
    with pytest.raises(ValueError, match="Formato inválido"):
        ObjectiveFunctionParser.parse("Z = 3a + b")

def test_non_consecutive_variables():
    with pytest.raises(ValueError, match="consecutivas"):
        ObjectiveFunctionParser.parse("Z = 3x1 + 5x3") # Falta x2

def test_starts_with_x2():
    with pytest.raises(ValueError, match="comenzar en x1"):
        ObjectiveFunctionParser.parse("Z = 3x2 + 5x3")