"""
Módulo core: Lógica de negocio para la Función Objetivo.
"""
import re
from typing import Dict

class ObjectiveFunctionParser:
    """Parsea y valida la expresión de la función objetivo."""

    @staticmethod
    def parse(expression: str) -> Dict[str, float]:
        """
        Parsea una función objetivo tipo: Z = 3x1 - 5x2 + 0x3
        Retorna un diccionario con los coeficientes.
        """
        if not expression.strip():
            raise ValueError("La función objetivo no puede estar vacía.")
        
        expression = expression.replace(" ", "")
        
        if "=" in expression:
            parts = expression.split("=")
            if len(parts) > 1:
                expression = parts[1]
            else:
                expression = parts[0] # Asumir que solo pasaron la parte derecha

        # Agregar + delante si el primer término no tiene signo
        if expression[0] not in "+-":
            expression = "+" + expression

        # Buscar términos del tipo +3x1, -5x2, 0x3, con opcional *
        pattern = r'([+-]?\d+\.?\d*)\*?x(\d+)'
        matches = re.findall(pattern, expression)
        
        if not matches:
            raise ValueError("Formato inválido. Ejemplo válido: Z = -2x1 + 3x2 + 0x3")

        coefficients = {}
        for coef, var in matches:
            try:
                coefficients[f"x{var}"] = float(coef)
            except ValueError:
                raise ValueError(f"Coeficiente inválido: {coef}")
        
        # Validar que los índices sean consecutivos (x1, x2, x3, ...)
        indices = sorted(int(v[1:]) for v in coefficients.keys())
        
        if not indices or indices[0] != 1:
            raise ValueError("Las variables deben comenzar en x1.")

        for i in range(1, len(indices)):
            if indices[i] != indices[i - 1] + 1:
                raise ValueError("Las variables deben ser consecutivas (ej: x1, x2, x3).")
                
        return coefficients