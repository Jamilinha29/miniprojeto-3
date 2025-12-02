<<<<<<< HEAD
from dataclasses import dataclass


@dataclass
class Solicitacao:
    id: int
    tipo: str
    timestep_criacao: int
=======
class Solicitacao:
    def __init__(self, tipo):
        self.tipo = tipo
>>>>>>> 22c94c5cea82f2b8a00cc4ee03d8a5dcc284771b
