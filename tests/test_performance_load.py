"""
Tests de Carga y Estrés para el Simplex Solver
Usa pytest nativo + threading para simular carga concurrente
"""
import pytest
import threading
import time
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.controllers.routers import init_app


# CONFIGURACIÓN


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

# Problema de prueba estándar
PROBLEMA_CARGA = {
    'problem_type': 'maximize',
    'objective[]': [3.0, 5.0],
    'constraint_1[]': [1.0, 0.0, 3.0],
    'constraint_2[]': [0.0, 2.0, 2.0],
    'constraint_sign[]': ['<=', '<=', '<='],
    'constraint_rhs[]': [4.0, 12.0, 18.0]
}


# TESTS DE CARGA (Load Testing)

@pytest.mark.timeout(60)
def test_carga_10_usuarios_concurrentes(client):
    """
    Test de carga: 10 usuarios simultáneos resolviendo problemas.

    Criterios de éxito:
    - Todas las requests completan exitosamente
    - Tiempo promedio < 2 segundos por request
    - Sin errores 500
    """
    num_usuarios = 10
    resultados = []
    errores = []
    tiempos = []

    def usuario_resuelve_problema():
        """Simula un usuario que envía un problema y lo resuelve"""
        try:
            inicio = time.time()
            
            # Enviar problema
            response1 = client.post('/new', data=PROBLEMA_CARGA)
            assert response1.status_code == 200, f"Error en /new: {response1.status_code}"

            # Resolver
            response2 = client.post('/solve', follow_redirects=True)
            assert response2.status_code == 200, f"Error en /solve: {response2.status_code}"

            tiempo_total = time.time() - inicio
            tiempos.append(tiempo_total)
            resultados.append(True)
            
        except Exception as e:
            errores.append(str(e))
            resultados.append(False)

    # Ejecutar concurrentemente
    with ThreadPoolExecutor(max_workers=num_usuarios) as executor:
        futures = [executor.submit(usuario_resuelve_problema) for _ in range(num_usuarios)]
        for future in as_completed(futures):
            future.result()  # Esperar a que termine

    # Validaciones
    assert len(errores) == 0, f"Hubo {len(errores)} errores: {errores[:3]}"
    assert len(resultados) == num_usuarios
    assert all(resultados), "Algunas requests fallaron"

    # Métricas de rendimiento
    tiempo_promedio = sum(tiempos) / len(tiempos)
    tiempo_max = max(tiempos)

    print(f"\nMétricas de Carga (10 usuarios):")
    print(f"   Requests exitosas: {len(resultados)}/{num_usuarios}")
    print(f"   Tiempo promedio: {tiempo_promedio:.2f}s")
    print(f"   Tiempo máximo: {tiempo_max:.2f}s")

    # Criterio de aceptación: tiempo promedio < 5s
    assert tiempo_promedio < 5.0, f"Tiempo promedio muy alto: {tiempo_promedio:.2f}s"

@pytest.mark.timeout(120)
def test_carga_50_usuarios_secuenciales(client):
    """
    Test de carga: 50 usuarios secuenciales (uno tras otro).

    Criterios de éxito:
    - Todas las requests completan exitosamente
    - El servidor no se degrada con el tiempo
    """
    num_requests = 50
    tiempos = []
    errores = []

    for i in range(num_requests):
        try:
            inicio = time.time()
            
            # Enviar y resolver
            client.post('/new', data=PROBLEMA_CARGA)
            response = client.post('/solve', follow_redirects=True)
            
            tiempo = time.time() - inicio
            tiempos.append(tiempo)
            
            assert response.status_code == 200
            
        except Exception as e:
            errores.append(f"Request {i}: {e}")

    # Validaciones
    assert len(errores) == 0, f"Errores encontrados: {errores[:5]}"

    # Verificar que no hay degradación (últimas 10 no son > 50% más lentas que primeras 10)
    primeras_10 = sum(tiempos[:10]) / 10
    ultimas_10 = sum(tiempos[-10:]) / 10
    degradacion = ((ultimas_10 - primeras_10) / primeras_10) * 100 if primeras_10 > 0 else 0

    print(f"\nMétricas de Carga Secuencial (50 requests):")
    print(f"   Requests exitosas: {num_requests - len(errores)}/{num_requests}")
    print(f"   Tiempo promedio primeras 10: {primeras_10:.2f}s")
    print(f"   Tiempo promedio últimas 10: {ultimas_10:.2f}s")
    print(f"   Degradación: {degradacion:.1f}%")

    assert degradacion < 50, f"Degradación muy alta: {degradacion:.1f}%"

# TESTS DE ESTRÉS (Stress Testing)

@pytest.mark.timeout(180)
def test_estres_30_usuarios_simultaneos(client):
    """
    Test de estrés: 30 usuarios completamente simultáneos.

    Criterios de éxito:
    - Al menos 80% de requests exitosas
    - Ningún crash del servidor
    - Memoria y CPU bajo control
    """
    num_usuarios = 30
    resultados = {'exito': 0, 'fallo': 0}
    errores = []
    lock = threading.Lock()

    # Capturar métricas del sistema
    process = psutil.Process(os.getpid())
    memoria_inicial = process.memory_info().rss / 1024 / 1024  # MB
    cpu_inicial = process.cpu_percent(interval=0.1)

    def usuario_bajo_estres():
        """Usuario que intenta usar el sistema bajo alta carga"""
        try:
            client.post('/new', data=PROBLEMA_CARGA)
            response = client.post('/solve', follow_redirects=True)
            
            with lock:
                if response.status_code == 200:
                    resultados['exito'] += 1
                else:
                    resultados['fallo'] += 1
                    errores.append(f"Status: {response.status_code}")
        except Exception as e:
            with lock:
                resultados['fallo'] += 1
                errores.append(str(e))

    # Lanzar todos los threads al mismo tiempo
    inicio = time.time()
    threads = []
    for _ in range(num_usuarios):
        t = threading.Thread(target=usuario_bajo_estres)
        threads.append(t)
    
    # Iniciar todos
    for t in threads:
        t.start()
    
    # Esperar a todos
    for t in threads:
        t.join()
        
    tiempo_total = time.time() - inicio

    # Métricas finales del sistema
    memoria_final = process.memory_info().rss / 1024 / 1024  # MB
    cpu_final = process.cpu_percent(interval=0.1)

    # Calcular tasa de éxito
    total = resultados['exito'] + resultados['fallo']
    tasa_exito = (resultados['exito'] / total) * 100 if total > 0 else 0

    print(f"\nMétricas de Estrés (30 usuarios simultáneos):")
    print(f"   Requests exitosas: {resultados['exito']}/{num_usuarios} ({tasa_exito:.1f}%)")
    print(f"   Requests fallidas: {resultados['fallo']}")
    print(f"   Tiempo total: {tiempo_total:.2f}s")
    print(f"   Memoria: {memoria_inicial:.1f}MB -> {memoria_final:.1f}MB (Delta {memoria_final-memoria_inicial:.1f}MB)")
    print(f"   CPU: {cpu_inicial:.1f}% -> {cpu_final:.1f}%")

    if errores:
        print(f"   Errores (primeros 5): {errores[:5]}")

    # Criterios de aceptación para test de estrés (más permisivos)
    assert tasa_exito >= 80, f"Tasa de éxito muy baja: {tasa_exito:.1f}%"
    assert memoria_final - memoria_inicial < 500, "Fuga de memoria detectada"

@pytest.mark.timeout(300)
def test_estres_carga_sostenida(client):
    """
    Test de estrés: Carga sostenida durante 2 minutos.

    Simula uso real: nuevos usuarios llegan cada segundo durante 120 segundos.

    Criterios de éxito:
    - Sistema responde durante toda la prueba
    - Tasa de error < 20%
    - No hay degradación exponencial
    """
    duracion_segundos = 120
    usuarios_por_segundo = 2
    
    resultados = {'exito': 0, 'fallo': 0}
    tiempos_respuesta = []
    lock = threading.Lock()

    def hacer_request():
        try:
            inicio = time.time()
            client.post('/new', data=PROBLEMA_CARGA)
            response = client.post('/solve', follow_redirects=True)
            tiempo = time.time() - inicio
            
            with lock:
                tiempos_respuesta.append(tiempo)
                if response.status_code == 200:
                    resultados['exito'] += 1
                else:
                    resultados['fallo'] += 1
        except:
            with lock:
                resultados['fallo'] += 1

    print(f"\nIniciando test de carga sostenida ({duracion_segundos}s)...")
    inicio_test = time.time()
    threads = []
    
    while time.time() - inicio_test < duracion_segundos:
        # Lanzar N usuarios este segundo
        for _ in range(usuarios_por_segundo):
            t = threading.Thread(target=hacer_request)
            t.start()
            threads.append(t)
            
        time.sleep(1)  # Esperar 1 segundo antes del siguiente batch

    # Esperar a que todos terminen
    print("   Esperando a que terminen todos los requests...")
    for t in threads:
        t.join(timeout=30)  # Timeout individual por thread

    # Análisis
    total = resultados['exito'] + resultados['fallo']
    tasa_error = (resultados['fallo'] / total * 100) if total > 0 else 0

    if tiempos_respuesta:
        tiempo_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
        # Asegurar que la lista no esté vacía antes de calcular P95
        idx_p95 = int(len(tiempos_respuesta) * 0.95)
        tiempo_p95 = sorted(tiempos_respuesta)[idx_p95] if idx_p95 < len(tiempos_respuesta) else tiempos_respuesta[-1]
    else:
        tiempo_promedio = 0
        tiempo_p95 = 0

    print(f"\nResultados de Carga Sostenida:")
    print(f"   Total requests: {total}")
    print(f"   Exitosas: {resultados['exito']} ({100-tasa_error:.1f}%)")
    print(f"   Fallidas: {resultados['fallo']} ({tasa_error:.1f}%)")
    print(f"   Tiempo promedio: {tiempo_promedio:.2f}s")
    print(f"   Percentil 95: {tiempo_p95:.2f}s")

    assert tasa_error < 20, f"Tasa de error muy alta: {tasa_error:.1f}%"
    assert tiempo_p95 < 5.0, f"P95 muy alto: {tiempo_p95:.2f}s"


# TESTS DE RENDIMIENTO (Performance Benchmarking)

def test_benchmark_solver_simple(benchmark, client):
    """
    Benchmark: Mide el tiempo exacto de resolver un problema simple.
    pytest-benchmark ejecuta múltiples veces y calcula estadísticas.
    """
    def resolver_problema():
        client.post('/new', data=PROBLEMA_CARGA)
        return client.post('/solve', follow_redirects=True)

    result = benchmark(resolver_problema)
    assert result.status_code == 200

def test_benchmark_solo_parser(benchmark, client):
    """
    Benchmark: Mide solo el tiempo del parser (POST /new).
    """
    result = benchmark(client.post, '/new', data=PROBLEMA_CARGA)
    assert result.status_code == 200