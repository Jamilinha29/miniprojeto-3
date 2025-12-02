<<<<<<< HEAD
from dataclasses import dataclass


@dataclass
class Atendente:
    id: int
    tipo: str
    servidor_id: str
    ativo: bool = True
=======
class Atendente:
    def __init__(self, tipo, servidor, idd):
        self.tipo = tipo
        self.servidor = servidor
        self.id = idd
        self.ativo = True

    def falhar(self, log):
        self.ativo = False
        msg = f"[FALHA] Atendente {self.id} ({self.tipo}) falhou no servidor {self.servidor}"
        print(msg)
        log(msg)
>>>>>>> 22c94c5cea82f2b8a00cc4ee03d8a5dcc284771b
