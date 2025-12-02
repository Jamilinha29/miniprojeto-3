try:
    from src.configuracoes import SimulacaoConfig
except ModuleNotFoundError:
    from configuracoes import SimulacaoConfig

try:
    from src.simulacao import SimulacaoAtendimentoDistribuido
except ModuleNotFoundError:
    from simulacao import SimulacaoAtendimentoDistribuido

try:
    from src.relatorios import RelatorioSimulacao
except ModuleNotFoundError:
    from relatorios import RelatorioSimulacao

import argparse


def main() -> None:
    config = SimulacaoConfig(
        num_timesteps=1000,
        # Valores conforme especificação (podem ser ajustados via código/CLI)
        min_requisicoes=100,
        max_requisicoes=20000,
        prob_falha_servidor=0.01,
        prob_falha_atendente=0.10,
        prob_entrada_atendente=0.05,
        prob_saida_atendente=0.03,
        capacidade_buffer=50,
    )

    parser = argparse.ArgumentParser(description="Executa a simulação e gera relatórios.")
    parser.add_argument("--tabelas", action="store_true", help="Gerar apenas as tabelas CSV (se usado junto com outros, gera selecionados)")
    parser.add_argument("--graficos", action="store_true", help="Gerar apenas os gráficos em data/graficos")
    parser.add_argument("--resumo", action="store_true", help="Gerar apenas o resumo em texto")
    args = parser.parse_args()

    # Ajuste automático de parâmetros para execuções de teste quando --tabelas for usado.
    # Isso evita estouros imediatos do buffer em runs rápidos de verificação.
    if args.tabelas:
        print("[AUTO-ADJUST] Modo de teste detectado (--tabelas): ajustando parâmetros para execução rápida.")
        # Valores de teste: fluxo leve e buffer grande para não interromper imediatamente
        config.min_requisicoes = 5
        config.max_requisicoes = 20
        config.capacidade_buffer = 1000

    simulacao = SimulacaoAtendimentoDistribuido(config=config, seed=42)
    simulacao.rodar()

    relatorio = RelatorioSimulacao(simulacao=simulacao)

    # Se nenhum flag for passado, gerar tudo (comportamento padrão)
    if not (args.tabelas or args.graficos or args.resumo):
        relatorio.gerar_tabelas()
        relatorio.gerar_graficos()
        relatorio.gerar_resumo()
        return

    # Caso algum flag seja passado, gerar somente os selecionados
    if args.tabelas:
        relatorio.gerar_tabelas()
    if args.graficos:
        relatorio.gerar_graficos()
    if args.resumo:
        relatorio.gerar_resumo()


if __name__ == "__main__":
    main()
