from src.configuracoes import SimulacaoConfig
from src.supervisor import Supervisor


def make_config(**overrides) -> SimulacaoConfig:
    base = SimulacaoConfig(
        num_timesteps=1,
        min_requisicoes=1,
        max_requisicoes=1,
        prob_falha_servidor=0.0,
        prob_falha_atendente=0.0,
        prob_entrada_atendente=0.0,
        prob_saida_atendente=0.0,
        capacidade_buffer=100,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def test_supervisor_run_simulation_success():
    supervisor = Supervisor(config=make_config())
    result = supervisor.run_simulation(seed=7)

    assert result.success
    assert result.total_atendimentos == 1
    assert result.failure_message is None


def test_supervisor_detects_buffer_overflow():
    supervisor = Supervisor(config=make_config(capacidade_buffer=1, min_requisicoes=50, max_requisicoes=50))
    result = supervisor.run_simulation(seed=13)

    assert not result.success
    assert result.failure_message is not None


def test_supervisor_run_batch_records_history():
    supervisor = Supervisor(config=make_config())
    seeds = [1, 2]
    results = supervisor.run_batch(seeds)

    assert len(results) == len(seeds)
    assert all(result.seed == seed for result, seed in zip(results, seeds))
    assert supervisor.history[-len(seeds) :] == results
