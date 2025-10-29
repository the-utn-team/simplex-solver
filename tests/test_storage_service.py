import pytest
import os
import json
import app.config as config  # Import config para OUTPUT_DIR
from app.services import StorageService
from app.core import Constraint

@pytest.fixture
def tmp_storage(tmpdir):
    """Fixture para directorio temp."""
    original_dir = config.OUTPUT_DIR  # Usa config
    config.OUTPUT_DIR = str(tmpdir)  # Override temporal
    yield
    config.OUTPUT_DIR = original_dir  # Restore

def test_save_objective_function(tmp_storage):
    """Test guarda JSON de objective."""
    coeffs = {"x1": 1.0, "x2": 2.0}
    filename = StorageService.save_objective_function(coeffs)
    assert filename.endswith(".json")
    assert os.path.exists(filename)
    with open(filename, 'r') as f:
        data = json.load(f)
        assert data == coeffs

def test_save_constraints(tmp_storage):
    """Test guarda JSON de constraints."""
    constraints = [Constraint({"x1": 1.0}, "<=", 10.0)]
    data = [c.to_dict() for c in constraints]
    filename = StorageService.save_constraints(data)
    assert filename.endswith(".json")
    assert os.path.exists(filename)
    with open(filename, 'r') as f:
        loaded = json.load(f)
        assert loaded[0]["coefficients"] == {"x1": 1.0}

def test_save_json_error(mocker, tmp_storage):
    """Test maneja IO error en save."""
    mocker.patch('builtins.open', side_effect=IOError("Mock error"))
    filename = StorageService.save_json({"test": 1}, "prefix")
    assert filename is None  # Retorna None en error