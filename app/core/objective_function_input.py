import re
import json
import os

class ObjectiveFunctionInput:
    def __init__(self):
        self.coefficients = {}

    def parse_function(self, expression: str):
        """
        Parsea una función objetivo tipo: Z = 3x1 - 5x2 + 0x3
        También permite que el primer coeficiente sea negativo o cero.
        Retorna un diccionario con los coeficientes.
        """
        if not expression.strip():
            raise ValueError("❌ La función objetivo no puede estar vacía.")

        expression = expression.replace(" ", "")
        if "=" in expression:
            expression = expression.split("=")[1]

        # Agregar + delante si el primer término no tiene signo, para simplificar regex
        if expression[0] not in "+-":
            expression = "+" + expression

        # Buscar términos del tipo +3x1, -5x2, 0x3
        pattern = r'([+-]?\d+)\*?x(\d+)'  # permite coeficiente 0
        matches = re.findall(pattern, expression)

        if not matches:
            raise ValueError("❌ Formato inválido. Ejemplo válido: Z = -2x1 + 3x2 + 0x3")

        self.coefficients = {}  # limpiar por si hay datos previos
        for coef, var in matches:
            try:
                self.coefficients[f"x{var}"] = float(coef)
            except ValueError:
                raise ValueError(f"❌ Coeficiente inválido: {coef}")

        # Validar que los índices sean consecutivos (x1, x2, x3, ...)
        indices = sorted(int(v[1:]) for v in self.coefficients.keys())
        for i in range(1, len(indices)):
            if indices[i] != indices[i - 1] + 1:
                raise ValueError("❌ Las variables deben ser consecutivas (por ejemplo x1, x2, x3).")

        return self.coefficients


def get_next_filename(prefix="funcion", extension=".json"):
    number = 1
    while os.path.exists(f"{prefix}{number}{extension}"):
        number += 1
    return f"{prefix}{number}{extension}"


def save_coefficients(coefficients):
    filename = get_next_filename()
    with open(filename, "w") as f:
        json.dump(coefficients, f, indent=4)
    print(f"💾 Función objetivo guardada en {filename}")


def main():
    print("=== Ingreso de Función Objetivo ===")
    print("Ejemplo: Z = -2x1 + 3x2 + 0x3")
    print("----------------------------------")

    service = ObjectiveFunctionInput()
    expresion = input("\nIngrese la función objetivo: ").strip()

    try:
        coef = service.parse_function(expresion)
        print("✅ Función válida. Coeficientes detectados:")
        for var, val in coef.items():
            print(f"  {var}: {val}")
        save_coefficients(coef)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
