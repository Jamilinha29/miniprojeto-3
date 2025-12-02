from dataclasses import dataclass


TIPO_SUPORTE = "suporte"
TIPO_VENDAS = "vendas"


@dataclass
class SimulacaoConfig:

    num_timesteps: int = 1000
    min_requisicoes: int = 100
    max_requisicoes: int = 500
    prob_falha_servidor: float = 0.01
    prob_falha_atendente: float = 0.02
    prob_entrada_atendente: float = 0.05
    prob_saida_atendente: float = 0.03
    capacidade_buffer: int = 50
    # Map of timestep -> list of server ids to fail at that timestep (programmed interruptions)
    scheduled_failures_servers: dict = None
