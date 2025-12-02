from dataclasses import dataclass


@dataclass
class Solicitacao:
    id: int
    tipo: str
    timestep_criacao: int
