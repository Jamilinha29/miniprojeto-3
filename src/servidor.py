<<<<<<< HEAD
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
=======
from atendente import Atendente

class Servidor:
    def __init__(self, nome, capacidade):
        self.nome = nome
        self.capacidade = capacidade
        self.atendentes_suporte = []
        self.atendentes_vendas = []
        self.falhou = False

    def adicionar_atendente(self, tipo, idd, log):
        at = Atendente(tipo, self.nome, idd)
        if tipo == "suporte":
            self.atendentes_suporte.append(at)
        else:
            self.atendentes_vendas.append(at)
        msg = f"[NOVO ATENDENTE] {tipo} #{idd} entrou no servidor {self.nome}"
        print(msg)
        log(msg)

    def remover_atendente(self, tipo, log):
        lista = self.atendentes_suporte if tipo == "suporte" else self.atendentes_vendas
        if lista:
            at = lista.pop()
            msg = f"[SAÍDA] Atendente {at.id} ({tipo}) saiu do servidor {self.nome}"
            print(msg)
            log(msg)

    def falhar_servidor(self, log):
        self.falhou = True
        msg = f"[FALHA] Servidor {self.nome} ficou OFFLINE"
        print(msg)
        log(msg)

    def recuperar_servidor(self, log):
        self.falhou = False
        msg = f"[RECUPERAÇÃO] Servidor {self.nome} voltou ONLINE"
        print(msg)
        log(msg)
>>>>>>> 22c94c5cea82f2b8a00cc4ee03d8a5dcc284771b
