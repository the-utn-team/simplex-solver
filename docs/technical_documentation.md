# Documentación Técnica — Simplex Solver

## 1. Descripción General

Simplex Solver es una aplicación académica desarrollada en el marco de la materia Ingeniería y Calidad de Software de la UTN – Facultad Regional San Rafael. El objetivo es construir una herramienta que permita definir y resolver problemas de programación lineal utilizando el Método Simplex. El proyecto se gestiona bajo la metodología Scrum. El lenguaje que utilizamos es Python, junto con el framework Flask.

## 2. Tecnologías Utilizadas

Lista de herramientas, lenguajes y librerías que soportan la aplicación.

* **Lenguaje**: Python
* **Contenerización**: Docker
* **Web**: Flask, HTML, CSS

### Dependencias Principales (`requirements.txt`)

Las librerías de Python se agrupan por su funcionalidad:

**Framework Web**
* `Flask==3.1.2`

**Cálculo y Ciencia de Datos**
* `numpy==1.26.4`
* `scipy==1.12.0`

**Solvers Simplex**
* `gilp==2.1.0`
* `simple-simplex==0.0.3`

**Reportes (PDF)**
* `reportlab==4.2.0`

**Tests (Base)**
* `pytest==7.4.0`
* `pytest-mock==3.14.0`
*  `beautifulsoup4==4.14.2`

**Pruebas de Rendimiento y Estrés**
* `psutil==7.1.3`
* `pytest-benchmark==4.0.0`
* `pytest-timeout==2.3.1`


## 3. Estructura del Proyecto

```
/app
  /controllers
  /core
  /services
  /utils
/docs
/outputs
/static
/templates
/test
/uploads

docker-compose.yml
Dockerfile
app.py
web_app.py
requirements.txt
readme.md
```

- **/app/controllers**
Gestiona las rutas y actúa como puente entre la interfaz y la lógica del backend.

* **/app/core**
Contiene la lógica matemática principal del método Simplex.

* **/app/services**
Servicios auxiliares: validaciones, procesamiento de archivos y manejo de datos.

* **/app/utils**
Funciones utilitarias y módulos de apoyo reutilizables.

* **/docs**
Incluye el manual de usuario y el manual de test.

* **/outputs**
JSON generados por la aplicación (problemas, restricciones, soluciones).

* **/static**
Archivos estáticos como hojas de estilo.

* **/templates**
Plantillas HTML usadas para las vistas de Flask.

* **/test**
Pruebas del sistema.

* **/uploads**
Archivos JSON cargados por el usuario.

* **Archivos raíz**
  * **docker-compose.yml**: Orquestación de contenedores.
  * **Dockerfile**: Construcción de la imagen Docker.
  * **app.py**: Configuración general.
  * **web_app.py**: Punto de entrada principal.
  * **requirements.txt**: Dependencias.
  * **readme.md**: Descripción general del proyecto.


## 4. Configuración del entorno y ejecución de la Aplicación

### 4.1 Configuración local sin Docker

1. Clonar el repositorio
```
git clone <URL_DEL_REPOSITORIO>
cd simplex-solver
```

2. Crear y activar entorno virtual
```
python -m venv venv
# Windows
venv\Scripts\Activate1.ps1
# Linux / Mac
source venv/bin/Activate.ps1
```

3. Instalar dependencias
```
pip install -r requirements.txt
```

4. Ejecutar la aplicación
```
pip install -r requirements.txt
python web_app.py
```
La aplicación estará disponible en ```http://localhost:5000```


### 4.2 Confinguración con Docker

1. Construir y levantar contenedores
```
docker-compose up --build
```

2. Acceder a la aplicación
Abrir el navegador en ```http://localhost:5000```

3. Detener contenedores
```
docker-compose down
```

### 4.3 Ejecución de Pruebas

Para asegurar la integridad del código, la carpeta `/test` contiene las pruebas unitarias, de integración, carga y estres

1.  Activar el entorno virtual (ver paso 4.1.2).
2.  Ejecutar el siguiente comando desde la raíz del proyecto:
    ```
    pytest
    ```
    (O el comando específico, ej: `python -m unittest discover test`)

## 5. Flujos Principales del Sistema

### 5.1 Crear un nuevo problema

1. El usuario accede a **/new**.
2. La aplicación muestra un formulario para ingresar la función objetivo y restricciones.
3. El usuario completa los campos y envía el formulario.
4. El backend construye la estructura del problema y la almacena temporalmente.
5. Se muestra una vista previa del problema antes de resolverlo.

### 5.2 Cargar un problema desde archivo JSON

1. El usuario accede a **/load** y selecciona un archivo `.json`.
2. El backend valida la estructura del archivo.
3. Si es válido, se carga el problema y se muestra en pantalla.
4. El usuario puede editarlo o resolverlo directamente.

### 5.3 Resolver un problema

1. El usuario confirma el problema cargado o creado.
2. El sistema envía la definición a la lógica del método Simplex.
3. Se ejecuta el solver y se genera un archivo de **solución**.
4. El resultado incluye:

   * Estado (óptimo, no factible, ilimitado)
   * Valores de las variables
   * Valor óptimo de Z
   * Mensaje del solver
5. El usuario puede:

   * Ver la solución en pantalla
   * Descargar el JSON de la solución
   * Exportar la solución a PDF


## 6. Rutas Principales

La aplicación expone un conjunto de rutas centrales que conforman el flujo operativo principal del usuario. Cada una cumple una función específica dentro del proceso de definición, carga, resolución y exportación de problemas del método Simplex.

```/``` **— Página de inicio**

Presenta la interfaz inicial desde la cual el usuario puede crear un nuevo problema o cargar uno existente.

```/new``` **— Crear nuevo problema**

Permite definir un problema desde cero ingresando la función objetivo, las restricciones y el tipo de optimización.

```/load``` **— Cargar problema**

Habilita la carga de archivos JSON previamente generados por la aplicación, reconstruyendo automáticamente el problema para su edición o resolución.

```/solve``` **— Resolver problema**

Ejecuta el proceso de optimización utilizando el método Simplex y muestra la solución obtenida, incluyendo valores óptimos y estado del solver.

```/exportar-pdf``` **— Descargar solución en PDF**

Genera y permite descargar un archivo PDF con la solución completa del problema resuelto.

```/descargar-problema-json``` **— Exportar problema en JSON**

Descarga el problema actual en formato JSON para su reutilización mediante la opción de carga.

## 7. Formato de Archivos JSON Generados

La estructura de los archivos generados y consumidos por la app es la siguiente:

### Función Objetivo

```
{
    "type": "maximize",
    "coefficients": {
        "x1": 1.0,
        "x2": 1.0,
        "x3": 4.0
    }
}
```

### Problema Completo

```
{
    "problema_definicion": {
        "funcion_objetivo": {
            "type": "maximize",
            "coefficients": {
                "x1": 2.0,
                "x2": 3.0
            }
        },
        "restricciones": [
            {
                "coefficients": {
                    "x1": 2.0,
                    "x2": 1.0
                },
                "operator": "<=",
                "rhs": 24.0
            },
            {
                "coefficients": {
                    "x1": 1.0,
                    "x2": 3.0
                },
                "operator": "<=",
                "rhs": 43.0
            }
        ]
    }
}
```

### Restricciones

```
[
    {
        "coefficients": {
            "x1": 1.0,
            "x2": 2.0,
            "x3": 0.0
        },
        "operator": "<=",
        "rhs": 10.0
    },
    {
        "coefficients": {
            "x2": 1.0,
            "x3": 3.0,
            "x1": 0.0
        },
        "operator": "<=",
        "rhs": 30.0
    }
]
```

### Solución

```
{
    "problema_definicion": {
        "funcion_objetivo": {
            "type": "maximize",
            "coefficients": {
                "x1": 1.0,
                "x2": 1.0,
                "x3": 4.0
            }
        },
        "restricciones": [
            {
                "coefficients": {
                    "x1": 1.0,
                    "x2": 2.0,
                    "x3": 0.0
                },
                "operator": "<=",
                "rhs": 10.0
            },
            {
                "coefficients": {
                    "x2": 1.0,
                    "x3": 3.0,
                    "x1": 0.0
                },
                "operator": "<=",
                "rhs": 30.0
            }
        ]
    },
    "solucion_encontrada": {
        "status": "Solucion Factible",
        "mensaje_solver": "Optimization terminated successfully. (HiGHS Status 7: Optimal)",
        "valores_variables": {
            "x1": 10.0,
            "x2": 0.0,
            "x3": 10.0
        },
        "valor_optimo_z": 50.0
    }
}
```

## 8. Pruebas

Simplex Solver cuenta con pruebas unitarias, de integración y de rendimiento. Cubren validación de inputs, lógica de control, almacenamiento, generación de reportes y comportamiento bajo carga y estrés. Se utilizan mocks, fixtures y clientes de prueba para asegurar aislamiento y repetibilidad. Los detalles de cada suite se documentan en un archivo separado.

Para información detallada consulte ```/docs/testing_guide.md```

## 9. Manejo de Errores y Casos Borde

### 9.1 Estados del Solver

El campo `status` dentro de `solucion_encontrada` informa el resultado de la optimización. Los valores principales son:

-   **"Solucion Factible" / "Optimal"**: El solver encontró la solución óptima.
    
-   **"Infactible" / "Infeasible"**: El problema no tiene solución; las restricciones son contradictorias.
    
-   **"Ilimitado" / "Unbounded"**: El problema no está acotado y la función objetivo puede crecer (o decrecer) infinitamente.
    

### 9.2 Validación de Entrada

La ruta `/load` (POST) valida que el archivo JSON subido cumpla con la estructura definida en la sección 7.1. Si el formato es incorrecto, el sistema devolverá un mensaje de error al usuario y no cargará el problema.

## 10. Autores

- [@ItsCaaam](https://www.github.com/itscaaam) Barrera Camila
- [@ivanjcs](https://www.github.com/ivanjcs) Castro Iván
- [@solparejas](https://www.github.com/solparejas) Parejas Sol
- [@Rocio-Caro-Caceres](https://www.github.com/Rocio-Caro-Caceres) Caro Caceres Rocío
