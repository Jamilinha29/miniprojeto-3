from dataclasses import dataclass


@dataclass
class Atendente:
    id: int
    tipo: str
    servidor_id: str
    ativo: bool = True
