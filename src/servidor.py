from dataclasses import dataclass, field
from typing import List

try:
    from src.atendente import Atendente
except ModuleNotFoundError:
    from atendente import Atendente


@dataclass
class Servidor:
    id: str
    capacidade: int
    atendentes: List[Atendente] = field(default_factory=list)
    ativo: bool = True
