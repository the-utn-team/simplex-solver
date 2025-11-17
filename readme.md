# Simplex-solver
Simplex Solver es una aplicación académica desarrollada en el marco de la materia Ingeniería y Calidad de Software de la UTN – Facultad Regional San Rafael. El objetivo es construir una herramienta que permita definir y resolver problemas de programación lineal utilizando el Método Simplex. El proyecto se gestiona bajo la metodología Scrum. El lenguaje que utilizamos es Python, junto con el framework Flask.

## Autores

- [@ItsCaaam](https://www.github.com/itscaaam) Barrera Camila
- [@ivanjcs](https://www.github.com/ivanjcs) Castro Iván
- [@solparejas](https://www.github.com/solparejas) Parejas Sol
- [@Rocio-Caro-Caceres](https://www.github.com/Rocio-Caro-Caceres) Caro Caceres Rocío

## Tecnologías

- **Lenguaje**: Python  
- **Framework Web**: Flask  
- **Contenerización**: Docker  
- **Frontend**: HTML / CSS  

Dependencias principales en `requirements.txt`: Flask, numpy, scipy, gilp, simple-simplex, reportlab, pytest, entre otras.

## Instalación
### Configuración local sin Docker

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

### Confinguración con Docker

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

### Ejecución de Pruebas

1.  Activar el entorno virtual (ver paso 4.1.2).
2.  Ejecutar el siguiente comando desde la raíz del proyecto:
    ```
    pytest
    ```
    (O el comando específico, ej: `python -m unittest discover test`)

## Rutas Clave
* / — Página de inicio
* /new — Crear nuevo problema
* /load — Cargar problema desde JSON
* /solve — Resolver problema
* /exportar-pdf — Descargar solución en PDF
* /descargar-problema-json — Exportar problema actual en JSON

## Documentación Completa
Para información detallada consulte los documentos en /docs
- [Documentación técnica]([https://github.com/the-utn-team/simplex-solver/blob/main/docs/technical_documentation.md]) 
- [Manual de usuario]([https://github.com/the-utn-team/simplex-solver/blob/main/docs/user_manual.md]) 
- [Guía de pruebas]([https://github.com/the-utn-team/simplex-solver/blob/main/docs/testing_guide.md]) 
