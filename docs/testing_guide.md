# Guía de Pruebas Unitarias e Integración para Simplex Solver

## Introducción

Esta guía detalla la implementación y el propósito de cada suite de pruebas en el proyecto Simplex Solver, con énfasis en su cobertura, lógica de verificación y resolución de consideraciones técnicas clave. Cada sección por archivo integra explicaciones sobre el comportamiento de los tests, incluyendo el uso de mocks para simular dependencias externas, el manejo de excepciones para validar errores esperados, y la verificación indirecta de componentes como gilp (que genera HTML interactivo con Plotly, donde se confirma la presencia de elementos como contenedores y variables en lugar de parsear JavaScript para iteraciones, ya que esto simula el comportamiento end-to-end sin complejidad innecesaria). Todos los tests evitan outputs reales mediante mocks o tmpdir para mantener la determinismo y velocidad, alineándose con prácticas estándar de testing que priorizan la independencia de estados externos.

pytest -v y pasan consistentemente en entornos Python 3.12+.

## test_constraints.py: Pruebas Unitarias para Parsing y Validación de Constraints

Esta suite verifica el núcleo del parsing de restricciones y su validación, cubriendo expresiones válidas e inválidas, consistencia de variables y serialización. Utiliza parametrización para eficiencia, probando múltiples escenarios con un solo test. El manejo de excepciones se realiza mediante pytest.raises(ValueError, match=...), que no solo confirma el lanzamiento de errores sino también el mensaje preciso, asegurando que el parser rechace inputs malformados de manera informativa (por ejemplo, diferenciando "vacío" de "duplicado").

-   **test_parse_valid_expressions**: Parametrizado con 7 casos (incluyendo multiplicación explícita con "*", negativos y RHS cero), verifica que el parser extraiga correctamente coeficientes, operador y RHS de expresiones como "2x1 + 3x2 <= 10". Cubre edge cases como decimales implícitos y coeficientes cero, confirmando que el output es un diccionario exacto sin dependencias externas.
    
-   **test_parse_invalid_expressions**: Parametrizado con 13 casos de error, prueba rechazos para inputs vacíos, operadores inválidos (ej: ">>"), números no válidos o términos no reconocidos. Integra excepciones con match para mensajes como "no puede estar vacía" o "Variable duplicada: x1", resolviendo dudas sobre validación al demostrar que el parser falla graceful sin propagar errores inesperados.
    
-   **test_validator_consecutive_valid**: Confirma que variables consecutivas (ej: x1, x2) pasan sin excepción, validando el set de coeficientes directamente.
    
-   **test_validator_consecutive_invalid_gap**: Lanza ValueError para gaps (ej: x1, x3), con match "Falta la variable x2", ilustrando cómo el validador previene inconsistencias en el modelo lineal.
    
-   **test_validator_consecutive_invalid_start**: Similar, falla si no inicia en x1 (ej: x2, x3), con match "debe comenzar en x1", asegurando alineación con el solver.
    
-   **test_validator_set_consistency_valid**: Verifica consistencia entre múltiples constraints (ej: mismas variables), retornando True sin excepción.
    
-   **test_validator_set_consistency_invalid**: Lanza ValueError para sets inconsistentes (ej: x1/x2 vs. x1/x3), con match "Inconsistencia de variables", probando post-procesamiento sin mocks ya que usa objetos Constraint reales.
    
-   **test_constraint_serialization**: Prueba round-trip de Constraint a dict y viceversa, verificando preservación de datos para persistencia JSON.
    
-   **test_parse_edge_cases**: Parametrizado con 2 casos límite (decimales, -0.0), extiende el parsing válido para robustez.
    
-   **test_validator_set_consistency_empty**: Confirma que sets vacíos son válidos (retorna True), manejando casos sin restricciones.
    

Esta suite resuelve dudas sobre parsing al demostrar aislamiento total (sin I/O), con excepciones que guían debugging.

## test_controllers.py: Pruebas Unitarias para Controladores de Input

Enfocada en flujos interactivos de entrada (función objetivo y constraints), esta suite mockea input para simular usuarios y verifica guardado vía fixture mock_storage_save. Integra manejo de reintentos y validaciones, usando side_effect para secuencias de respuestas. Las excepciones se mockean en validadores para probar flujos de error sin crashes reales.

-   **test_objective_controller_valid_input**: Mockea input para "max" y expresión válida ("Z = 2x1 - 3x2 + 0x3"), verificando coeficientes output y guardado implícito. Resuelve dudas sobre mocks al mostrar cómo simula interacciones sin consola real.
    
-   **test_objective_controller_invalid_then_valid**: Secuencia inválida seguida de "min" y expresión válida; confirma reintento y output correcto, probando resiliencia (Issue #6 resuelto con prompt explícito para tipo).
    
-   **test_constraints_controller_valid_inputs**: Mockea inputs para 2 constraints válidas ("2x1 + 3x2 <= 10", "1x1 >= 5") y "fin"; verifica longitud de lista y operadores, asegurando append correcto.
    
-   **test_constraints_controller_invalid_input**: Ignora inválido ("invalid"), agrega solo el siguiente válido; confirma longitud 1, demostrando loop tolerante.
    
-   **test_constraints_controller_no_constraints**: Input directo "fin"; verifica lista vacía, sin guardado.
    
-   **test_constraints_controller_inconsistency_error**: Inputs válidos seguidos de ValueError mockeado en validador; verifica append pero no guardado final, integrando excepciones para probar manejo post-loop.
    

La suite usa mocks para input/guardado, evitando outputs reales y enfocándose en lógica de control.

## test_objective_function.py: Pruebas Unitarias para Parsing de Función Objetivo

Suite minimalista para `ObjectiveFunctionParser`, cubriendo sintaxis y validaciones con asserts directos y excepciones `match`. Resuelve dudas sobre consecutividad al probar fallos específicos sin mocks externos.

-   **test_valid_input**: Parsing "Z = 3x1 - 5x2 + 0x3"; output exacto con coefs.
    
-   **test_no_z**: Sin "Z"; confirma implícito.
    
-   **test_negative_first**: "-3x1 + 5x2"; maneja negativos iniciales.
    
-   **test_with_star**: "3*x1"; soporta multiplicación explícita.
    
-   **test_invalid_format**: "Z = 3a + b"; ValueError con "Formato inválido".
    
-   **test_non_consecutive_variables**: "Z = 3x1 + 5x3"; ValueError con "consecutivas".
    
-   **test_starts_with_x2**: "Z = 3x2 + 5x3"; ValueError con "comenzar en x1".
    

Tests puros, ideales para lógica de parsing.

## test_solver_controller.py: Pruebas Unitarias para Solver Principal

Verifica preparación de modelo y flujos `run()`, usando mocks para la carga de datos (pasados al `__init__`) y `capsys` para capturar `print`. Integra `pytest.approx` para floats y mocks de `linprog` y `_generate_visualization...` para simular resultados del solver y la visualización.

-   **test_prepare_model_for_scipy_maximize**: Carga mockeada; verifica matrices negadas para max (c=[-15,-18]).
    
-   **test_prepare_model_for_scipy_minimize**: Asigna datos manual; invierte filas para >= (A_ub negativos).
    
-   **test_run_success_maximize**: Mock `linprog` y `_generate_visualization...`; verifica prints (x1=388.8889, Z=9833.3333) y reporte guardado (approx para precisión).
    
-   **test_run_success_minimize**: Similar para min (Z=108.6957 positivo); confirma status y valores.
    
-   **test_run_infeasible**: `Linprog` mockeado para fallar; verifica print "Sin Solucion Factible" y `None` en Z del reporte.
    
-   **test_run_load_data_fails**: Instancia el controller con un `problem_data_wrapper` vacío; verifica mensaje de error ("Error: El solver no recibió datos válidos") y que `save_solution` no fue llamado.
    

Cobertura del 100% del flujo `run()`, con mocks para aislamiento total de dependencias externas.

## test_performance_load.py: Pruebas de Carga, Estrés y Rendimiento

(Sección Nueva)

Esta suite evalúa la estabilidad y velocidad de la aplicación bajo concurrencia. Utiliza un enfoque nativo de Pytest sin dependencias externas complejas, combinando `threading` (para simular usuarios), `psutil` (para monitorear recursos) y `pytest-benchmark` (para mediciones precisas).

-   **test_carga_10_usuarios_concurrentes**: Simula 10 usuarios simultáneos (vía `ThreadPoolExecutor`) que envían y resuelven un problema. Valida que todas las peticiones sean exitosas y que el tiempo de respuesta promedio se mantenga bajo el umbral aceptable (ej. < 10.0s).
    
-   **test_carga_50_usuarios_secuenciales**: Ejecuta 50 peticiones, una tras otra, para asegurar que el servidor no sufra degradación de rendimiento. Compara el tiempo promedio de las primeras 10 peticiones con las últimas 10.
    
-   **test_estres_30_usuarios_simultaneos**: Lanza 30 hilos (`threading.Thread`) de forma concurrente para estresar el servidor. Mide la tasa de éxito (debe ser >= 80%) y usa `psutil` para verificar que el consumo de memoria (RSS) y CPU se mantenga en límites razonables.
    
-   **test_estres_carga_sostenida**: Simula una carga constante (ej. 2 usuarios por segundo) durante un período prolongado (120 segundos) para probar la estabilidad a largo plazo. Valida la tasa de error total y el percentil 95 del tiempo de respuesta.
    
-   **test_benchmark_solver_simple**: Usa `pytest-benchmark` para medir con precisión estadística el tiempo del flujo completo `/new` -> `/solve`.
    
-   **test_benchmark_solo_parser**: Usa `pytest-benchmark` para aislar y medir el rendimiento de la ruta `/new` (parsing y guardado en `session`).
    

## test_storage_service.py: Pruebas Unitarias para Almacenamiento

Usa `tmpdir` para simular I/O sin outputs reales. Verifica serialización JSON y manejo graceful de errores.

-   **test_save_objective_function**: Guarda dict; lee y confirma igualdad.
    
-   **test_save_constraints**: Serializa constraints; verifica coefs en JSON.
    
-   **test_save_json_error**: IOError mockeado; retorna None sin crash.
    

Excepciones como IOError se manejan internamente, probando resiliencia.

## test_visualization_integration.py: Pruebas de Integración para Visualización

Evalúa flujos Flask + `gilp` con `client` y `tmpdir`. Verifica HTML con `BeautifulSoup`, enfocándose en verificación indirecta para `gilp` (presencia de 'plotly', variables en HTML, sin parsear JS). Resuelve dudas sobre `gilp` al confirmar que se genera HTML válido con inputs correctos, asumiendo que la librería es confiable. Los tests unitarios del `SolverController` mockean la generación de visualización para aislar la lógica del controlador.

-   **test_flujo_completo_visualizacion_maximizacion**: POST `/new` y `/solve`; verifica preview (coef 3), solución (x1=2, Z=36) y el contenedor de visualización (mockeado).
    
-   **test_tablas_simplex_coinciden_con_calculos_internos**: Ejecuta `solver.run()` (con mocks); verifica reporte (x1=2, Z=36) y HTML (mockeado), alineando cálculos con visualización.
    
-   **test_visualizacion_problema_minimizacion**: POST para min; confirma Z=14 y contenedor.
    
-   **test_visualizacion_con_restricciones_igualdad**: "=" convertido; verifica no-errores en HTML.
    
-   **test_visualizacion_problema_infactible**: Status infactible; HTML contiene "Visualización no disponible".
    
-   **test_verificar_estructura_html_visualizacion**: Verifica que el mock `div id='plotly-test'` se renderiza.
    
-   **test_integracion_css_con_visualizacion**: Confirma presencia de `.gilp-container` y link a `style.css`.
    
-   **test_regresion_problema_sin_restricciones**: Unbounded; no crashea, 'solucion_encontrada' presente con status 'Error'.
    
-   **test_regresion_coeficientes_cero**: Coefs 0; verifica valores (x1=0).
    
-   **test_performance_visualizacion_problema_grande**: 3 vars; no falla, HTML presente.
    
-   **test_solucion_contiene_datos_problema_original**: Reporte incluye input original