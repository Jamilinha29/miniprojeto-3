import csv
from collections import Counter
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from src.simulacao import SimulacaoAtendimentoDistribuido
except ModuleNotFoundError:
    from simulacao import SimulacaoAtendimentoDistribuido


class RelatorioSimulacao:
    def __init__(
        self,
        simulacao: SimulacaoAtendimentoDistribuido,
        tabelas_dir: Optional[Path] = None,
        graficos_dir: Optional[Path] = None,
    ) -> None:
        self.simulacao = simulacao
        self.tabelas_dir = Path(tabelas_dir or "data/tabelas")
        self.graficos_dir = Path(graficos_dir or "data/graficos")

    def gerar_tabelas(self) -> None:
        self.tabelas_dir.mkdir(parents=True, exist_ok=True)
        self._escrever_status_csv()
        self._escrever_redirecionamentos_csv()
        # Gerar apenas os CSVs; não gerar PNGs das tabelas (solicitado)

    def gerar_graficos(self) -> None:
        self.graficos_dir.mkdir(parents=True, exist_ok=True)
        self._plot_atendimentos_por_servidor()
        self._plot_falhas_por_timestep()
        self._plot_percentual_redirecionamentos()

    def _escrever_status_csv(self) -> None:
        path = self.tabelas_dir / "status_servidores.csv"
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
            for entry in self.simulacao.status_por_timestep:
                writer.writerow(entry)

    def _escrever_redirecionamentos_csv(self) -> None:
        path = self.tabelas_dir / "transferencias.csv"
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
            for entry in self.simulacao.redirecionamentos:
                writer.writerow(entry)
    def gerar_resumo(self) -> None:
        """Escreve o resumo (como no terminal) apenas em texto (TXT)."""
        rel_dir = Path("data/relatorios")
        rel_dir.mkdir(parents=True, exist_ok=True)
        txt_path = rel_dir / "resumo_simulacao.txt"
        lines = [
            "===== RESUMO DA SIMULAÇÃO =====",
            f"Total de atendimentos de SUPORTE: {self.simulacao.total_atendimentos_suporte}",
            f"Total de atendimentos de VENDAS:  {self.simulacao.total_atendimentos_vendas}",
            f"Total de falhas de SERVIDOR:      {self.simulacao.total_falhas_servidor}",
            f"Total de falhas de ATENDENTE:     {self.simulacao.total_falhas_atendente}",
            f"Total de realocações registradas: {self.simulacao.total_realocacoes}",
            f"Tamanho final da fila SUPORTE:    {len(self.simulacao.fila_suporte)}",
            f"Tamanho final da fila VENDAS:     {len(self.simulacao.fila_vendas)}",
            "================================",
        ]
        txt_path.write_text("\n".join(lines), encoding="utf-8")

    def _plot_atendimentos_por_servidor(self) -> None:
        counts = Counter(
            log.detalhes.get("servidor")
            for log in self.simulacao.logs
            if log.evento == "atendimento"
        )
        servidores = sorted(counts) or ["nenhum"]
        values = [counts[s] for s in servidores]
        plt.figure()
        plt.bar(servidores, values, color="tab:blue")
        plt.title("Atendimentos por servidor")
        plt.xlabel("Servidor")
        plt.ylabel("Atendimentos")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.graficos_dir / "atendimentos_por_servidor.png")
        plt.close()

    def _plot_falhas_por_timestep(self) -> None:
        falhas = Counter()
        for log in self.simulacao.logs:
            if log.evento in {"falha_servidor", "falha_atendente"}:
                falhas[log.timestep] += 1
        x_values = list(range(1, self.simulacao.num_timesteps + 1))
        y_values = [falhas.get(x, 0) for x in x_values]
        plt.figure()
        plt.plot(x_values, y_values, marker="o", linestyle="-", color="tab:red")
        plt.title("Falhas por timestep")
        plt.xlabel("Timestep")
        plt.ylabel("Falhas")
        plt.tight_layout()
        plt.savefig(self.graficos_dir / "falhas_por_timestep.png")
        plt.close()

    def _plot_percentual_redirecionamentos(self) -> None:
        # Preferir a contagem a partir do CSV de transferencias (se existir e estiver preenchido),
        # caso contrário usar os logs em memória.
        total = (
            self.simulacao.total_atendimentos_suporte
            + self.simulacao.total_atendimentos_vendas
        )
        redirecionados = 0
        csv_path = self.tabelas_dir / "transferencias.csv"
        if csv_path.exists():
            try:
                with csv_path.open("r", encoding="utf-8") as fp:
                    lines = [l for l in fp.readlines() if l.strip()]
                # se houver mais que apenas cabeçalho
                if len(lines) > 1:
                    redirecionados = len(lines) - 1
                else:
                    redirecionados = sum(1 for log in self.simulacao.logs if log.evento == "realocacao")
            except Exception:
                redirecionados = sum(1 for log in self.simulacao.logs if log.evento == "realocacao")
        else:
            redirecionados = sum(1 for log in self.simulacao.logs if log.evento == "realocacao")
        if total == 0:
            sizes = [0, 1]
            labels = ["Redirecionados", "Sem atendimentos"]
        else:
            sizes = [redirecionados, max(total - redirecionados, 0)]
            labels = ["Redirecionados", "Atendidos no servidor original"]
        plt.figure()
        plt.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=["tab:purple", "tab:green"],
        )
        plt.axis("equal")
        plt.title("Percentual de requisições redirecionadas")
        plt.tight_layout()
        plt.savefig(self.graficos_dir / "percentual_redirecionamentos.png")
        plt.close()
