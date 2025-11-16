import time
from locust import HttpUser, task, between

class SimplexUser(HttpUser):
    """
    Define el comportamiento de un usuario virtual que navega
    y resuelve problemas Simplex.
    """
    
    # El usuario esperará entre 1 y 3 segundos entre cada tarea
    wait_time = between(1, 3)

    # DATOS DE PRUEBA (Extraídos de tus tests)
    
    # Datos para un problema de Maximización
    FORM_DATA_MAX = {
        'problem_type': 'maximize',
        'objective[]': [3.0, 5.0],
        'constraint_1[]': [1.0, 3.0, 3.0],  # Coeficientes de x1
        'constraint_2[]': [0.0, 2.0, 2.0],  # Coeficientes de x2
        'constraint_sign[]': ['<=', '<=', '<='],
        'constraint_rhs[]': [4.0, 12.0, 18.0]
    }
    
    # Datos para un problema de Minimización
    FORM_DATA_MIN = {
        'problem_type': 'minimize',
        'objective[]': [2.0, 3.0],
        'constraint_1[]': [1.0, 2.0], # Coeficientes de x1
        'constraint_2[]': [1.0, 1.0], # Coeficientes de x2
        'constraint_sign[]': ['>=', '>='],
        'constraint_rhs[]': [5.0, 8.0]
    }

    # TAREAS DEL USUARIO
    # Locust elegirá aleatoriamente entre estas tareas.
    # El número en @task() es el "peso": 
    # es 3 veces más probable que resuelvan un problema
    # a que solo visiten la página principal.

    @task(3) # Tarea con peso 3
    def solve_max_problem(self):
        """
        Simula el flujo completo de un usuario resolviendo
        un problema de MAXIMIZACIÓN.
        """
        # 1. El usuario envía el formulario con los datos
        self.client.post("/new", data=self.FORM_DATA_MAX)
        
        # 2. El usuario presiona "Resolver"
        # Usamos 'name' para agrupar esta petición en las estadísticas
        self.client.post("/solve", name="/solve (max)")

    @task(3) # Tarea con peso 3
    def solve_min_problem(self):
        """
        Simula el flujo completo de un usuario resolviendo
        un problema de MINIMIZACIÓN.
        """
        # 1. Enviar formulario
        self.client.post("/new", data=self.FORM_DATA_MIN)
        
        # 2. Resolver
        self.client.post("/solve", name="/solve (min)")

    @task(1) # Tarea con peso 1
    def visit_index(self):
        """
        Simula un usuario que solo visita la página principal
        y luego se va (no resuelve nada).
        """
        self.client.get("/")