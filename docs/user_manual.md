# Manual de Usuario – Simplex Solver

## 1. Introducción

Simplex Solver es una aplicación web diseñada para crear, cargar y resolver problemas de programación lineal utilizando el método Simplex de manera guiada. El objetivo es que cualquier usuario pueda formular un modelo, visualizar las iteraciones del algoritmo y comprender el proceso paso a paso hasta llegar a la solución óptima.

La interfaz está pensada para ser intuitiva y acompañar al usuario desde la creación del problema hasta la interpretación del resultado final, sin necesidad de conocimientos avanzados en programación o herramientas externas.


## 2. Requisitos del sistema

Para utilizar la aplicación Simplex Solver, el usuario solo necesita contar con lo siguiente:


### 2.1 Navegador web compatible

La aplicación funciona correctamente en navegadores modernos:

* Google Chrome
* Microsoft Edge
* Mozilla Firefox

Se recomienda utilizar la versión más reciente para garantizar el funcionamiento óptimo.

### 2.2 Resolución recomendada

* Resolución mínima: **1280 x 720**
* Resolución recomendada: **1920 x 1080**

Esto asegura que las tablas del método Simplex y los formularios se visualicen sin desplazamientos excesivos.

### 2.3 Acceso a la aplicación

El usuario debe acceder mediante la URL correspondiente a la instancia desplegada (local o remota). Si la aplicación está instalada localmente, generalmente se accede a través de:

```
http://localhost:5000
```


## 3. Pantalla principal

Al ingresar a Simplex Solver, el usuario encontrará la pantalla principal, donde se presentan las opciones iniciales para comenzar a trabajar con un problema de programación lineal. La interfaz está diseñada para ser clara y simple.

### 3.1 Elementos principales de la pantalla

#### **a) Botón “Nuevo problema”**

Permite iniciar el proceso de creación de un modelo desde cero. Al seleccionarlo, el usuario será llevado a un formulario donde podrá indicar:

* Cantidad de variables
* Cantidad de restricciones
* Tipo de objetivo (maximizar o minimizar)

Esta es la opción recomendada para usuarios que desean armar un nuevo ejercicio o práctica.

#### **b) Botón “Cargar problema”**

Opción destinada a quienes ya tienen un problema previamente guardado en un archivo compatible. Al seleccionarlo, el sistema permite subir el archivo y continuar desde el punto donde se dejó.

Esta función es útil para retomar trabajos, compartir modelos o cargar ejemplos preparados.


## 4. Crear un nuevo problema

La opción **“Nuevo problema”** permite al usuario construir un modelo de programación lineal desde cero. El proceso está guiado para asegurar que todos los datos necesarios sean ingresados correctamente.

### 4.1 Ingreso de datos iniciales

Al seleccionar esta opción, se muestra un formulario donde el usuario debe completar los siguientes campos:

#### **a) Tipo de objetivo**

El usuario debe seleccionar si el problema busca:

* **Maximizar** (por ejemplo, maximizar ganancias)
* **Minimizar** (por ejemplo, minimizar costos)

#### **b) Ingresar datos**

El usuario puede:
* Ingresar nuevos coeficientes principales.
* Ingresar los coeficientes de la función objetivo.
* Insertar nuevas restricciones.
* Ingresar los coeficientes de las restricciones.
* Seleccionar los signos de desigualdad (≤, =, ≥) según corresponda.

### 4.2 Validaciones

El sistema verifica que:

* Todos los campos estén completos.
* Los valores numéricos sean válidos.
* No existan caracteres no permitidos.

Si algún dato no es correcto, se mostrará un recuadro rojo de error indicando cuál es el campo que debe corregirse.

## 5. Cargar un problema

La opción **“Cargar problema”** permite abrir un modelo previamente guardado en formato `.json`. Esta función es útil para continuar ejercicios, revisar ejemplos o compartir modelos entre usuarios.

### 5.1 Cómo cargar un archivo

Al seleccionar esta opción, el sistema mostrará un botón para elegir un archivo desde el dispositivo. Una vez seleccionado, el sistema validará el contenido y mostrará la pantalla de armado del modelo o la tabla inicial del Simplex, según corresponda.

Si el archivo no cumple con el formato requerido, se mostrará un mensaje indicando el error.

### 5.2 Formato del archivo JSON

El archivo debe contener la estructura exacta utilizada por Simplex Solver para reconstruir el problema. A continuación se muestra el formato esperado:

```json
{
  "objective": {
    "type": "max" | "min",
    "coefficients": [c1, c2, c3]
  },
  "constraints": [
    {
      "coefficients": [a1, a2, a3],
      "sign": "<=" | "=" | ">=",
      "value": b
    }
  ],
  "variable_count": 3,
  "constraint_count": 1
}
```

### 5.3 Descripción del formato

* **objective.type**: indica si el modelo es de maximización (`"max"`) o minimización (`"min"`).
* **objective.coefficients**: lista de coeficientes de la función objetivo.
* **constraints**: lista de restricciones. Cada restricción contiene:

  * `coefficients`: coeficientes de la restricción.
  * `sign`: tipo de desigualdad.
  * `value`: término independiente.
* **variable_count**: cantidad total de variables.
* **constraint_count**: cantidad total de restricciones.

### 5.4 Validaciones al cargar

El sistema revisa que:

* El archivo tenga un JSON válido.
* Todos los campos requeridos existan y tengan valores correctos.
* La cantidad de variables y restricciones coincida con los vectores de coeficientes.

Si la validación es exitosa, el usuario podrá continuar inmediatamente desde la vista correspondiente.

## 6. Previsualización del problema
Después de crear un nuevo problema o cargar un archivo JSON válido, el sistema muestra una **vista de previsualización**. Esta sección permite al usuario confirmar que los datos fueron interpretados correctamente antes de avanzar al método Simplex.

### 6.1 Contenido mostrado en la previsualización
La pantalla incluye:
- **Función objetivo**: tipo (Maximizar/Minimizar) y coeficientes.
- **Restricciones**: todas las ecuaciones con sus coeficientes, signo y valor.
- **Cantidad de variables y restricciones**.

### 6.2 Acciones disponibles
Esta pantalla **no permite editar datos**. Es una vista informativa.

Las acciones disponibles son:
- **Volver**: regresa a la pantalla de creación o carga para corregir cualquier dato.
- **Resolver problema**: avanza a la interfaz del método Simplex.

### 6.3 Cuándo aparece esta vista
- Siempre que se carga un archivo JSON correctamente.
- Luego de completar el formulario de creación de problema.


## 7. Interfaz del método Simplex

La vista del método Simplex presenta información numérica, visual y controles interactivos para facilitar la comprensión del proceso y del resultado. A continuación se explica cada elemento visible en pantalla y su propósito.

### 7.1 Estado y resumen numérico

En la parte superior o en un panel resumen se muestran indicadores rápidos del estado del problema y la solución:

* **Estado:** puede ser “Solución Factible”, “Sin Solución Factible” o “Ilimitado”.
* **Variables:** listado de las variables de decisión con sus valores para la iteración seleccionada (ej.: `x1 = 0.0000`, `x2 = 0.0000`). Son valores de solo lectura.
* **Valor Óptimo (Z):** valor numérico de la función objetivo.

Estos elementos permiten obtener de un vistazo la situación general del modelo sin revisar las tablas.

### 7.2 Visualización geométrica del problema

La aplicación ajusta el tipo de visualización según la cantidad de variables:

* **2 variables:** se muestra una gráfica 2D con:

  * Las rectas de cada restricción y sus zonas factibles.
  * La región factible (si existe).
  * El punto óptimo determinado por el algoritmo.
* **3 variables:** se muestra una gráfica 3D con
  * El espacio factible.
  * El punto óptimo determinado por el algoritmo.
* **4 variables o más:** no es posible la representación geométrica; en su lugar, la interfaz permite visualizar las tablas intermedias del método Simplex.

A un costado de la gráfica se muestran la función objetivo y las restricciones tal como fueron ingresadas.

### 7.3 Controles interactivos: deslizadores

Están disponibles solo cuando existe gráfica (2 o 3 variables).

#### Deslizador de iteraciones

* Permite desplazarse entre las distintas iteraciones del Simplex.
* Al moverlo, se actualizan los valores numéricos de las variables y el valor Z.
* Cuando hay visualización geométrica, se destaca el punto o base correspondiente a esa iteración.

#### Deslizador de valor objetivo (objective value)

* Desplaza una recta o plano de nivel de la función objetivo para diferentes valores de Z.
* Es una herramienta puramente visual: no modifica el modelo ni recalcula iteraciones.

### 7.4 Comportamiento en casos especiales

La aplicación distingue automáticamente los estados especiales del problema y ajusta la visualización:

#### Problema ilimitado

* **Estado:** *Error*
* **Descripción:** “No se encontró una solución factible.”
* **Visualización de tablas:** no disponible.
* **Visualización geométrica:** “Visualización no disponible (Problema infactible o no acotado).”

#### Problema no factible

* **Estado:** *Sin Solución Factible*
* **Descripción:** “No se encontró una solución factible.”
* **Visualización de tablas:** no disponible.
* **Visualización geométrica:** “Visualización no disponible (Problema infactible o no acotado).”


## 8. Exportar y guardar

Simplex Solver permite conservar y reutilizar la información generada tras resolver un problema. Desde esta vista, el usuario puede descargar tanto la definición completa del modelo como la solución en un formato listo para usar.

### 8.1 Descargar el problema en formato JSON

Luego de ejecutar el método Simplex, la aplicación permite descargar un archivo `.json` que contiene:

* La función objetivo
* Las restricciones
* La cantidad de variables y restricciones
* Toda la información necesaria para volver a cargar el problema

#### Cuándo usar esta opción

* Para utilizar el archivo en la opción **Cargar problema**
* Para compartir el modelo con otros usuarios
* Para conservar una copia editable del problema

### 8.2 Exportar la solución en PDF

La aplicación también permite descargar un reporte en formato `.pdf` con los resultados finales del método Simplex, incluyendo:

* El estado del problema.
* El valor óptimo y los valores de las variables.
* Las tablas intermedias.

Este reporte es útil para documentación técnica, trabajos académicos o registro personal.

### 8.3 Ubicación de los botones de descarga

Los botones para descargar tanto el **JSON del problema** como el **PDF de la solución** aparecen en la **vista de resultados** después de finalizar el cálculo. 



## 9. Preguntas frecuentes (FAQ)

**¿Puedo resolver un problema sin conocer el método Simplex?**
Sí. La aplicación guía al usuario paso a paso mostrando iteraciones, pivotes y la tabla final.

**¿Qué formato debe tener el archivo JSON para cargar un problema?**
Debe seguir la estructura indicada en la sección correspondiente:
- `objective` con tipo y coeficientes
- `constraints` con coeficientes, signo y valor
- `variable_count`
- `constraint_count`

**¿La aplicación requiere instalación?**
No para el usuario final; solo se necesita un navegador compatible. La instalación técnica depende del entorno del desarrollador.

**¿Qué hago si la aplicación muestra un error inesperado?**
Generalmente basta con recargar la página o verificar los datos ingresados. Si persiste, intentar cargar un nuevo archivo JSON.

**¿Puedo exportar solo las iteraciones o solo la solución?**
Sí, siempre que la instancia de la aplicación tenga habilitadas dichas opciones.



## 10. Contacto y soporte
Si el usuario necesita asistencia adicional, puede:
- Consultar la documentación técnica del proyecto.
- Contactar al equipo desarrollador a través de la cuenta de github [@the-utn-team](https://www.github.com/the-utn-team).

No se requiere soporte técnico especializado para el uso básico del sistema, pero sí para mantenimiento, instalación o modificaciones del código.
