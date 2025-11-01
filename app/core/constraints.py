"""
Módulo core: Lógica de negocio para las Restricciones.
"""
import re
from typing import Dict, List

class Constraint:
    """Representa una única restricción: Coeficientes, Operador y Lado Derecho (RHS)."""
    
    def __init__(self, coefficients: Dict[str, float], operator: str, rhs: float):
        self.coefficients = coefficients
        self.operator = operator
        self.rhs = rhs

    def to_dict(self) -> Dict:
        """Convierte la restricción a un diccionario simple para serialización."""
        return {
            "coefficients": self.coefficients,
            "operator": self.operator,
            "rhs": self.rhs
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Constraint':
        """Crea una instancia de Constraint desde un diccionario."""
        return cls(
            coefficients=data.get("coefficients", {}),
            operator=data.get("operator", "="),
            rhs=data.get("rhs", 0.0)
        )

class ConstraintsParser:
    """Servicio de parsing. Transforma un string en un objeto Constraint."""
    
    VALID_OPERATORS = ["<=", ">=", "="]
    
    @staticmethod
    def parse(expression: str) -> Constraint:
        """
        Parsea una expresión de restricción (ej: "2x1 - 3x2 <= 10").

        Raises:
            ValueError: Si el formato, operador, RHS o variables son inválidos.
        """
        if not expression or not expression.strip():
            raise ValueError("La restricción no puede estar vacía.")

        expression_cleaned = expression.replace(" ", "")
        
        # 1. Encontrar operador y separar
        operator = None
        parts = None
        for op in ConstraintsParser.VALID_OPERATORS:
            if op in expression_cleaned:
                parts = expression_cleaned.split(op)
                if len(parts) == 2:
                    operator = op
                    break
        
        if not operator or not parts or len(parts) != 2:
            raise ValueError(f"Formato inválido. Debe contener un operador válido: {', '.join(ConstraintsParser.VALID_OPERATORS)}")

        left_side, right_side = parts

        # 2. Parsear Lado Derecho (RHS)
        try:
            rhs_value = float(right_side)
        except ValueError:
            raise ValueError(f"El lado derecho (RHS) debe ser un número válido. Se recibió: '{right_side}'")

        # 3. Parsear Lado Izquierdo (Coeficientes)
        coefficients = ConstraintsParser._parse_left_side(left_side)

        return Constraint(coefficients, operator, rhs_value)

    @staticmethod
    def _parse_left_side(left_side: str) -> Dict[str, float]:
        """Parsea el lado izquierdo (ej: "+2x1-1.5x2") a un diccionario."""
        if not left_side:
            raise ValueError("El lado izquierdo de la restricción está vacío.")

        # Asegurar que el primer término tenga signo para facilitar el regex
        if left_side[0] not in "+-":
            left_side = "+" + left_side

        # Regex: Captura (signo y coeficiente opcional)x(indice)
        # Permite: +2x1, -x2 (captura -1), +3.5x3
        pattern = r'([+-]?\d*\.?\d*)\*?x(\d+)'
        matches = re.findall(pattern, left_side)
        
        if not matches:
            raise ValueError("Formato inválido en el lado izquierdo. Ejemplo válido: 2x1 + 3x2")

        coefficients = {}
        original_terms = "".join([term[0].replace("*","") + "x" + term[1] for term in matches])
        
        # Verificar que el regex cubrió toda la expresión
        if original_terms != left_side.replace("*", ""):
                 raise ValueError("Formato inválido. Contiene términos no reconocidos.")

        for coef_str, var_index in matches:
            var_name = f"x{var_index}"
            
            # Manejar coeficientes implícitos (ej: +x1 -> +1, -x2 -> -1)
            if coef_str == '+':
                coef_value = 1.0
            elif coef_str == '-':
                coef_value = -1.0
            else:
                try:
                    coef_value = float(coef_str)
                except ValueError:
                    raise ValueError(f"Coeficiente inválido: '{coef_str}'")
            
            if var_name in coefficients:
                raise ValueError(f"Variable duplicada: {var_name}")
                
            coefficients[var_name] = coef_value
            
        return coefficients


class ConstraintsValidator:
    """Validaciones de negocio sobre las restricciones."""

    @staticmethod
    def validate_consecutive_variables(coefficients: Dict[str, float]):
        """Valida que las variables sean x1, x2, x3... sin saltos."""
        if not coefficients:
            return # Vacío es válido

        indices = sorted([int(var[1:]) for var in coefficients.keys()])
        
        if indices[0] != 1:
            raise ValueError("La numeración de variables debe comenzar en x1.")

        for i in range(len(indices) - 1):
            if indices[i+1] != indices[i] + 1:
                raise ValueError(f"Falta la variable x{indices[i] + 1}. Las variables deben ser consecutivas.")
    
    @staticmethod
    def validate_set_consistency(constraints: List[Constraint]) -> bool:
        """
        Valida que todas las restricciones en un set tengan las mismas variables.
        Ej: Si una tiene (x1, x2), todas deben tener (x1, x2).
        Nota: Asume que las variables faltantes ya han sido rellenadas con 0s (pre-fill requerido antes de llamar este método).
        """
        if not constraints:
            return True # Vacío es consistente

        first_vars = set(constraints[0].coefficients.keys())
        
        for i, constraint in enumerate(constraints[1:], 1):
            current_vars = set(constraint.coefficients.keys())
            if current_vars != first_vars:
                raise ValueError(f"Inconsistencia de variables en la restricción {i+1}. "
                                 f"Se esperaban {sorted(list(first_vars))} pero se encontraron {sorted(list(current_vars))}.")
        return True
