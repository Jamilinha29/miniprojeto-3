import random

class Supervisor:
    def __init__(self, servidores, falha_servidor, falha_atendente, log):
        self.servidores = servidores
        self.falha_servidor = falha_servidor
        self.falha_atendente = falha_atendente
        self.log = log

    def monitorar(self):
        for servidor in self.servidores:
            if random.random() < self.falha_servidor:
                servidor.falhar_servidor(self.log)

            if servidor.falhou and random.random() < 0.05:
                servidor.recuperar_servidor(self.log)

            for lista in [servidor.atendentes_suporte, servidor.atendentes_vendas]:
                for at in lista:
                    if at.ativo and random.random() < self.falha_atendente:
                        at.falhar(self.log)