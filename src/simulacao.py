<<<<<<< HEAD
import csv
import random
from pathlib import Path
from typing import Dict, List, Optional

try:
    from src.atendente import Atendente
except ModuleNotFoundError:
    from atendente import Atendente

try:
    from src.configuracoes import SimulacaoConfig, TIPO_SUPORTE, TIPO_VENDAS
except ModuleNotFoundError:
    from configuracoes import SimulacaoConfig, TIPO_SUPORTE, TIPO_VENDAS

try:
    from src.logs import LogEntry
except ModuleNotFoundError:
    from logs import LogEntry

try:
    from src.servidor import Servidor
except ModuleNotFoundError:
    from servidor import Servidor

try:
    from src.solicitacao import Solicitacao
except ModuleNotFoundError:
    from solicitacao import Solicitacao


class SimulacaoAtendimentoDistribuido:
    def __init__(
        self,
        config: SimulacaoConfig,
        seed: Optional[int] = None,
        relatorios_dir: Optional[Path] = None,
    ) -> None:
        if seed is not None:
            random.seed(seed)

        self.config = config
        self.num_timesteps = config.num_timesteps
        self.min_requisicoes = config.min_requisicoes
        self.max_requisicoes = config.max_requisicoes
        self.prob_falha_servidor = config.prob_falha_servidor
        self.prob_falha_atendente = config.prob_falha_atendente
        self.prob_entrada_atendente = config.prob_entrada_atendente
        self.prob_saida_atendente = config.prob_saida_atendente
        self.capacidade_buffer = config.capacidade_buffer

        self.fila_suporte: List[Solicitacao] = []
        self.fila_vendas: List[Solicitacao] = []
        self.logs: List[LogEntry] = []

        self._next_atendente_id = 1
        self._next_solicitacao_id = 1

        self.total_atendimentos_suporte = 0
        self.total_atendimentos_vendas = 0
        self.total_falhas_servidor = 0
        self.total_falhas_atendente = 0
        self.total_realocacoes = 0

        self.servidores: Dict[str, Servidor] = {}
        self._inicializar_servidores()
        self.buffer_estourou = False
        self.buffer_error_message: Optional[str] = None
        self.status_por_timestep: List[Dict[str, int]] = []
        self.redirecionamentos: List[Dict[str, str]] = []
        self._realocacoes_no_timestep = 0
        base_dir = relatorios_dir or Path("data/relatorios")
        self.relatorios_dir = Path(base_dir)
        self.status_por_timestep: List[Dict[str, int]] = []
        self.redirecionamentos: List[Dict[str, str]] = []
        self._realocacoes_no_timestep = 0
        self.buffer_estourou = False
        self.buffer_error_message: Optional[str] = None

    def _inicializar_servidores(self) -> None:
        capacidades = {"A": 500, "B": 700, "C": 1000}

        for sid, cap in capacidades.items():
            self.servidores[sid] = Servidor(id=sid, capacidade=cap)

        # Para cada servidor, gerar uma quantidade aleatória de atendentes
        # respeitando o mínimo de 2 (para permitir 1 de cada tipo) e a capacidade máxima.
        for servidor in self.servidores.values():
            max_initial = max(2, servidor.capacidade)
            num_atendentes = random.randint(2, servidor.capacidade)
            for _ in range(num_atendentes):
                tipo = random.choice([TIPO_SUPORTE, TIPO_VENDAS])
                atendente = Atendente(
                    id=self._next_atendente_id,
                    tipo=tipo,
                    servidor_id=servidor.id,
                )
                self._next_atendente_id += 1
                servidor.atendentes.append(atendente)

        for servidor in self.servidores.values():
            tipos_presentes = {a.tipo for a in servidor.atendentes}
            if TIPO_SUPORTE not in tipos_presentes and servidor.atendentes:
                servidor.atendentes[0].tipo = TIPO_SUPORTE
            if TIPO_VENDAS not in tipos_presentes and len(servidor.atendentes) > 1:
                servidor.atendentes[1].tipo = TIPO_VENDAS

        def contar_tipo(tipo: str) -> int:
            return sum(
                1
                for s in self.servidores.values()
                for a in s.atendentes
                if a.tipo == tipo
            )

        while contar_tipo(TIPO_SUPORTE) < 100:
            servidor = random.choice(list(self.servidores.values()))
            atendente = random.choice(servidor.atendentes)
            atendente.tipo = TIPO_SUPORTE

        while contar_tipo(TIPO_VENDAS) < 100:
            servidor = random.choice(list(self.servidores.values()))
            atendente = random.choice(servidor.atendentes)
            atendente.tipo = TIPO_VENDAS

    def _gerar_solicitacoes(self, timestep: int) -> None:
        qtd = random.randint(self.min_requisicoes, self.max_requisicoes)
        for _ in range(qtd):
            tipo = random.choice([TIPO_SUPORTE, TIPO_VENDAS])
            solicitacao = Solicitacao(
                id=self._next_solicitacao_id,
                tipo=tipo,
                timestep_criacao=timestep,
            )
            self._next_solicitacao_id += 1

            if tipo == TIPO_SUPORTE:
                self.fila_suporte.append(solicitacao)
            else:
                self.fila_vendas.append(solicitacao)

        tamanho_buffer = len(self.fila_suporte) + len(self.fila_vendas)
        if tamanho_buffer > self.capacidade_buffer:
            self.buffer_estourou = True
            self.buffer_error_message = (
                f"Buffer estourou no timestep {timestep} com {tamanho_buffer} solicitações na fila."
            )
            # Registrar snapshot de status antes de encerrar, para garantir que
            # o CSV `status_servidores.csv` contenha ao menos o registro deste timestep.
            try:
                self._registrar_status_preemptivo(timestep)
            except Exception:
                # garantir que não atrapalhe a propagação do erro original
                pass
            raise RuntimeError(self.buffer_error_message)

    def _registrar_status_preemptivo(self, timestep: int) -> None:
        servidores_ativos = sum(1 for s in self.servidores.values() if s.ativo)
        atendentes_suporte_ativos = sum(
            1
            for s in self.servidores.values()
            for a in s.atendentes
            if a.ativo and a.tipo == TIPO_SUPORTE
        )
        atendentes_vendas_ativos = sum(
            1
            for s in self.servidores.values()
            for a in s.atendentes
            if a.ativo and a.tipo == TIPO_VENDAS
        )
        # usar realocacoes acumuladas no timestep atual (pode ser zero)
        realocacoes = getattr(self, "_realocacoes_no_timestep", 0)
        self.status_por_timestep.append(
            {
                "timestep": timestep,
                "fila_suporte": len(self.fila_suporte),
                "fila_vendas": len(self.fila_vendas),
                "servidores_ativos": servidores_ativos,
                "atendentes_suporte_ativos": atendentes_suporte_ativos,
                "atendentes_vendas_ativos": atendentes_vendas_ativos,
                "realocacoes": realocacoes,
            }
        )

    def _simular_falhas_servidor(self, timestep: int) -> None:
        for servidor in self.servidores.values():
            servidor.ativo = True
            # aplicar falhas programadas (se fornecidas)
            if self.config.scheduled_failures_servers:
                scheduled = self.config.scheduled_failures_servers.get(timestep, [])
                if servidor.id in scheduled:
                    servidor.ativo = False
                    self.total_falhas_servidor += 1
                    self.logs.append(
                        LogEntry(
                            timestep=timestep,
                            evento="falha_servidor",
                            detalhes={"servidor": servidor.id, "tipo": "programada"},
                        )
                    )
                    continue

            if random.random() < self.prob_falha_servidor:
                servidor.ativo = False
                self.total_falhas_servidor += 1
                self.logs.append(
                    LogEntry(
                        timestep=timestep,
                        evento="falha_servidor",
                        detalhes={"servidor": servidor.id},
                    )
                )

    def _simular_falhas_atendentes(self, timestep: int) -> None:
        for servidor in self.servidores.values():
            for atendente in servidor.atendentes:
                atendente.ativo = True
                if random.random() < self.prob_falha_atendente:
                    atendente.ativo = False
                    self.total_falhas_atendente += 1
                    self.logs.append(
                        LogEntry(
                            timestep=timestep,
                            evento="falha_atendente",
                            detalhes={
                                "servidor": servidor.id,
                                "atendente_id": str(atendente.id),
                                "tipo": atendente.tipo,
                            },
                        )
                    )

    def _ajustar_capacidade_dinamica(self, timestep: int) -> None:
        if random.random() < self.prob_entrada_atendente:
            servidor = random.choice(list(self.servidores.values()))
            if len(servidor.atendentes) < servidor.capacidade:
                tipo = random.choice([TIPO_SUPORTE, TIPO_VENDAS])
                novo = Atendente(
                    id=self._next_atendente_id,
                    tipo=tipo,
                    servidor_id=servidor.id,
                )
                self._next_atendente_id += 1
                servidor.atendentes.append(novo)
                self.logs.append(
                    LogEntry(
                        timestep=timestep,
                        evento="entrada_atendente",
                        detalhes={
                            "servidor": servidor.id,
                            "atendente_id": str(novo.id),
                            "tipo": tipo,
                        },
                    )
                )

        if random.random() < self.prob_saida_atendente:
            servidor = random.choice(list(self.servidores.values()))
            if len(servidor.atendentes) > 2:
                candidatos = list(servidor.atendentes)
                random.shuffle(candidatos)
                for a in candidatos:
                    tipos_restantes = [x.tipo for x in servidor.atendentes if x != a]
                    if TIPO_SUPORTE in tipos_restantes and TIPO_VENDAS in tipos_restantes:
                        servidor.atendentes.remove(a)
                        self.logs.append(
                            LogEntry(
                                timestep=timestep,
                                evento="saida_atendente",
                                detalhes={
                                    "servidor": servidor.id,
                                    "atendente_id": str(a.id),
                                    "tipo": a.tipo,
                                },
                            )
                        )
                        break

    def _processar_solicitacoes(self, timestep: int) -> None:
        self._realocacoes_no_timestep = 0
        atendentes_suporte: List[Atendente] = []
        atendentes_vendas: List[Atendente] = []

        for servidor in self.servidores.values():
            if not servidor.ativo:
                continue
            for atendente in servidor.atendentes:
                if not atendente.ativo:
                    continue
                if atendente.tipo == TIPO_SUPORTE:
                    atendentes_suporte.append(atendente)
                else:
                    atendentes_vendas.append(atendente)

        self._atender_fila(
            timestep=timestep,
            fila=self.fila_suporte,
            atendentes=atendentes_suporte,
            tipo=TIPO_SUPORTE,
        )

        self._atender_fila(
            timestep=timestep,
            fila=self.fila_vendas,
            atendentes=atendentes_vendas,
            tipo=TIPO_VENDAS,
        )

        self._registrar_status(timestep)

    def _atender_fila(
        self,
        timestep: int,
        fila: List[Solicitacao],
        atendentes: List[Atendente],
        tipo: str,
    ) -> None:
        disponiveis = atendentes.copy()
        random.shuffle(disponiveis)

        while fila and disponiveis:
            solicitacao = fila.pop(0)
            atendente = disponiveis.pop()

            if not atendente.ativo:
                self.total_realocacoes += 1
                self._realocacoes_no_timestep += 1
                detalhes = {
                    "motivo": "falha_atendente_no_momento",
                    "atendente_original": str(atendente.id),
                    "tipo": tipo,
                    "servidor_original": atendente.servidor_id,
                }
                self.logs.append(
                    LogEntry(
                        timestep=timestep,
                        evento="realocacao",
                        detalhes=detalhes,
                    )
                )
                if disponiveis:
                    novo_atendente = disponiveis.pop()
                    detalhes["servidor_destino"] = novo_atendente.servidor_id
                    detalhes["atendente_substituto"] = str(novo_atendente.id)
                    self.redirecionamentos.append(
                        {
                            "timestep": timestep,
                            "solicitacao_id": str(solicitacao.id),
                            "tipo": solicitacao.tipo,
                            "servidor_original": atendente.servidor_id,
                            "atendente_original": str(atendente.id),
                            "servidor_destino": novo_atendente.servidor_id,
                            "atendente_substituto": str(novo_atendente.id),
                        }
                    )
                    self._registrar_atendimento(timestep, solicitacao, novo_atendente)
                else:
                    fila.insert(0, solicitacao)
                    break
            else:
                self._registrar_atendimento(timestep, solicitacao, atendente)

    def _registrar_status(self, timestep: int) -> None:
        servidores_ativos = sum(1 for s in self.servidores.values() if s.ativo)
        atendentes_suporte_ativos = sum(
            1
            for s in self.servidores.values()
            for a in s.atendentes
            if a.ativo and a.tipo == TIPO_SUPORTE
        )
        atendentes_vendas_ativos = sum(
            1
            for s in self.servidores.values()
            for a in s.atendentes
            if a.ativo and a.tipo == TIPO_VENDAS
        )
        self.status_por_timestep.append(
            {
                "timestep": timestep,
                "fila_suporte": len(self.fila_suporte),
                "fila_vendas": len(self.fila_vendas),
                "servidores_ativos": servidores_ativos,
                "atendentes_suporte_ativos": atendentes_suporte_ativos,
                "atendentes_vendas_ativos": atendentes_vendas_ativos,
                "realocacoes": self._realocacoes_no_timestep,
            }
        )

    def _registrar_atendimento(
        self, timestep: int, solicitacao: Solicitacao, atendente: Atendente
    ) -> None:
        if solicitacao.tipo == TIPO_SUPORTE:
            self.total_atendimentos_suporte += 1
        else:
            self.total_atendimentos_vendas += 1

        self.logs.append(
            LogEntry(
                timestep=timestep,
                evento="atendimento",
                detalhes={
                    "solicitacao_id": str(solicitacao.id),
                    "tipo": solicitacao.tipo,
                    "servidor": atendente.servidor_id,
                    "atendente_id": str(atendente.id),
                },
            )
        )

    def _escrever_relatorios(self) -> None:
        self.relatorios_dir.mkdir(parents=True, exist_ok=True)
        # Não gerar CSVs de tabelas aqui (essas ficam sob `data/tabelas` via RelatorioSimulacao).
        # Gerar apenas o resumo em texto em `data/relatorios/resumo_simulacao.txt`.
        self._escrever_resumo_txt()

    def _escrever_status_csv(self) -> None:
        path = self.relatorios_dir / "status_servidores.csv"
        fields = [
            "timestep",
            "fila_suporte",
            "fila_vendas",
            "servidores_ativos",
            "atendentes_suporte_ativos",
            "atendentes_vendas_ativos",
            "realocacoes",
        ]
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fields)
            writer.writeheader()
            for entry in self.status_por_timestep:
                writer.writerow(entry)

    def _escrever_redirecionamentos_csv(self) -> None:
        path = self.relatorios_dir / "transferencias.csv"
        fields = [
            "timestep",
            "solicitacao_id",
            "tipo",
            "servidor_original",
            "atendente_original",
            "servidor_destino",
            "atendente_substituto",
        ]
        with path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=fields)
            writer.writeheader()
            for entry in self.redirecionamentos:
                writer.writerow(entry)

    def _escrever_resumo_csv(self) -> None:
        # antigo método de escrever CSV foi removido; manter compatibilidade caso seja chamado
        pass

    def _escrever_resumo_txt(self) -> None:
        path = self.relatorios_dir / "resumo_simulacao.txt"
        lines = [
            "===== RESUMO DA SIMULAÇÃO =====",
            f"Total de atendimentos de SUPORTE: {self.total_atendimentos_suporte}",
            f"Total de atendimentos de VENDAS:  {self.total_atendimentos_vendas}",
            f"Total de falhas de SERVIDOR:      {self.total_falhas_servidor}",
            f"Total de falhas de ATENDENTE:     {self.total_falhas_atendente}",
            f"Total de realocações registradas: {self.total_realocacoes}",
            f"Tamanho final da fila SUPORTE:    {len(self.fila_suporte)}",
            f"Tamanho final da fila VENDAS:     {len(self.fila_vendas)}",
            "================================",
        ]
        path.write_text("\n".join(lines), encoding="utf-8")

    def rodar(self) -> None:
        print("Iniciando simulação...")
        try:
            for t in range(1, self.num_timesteps + 1):
                cont = self.step(t)
                if not cont:
                    break
            if not self.buffer_estourou:
                print("Simulação concluída sem estouro de buffer.")
        except RuntimeError as e:
            self.buffer_estourou = True
            self.buffer_error_message = self.buffer_error_message or str(e)
            print("Simulação encerrada com falha:", e)
        finally:
            self._imprimir_resumo()
            self._escrever_relatorios()

    def step(self, t: int) -> bool:
        """Executa um timestep da simulação. Retorna False se o buffer estourar e a simulação deve encerrar."""
        self._ajustar_capacidade_dinamica(t)
        self._simular_falhas_servidor(t)
        self._simular_falhas_atendentes(t)
        self._gerar_solicitacoes(t)
        # _gerar_solicitacoes pode lançar RuntimeError quando o buffer estourar
        self._processar_solicitacoes(t)
        # se tudo ok, continuar
        return not self.buffer_estourou

    def _imprimir_resumo(self) -> None:
        print("\n===== RESUMO DA SIMULAÇÃO =====")
        print(f"Total de atendimentos de SUPORTE: {self.total_atendimentos_suporte}")
        print(f"Total de atendimentos de VENDAS:  {self.total_atendimentos_vendas}")
        print(f"Total de falhas de SERVIDOR:      {self.total_falhas_servidor}")
        print(f"Total de falhas de ATENDENTE:     {self.total_falhas_atendente}")
        print(f"Total de realocações registradas: {self.total_realocacoes}")
        print(f"Tamanho final da fila SUPORTE:    {len(self.fila_suporte)}")
        print(f"Tamanho final da fila VENDAS:     {len(self.fila_vendas)}")
        print("================================")
=======
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
>>>>>>> 22c94c5cea82f2b8a00cc4ee03d8a5dcc284771b
