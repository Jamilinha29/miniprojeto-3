from src.configuracoes import SimulacaoConfig
from src.simulacao import SimulacaoAtendimentoDistribuido


def make_config(**overrides) -> SimulacaoConfig:
    base = SimulacaoConfig(
        num_timesteps=1,
        min_requisicoes=0,
        max_requisicoes=0,
        prob_falha_servidor=1.0,
        prob_falha_atendente=1.0,
        prob_entrada_atendente=0.0,
        prob_saida_atendente=0.0,
        capacidade_buffer=1000,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def test_simulacao_registra_falhas_em_todos_os_nos():
    config = make_config()
    simulacao = SimulacaoAtendimentoDistribuido(config=config, seed=0)

    simulacao._simular_falhas_servidor(timestep=1)
    simulacao._simular_falhas_atendentes(timestep=1)

    total_servidores = len(simulacao.servidores)
    total_atendentes = sum(len(s.atendentes) for s in simulacao.servidores.values())

    assert simulacao.total_falhas_servidor == total_servidores
    assert simulacao.total_falhas_atendente == total_atendentes
