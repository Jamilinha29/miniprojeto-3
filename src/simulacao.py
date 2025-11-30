import random
from collections import deque
from servidor import Servidor
from supervisor import Supervisor
from solicitacao import Solicitacao

def simular(nome, cfg, log):
    print(f"\n=========== {nome} ===========\n")

    servidores = [
        Servidor("A", 500),
        Servidor("B", 700),
        Servidor("C", 1000)
    ]

    atendente_id = 0

    for s in servidores:
        for _ in range(cfg["atendentes_iniciais"]):
            s.adicionar_atendente("suporte", atendente_id, log)
            atendente_id += 1
        for _ in range(cfg["atendentes_iniciais"]):
            s.adicionar_atendente("vendas", atendente_id, log)
            atendente_id += 1

    supervisor = Supervisor(
        servidores,
        cfg["falha_servidor"],
        cfg["falha_atendente"],
        log
    )

    fila_suporte = deque(maxlen=50)
    fila_vendas = deque(maxlen=50)

    for t in range(cfg["timesteps"]):
        print(f"\n===== Timestep {t} =====")

        novas = random.randint(cfg["req_min"], cfg["req_max"])
        print(f"[GERAÇÃO] {novas} novas requisições")

        for _ in range(novas):
            tipo = "suporte" if random.random() < 0.5 else "vendas"
            req = Solicitacao(tipo)

            if tipo == "suporte":
                if len(fila_suporte) < 50:
                    fila_suporte.append(req)
                else:
                    print("[ERRO] Buffer suporte estourou!")
                    return
            else:
                if len(fila_vendas) < 50:
                    fila_vendas.append(req)
                else:
                    print("[ERRO] Buffer vendas estourou!")
                    return

        supervisor.monitorar()

        for s in servidores:
            if s.falhou:
                print(f"[SKIP] Servidor {s.nome} OFFLINE")
                continue

            for at in s.atendentes_suporte:
                if at.ativo and fila_suporte:
                    fila_suporte.popleft()

            for at in s.atendentes_vendas:
                if at.ativo and fila_vendas:
                    fila_vendas.popleft()

        print(f"Fila suporte: {len(fila_suporte)}/50")
        print(f"Fila vendas: {len(fila_vendas)}/50")