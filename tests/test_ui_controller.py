"""
Tests para el Controlador de la UI (Flask).
Verifica que las rutas web funcionen como se espera.
"""
import pytest
from app.controllers.routers import init_app
from app.services import StorageService, PdfReportService
import os

# --- Fixtures (Configuración de Prueba) ---

@pytest.fixture
def app():
    """Crea una instancia de la app de Flask para testing."""
    app = init_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key" # Necesario para los flashes
    })
    yield app

@pytest.fixture
def client(app):
    """Un cliente de prueba para la app de Flask."""
    return app.test_client()

# Datos de prueba (un reporte de solución falso)
MOCK_SOLUTION_REPORT = {
    "problema_definicion": {
        "funcion_objetivo": {"type": "maximize", "coefficients": {"x1": 1, "x2": 2}},
        "restricciones": [{"coefficients": {"x1": 1, "x2": 1}, "operator": "<=", "rhs": 10}]
    },
    "solucion_encontrada": {
        "status": "Solucion Factible",
        "valores_variables": {"x1": 0.0, "x2": 10.0},
        "valor_optimo_z": 20.0
    },
    "tablas_intermedias": [
        {"title": "Iteración 0", "table": [["Base", "x1", "x2", "RHS"], ["s1", 1, 1, 10], ["Z", -1, -2, 0]]}
    ]
}

# --- Tests para /exportar-pdf ---

def test_exportar_pdf_success(mocker, client):
    """
    Testea que la ruta /exportar-pdf llame a los servicios correctos
    y envíe un archivo cuando la solución SÍ existe.
    """
    
    # 1. Simular (mock) los servicios que se usan
    
    # Simular que SÍ encontramos un reporte JSON
    mocker.patch.object(StorageService, 'load_solution', return_value=MOCK_SOLUTION_REPORT)
    
    # Simular que nos da un nombre de archivo PDF
    mocker.patch.object(StorageService, 'get_new_pdf_path', return_value="outputs/mock_report.pdf")
    
    # Simular la *generación* del PDF (no queremos crear un archivo real)
    mock_pdf_generate = mocker.patch.object(PdfReportService, 'generate', return_value=True)
    
    # Simular el *envío* del archivo (lo más importante)
    mock_send_file = mocker.patch('app.controllers.ui_controller.send_file', return_value="PDF content as string")

    # 2. Llamar a la ruta /exportar-pdf
    response = client.get('/exportar-pdf')

    # 3. Verificar (Asserts)
    
    # Verificamos que la respuesta fue "OK" (200)
    assert response.status_code == 200 
    assert response.data == b"PDF content as string" 
    
    # Verificamos que se llamó a `generate`
    mock_pdf_generate.assert_called_once()
    
    # Verificamos que `send_file` se llamó con los argumentos correctos
    mock_send_file.assert_called_with(
        "outputs/mock_report.pdf",
        as_attachment=True,
        download_name="mock_report.pdf"
    )

def test_exportar_pdf_no_solution_found(mocker, client):
    """
    Testea que redirija a / (index) con un mensaje flash
    si NO se encuentra el archivo solucion_X.json.
    """
    # 1. Simular el error (StorageService no encuentra el archivo)
    mocker.patch.object(StorageService, 'load_solution', side_effect=FileNotFoundError("No solution file found"))
    
    # 2. Llamar a la ruta
    # 'follow_redirects=True' hace que el test siga la redirección
    response = client.get('/exportar-pdf', follow_redirects=True)

    # 3. Verificar (Asserts)
    
    # Aterrizamos en la página de inicio
    assert response.status_code == 200 
    
    # Verificamos que el mensaje de error (que pusimos en index.html) SÍ aparece
    assert b"Error al cargar el reporte: No solution file found" in response.data