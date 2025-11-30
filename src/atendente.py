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