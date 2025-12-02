<<<<<<< HEAD
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

try:
    from src.configuracoes import SimulacaoConfig
    from src.simulacao import SimulacaoAtendimentoDistribuido
except ModuleNotFoundError:
    from configuracoes import SimulacaoConfig
    from simulacao import SimulacaoAtendimentoDistribuido


@dataclass
class SupervisorRunResult:
    seed: int
    success: bool
    total_atendimentos_suporte: int
    total_atendimentos_vendas: int
    total_falhas_servidor: int
    total_falhas_atendente: int
    total_realocacoes: int
    fila_suporte: int
    fila_vendas: int
    failure_message: Optional[str] = None

    @property
    def total_atendimentos(self) -> int:
        return self.total_atendimentos_suporte + self.total_atendimentos_vendas


@dataclass
class Supervisor:
    config: SimulacaoConfig
    history: List[SupervisorRunResult] = field(default_factory=list)

    def run_simulation(self, seed: Optional[int] = None) -> SupervisorRunResult:
        simulacao = SimulacaoAtendimentoDistribuido(config=self.config, seed=seed)

        # executar step a step para permitir monitoramento por timestep
        failure_message = None
        for t in range(1, simulacao.num_timesteps + 1):
            try:
                cont = simulacao.step(t)
            except RuntimeError as e:
                failure_message = str(e)
                break

            # Monitor: checar disponibilidade dos servidores ao fim do timestep
            # Falha = servidor inativo (já registrado nos logs pela simulação)
            # Podemos aqui anexar lógica adicional de alerta se necessário.
            # Se buffer estourou, sair
            if simulacao.buffer_estourou:
                failure_message = simulacao.buffer_error_message
                break

            if not cont:
                break

        result = SupervisorRunResult(
            seed=seed if seed is not None else 0,
            success=not simulacao.buffer_estourou,
            total_atendimentos_suporte=simulacao.total_atendimentos_suporte,
            total_atendimentos_vendas=simulacao.total_atendimentos_vendas,
            total_falhas_servidor=simulacao.total_falhas_servidor,
            total_falhas_atendente=simulacao.total_falhas_atendente,
            total_realocacoes=simulacao.total_realocacoes,
            fila_suporte=len(simulacao.fila_suporte),
            fila_vendas=len(simulacao.fila_vendas),
            failure_message=failure_message,
        )
        self.history.append(result)
        return result

    def run_batch(self, seeds: Sequence[int]) -> List[SupervisorRunResult]:
        return [self.run_simulation(seed) for seed in seeds]
=======
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
>>>>>>> 22c94c5cea82f2b8a00cc4ee03d8a5dcc284771b
