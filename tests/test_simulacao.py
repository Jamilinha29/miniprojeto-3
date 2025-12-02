import pytest

from src.configuracoes import SimulacaoConfig
from src.simulacao import SimulacaoAtendimentoDistribuido


def make_config(**overrides) -> SimulacaoConfig:
    base = SimulacaoConfig(
        num_timesteps=5,
        min_requisicoes=1,
        max_requisicoes=1,
        prob_falha_servidor=0.0,
        prob_falha_atendente=0.0,
        prob_entrada_atendente=0.0,
        prob_saida_atendente=0.0,
        capacidade_buffer=1000,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def test_simulacao_processa_todas_as_requisicoes_sem_estourar(tmp_path):
    config = make_config(num_timesteps=3)
    relatorios_dir = tmp_path / "relatorios"
    simulacao = SimulacaoAtendimentoDistribuido(
        config=config, seed=1, relatorios_dir=relatorios_dir
    )

    simulacao.rodar()

    assert (simulacao.total_atendimentos_suporte + simulacao.total_atendimentos_vendas) == 3
    assert simulacao.buffer_estourou is False
    assert simulacao.buffer_error_message is None


def test_simulacao_raise_buffer_overflow_e_mensagem_disponivel():
    config = make_config(min_requisicoes=10, max_requisicoes=10, capacidade_buffer=1)
    simulacao = SimulacaoAtendimentoDistribuido(config=config, seed=2)

    with pytest.raises(RuntimeError):
        simulacao._gerar_solicitacoes(timestep=1)

    assert simulacao.buffer_estourou is True
    assert "Buffer estourou" in simulacao.buffer_error_message


def test_simulacao_gera_relatorios_csv(tmp_path):
    config = make_config(num_timesteps=2)
    relatorios_dir = tmp_path / "relatorios"
    simulacao = SimulacaoAtendimentoDistribuido(
        config=config, seed=3, relatorios_dir=relatorios_dir
    )

    simulacao.rodar()

    status_path = relatorios_dir / "status_servidores.csv"
    transferencias_path = relatorios_dir / "transferencias.csv"
    resumo_path = relatorios_dir / "resumo_simulacao.csv"
    assert status_path.exists()
    assert transferencias_path.exists()
    assert resumo_path.exists()
