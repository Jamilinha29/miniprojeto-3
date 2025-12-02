# Tolerância a Falhas em um Sistema Distribuído de Atendimento ao Cliente

## Objetivo

Este documento descreve o projeto "Miniprojeto 3" com foco na investigação de mecanismos de tolerância a falhas em um sistema distribuído de atendimento ao cliente. O escopo inclui modelagem de servidores, filas por tipo de atendimento (suporte, vendas), injeção de falhas (servidor e atendente), estratégias automáticas de realocação e geração de métricas/relatórios para análise de resiliência.

## Metodologia

- Simulação baseada em timesteps (implementada em `src/simulacao.py`).
- O `Supervisor` (em `src/supervisor.py`) executa a simulação passo a passo e coleta métricas.
- Eventos registrados: `atendimento`, `falha_servidor`, `falha_atendente`, `realocacao`, `entrada_atendente`, `saida_atendente`.

## Principais arquivos do projeto

- Código-fonte: `src/` (módulos: `simulacao.py`, `supervisor.py`, `servidor.py`, `atendente.py`, `solicitacao.py`, `relatorios.py`, etc.).
- Testes: `tests/` (executar com `pytest`).
- Relatórios de saída gerados pela simulação:
  - `data/tabelas/` — CSVs com tabelas: `status_servidores.csv`, `transferencias.csv`.
  - `data/graficos/` — PNGs de análise: `atendimentos_por_servidor.png`, `falhas_por_timestep.png`, `percentual_redirecionamentos.png`.
  - `data/relatorios/resumo_simulacao.txt` — resumo textual da execução.

## Configurações principais

As configurações da simulação estão em `src/configuracoes.py`. Parâmetros importantes:

- `capacidade_buffer` (tamanho máximo de fila antes de considerar estouro).
- `min_requisicoes` / `max_requisicoes` (volume de solicitações por timestep).
- `scheduled_failures_servers` (lista de falhas programadas por servidor e timestep).

## Como reproduzir os resultados

1. Crie e ative um ambiente virtual (opcional):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

3. Execute a simulação (opções de saída):

```powershell
python .\src\main.py          # gera tabelas, gráficos e resumo (padrão)
python .\src\main.py --tabelas   # apenas CSVs em data/tabelas (modo de teste)
python .\src\main.py --graficos  # apenas gráficos em data/graficos
python .\src\main.py --resumo    # apenas resumo em data/relatorios
```

4. Para rodar os testes:

```powershell
pip install -r requirements-dev.txt
pytest -q
```

## Observações e recomendações

- Para desenvolvimento local, use `--tabelas` para ativar o modo de teste (reduz o volume de eventos e aumenta o buffer), evitando estouros imediatos.
- Use `pre-commit` para aplicar formatação e lint localmente:

```powershell
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
```

- Se desejar, podemos estender este relatório incluindo gráficos de exemplo, tabelas de métricas (médias, desvios) ou um anexo com logs de uma execução específica.

---

## Arquitetura e descrição dos módulos

O projeto está organizado em módulos Python dentro da pasta `src/`. Abaixo está uma descrição dos principais arquivos e responsabilidades:

- `src/main.py`
  - Ponto de entrada da aplicação. Expõe uma CLI com flags: `--tabelas`, `--graficos`, `--resumo`. Inicializa a `SimulacaoAtendimentoDistribuido` com configurações e invoca o `Supervisor`/relatórios conforme a opção.

- `src/configuracoes.py`
  - Contém `SimulacaoConfig` com parâmetros configuráveis (ex.: `capacidade_buffer`, `min_requisicoes`, `max_requisicoes`, `scheduled_failures_servers`). Use este arquivo para ajustar o comportamento da simulação.

- `src/simulacao.py`
  - Implementa `SimulacaoAtendimentoDistribuido`. Principais responsabilidades:
    - Gerar solicitações por timestep.
    - Alocar atendentes por tipo e servidor.
    - Manusear falhas: `falha_servidor`, `falha_atendente` e realocações.
    - Registrar métricas e eventos em memória.
    - Exportar um resumo textual (`data/relatorios/resumo_simulacao.txt`).
    - Métodos importantes: `step(timestep)`, `rodar()`, `_registrar_status_preemptivo()` (registra status imediatamente antes de um estouro de buffer para diagnóstico).

- `src/supervisor.py`
  - Orquestra a execução passo-a-passo da simulação. Permite executar e inspecionar resultados por timestep, registrar run results e integrar com geradores de relatório.

- `src/servidor.py`
  - Modelo `Servidor` que contém atributos como `nome`, `capacidade`, lista de `Atendente`s alocados, e métodos para checar disponibilidade e aplicar falhas.

- `src/atendente.py`
  - Modelo `Atendente` (provavelmente um dataclass) com `id`, `tipo` (SUPORTE/VENDAS), `ativo` e histórico de atendimentos.

- `src/solicitacao.py`
  - Modelo `Solicitacao` com `id`, `tipo`, `timestamp_insercao`, `servidor_alocado` (quando houver) e `status`.

- `src/logs.py`
  - Estruturas para `LogEntry` e funções para registrar eventos estruturados que alimentam os CSVs e os gráficos.

- `src/relatorios.py`
  - Responsável por escrever os CSVs em `data/tabelas/` e gerar gráficos analíticos em `data/graficos/`. Os CSVs são considerados canônicos para reprodução dos gráficos.

- `tests/`
  - Contém testes unitários (`pytest`) que cobrem comportamento do servidor, supervisor e simulação (falhas e realocações). Execute `pytest -q` para rodar a suíte.

## Formato dos arquivos gerados

- `data/tabelas/status_servidores.csv`
  - Colunas típicas: `timestep`, `servidor`, `tamanho_fila_suporte`, `tamanho_fila_vendas`, `atendentes_ativos`, `capacidade`, `realocacoes_no_timestep`.

- `data/tabelas/transferencias.csv`
  - Registra eventos de realocação/redirecionamento: `timestamp`, `from_servidor`, `to_servidor`, `tipo_atendente`, `motivo`.

- `data/relatorios/resumo_simulacao.txt`
  - Resumo textual com métricas agregadas: total de atendimentos por tipo, total de falhas por tipo, timestep do estouro (se ocorreu), média de filas, etc.

- `data/graficos/*.png`
  - Gráficos analíticos: `atendimentos_por_servidor.png`, `falhas_por_timestep.png`, `percentual_redirecionamentos.png`. Os gráficos são gerados a partir dos CSVs.

## Como executar (resumo rápido)

1. Ambiente virtual (opcional):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
pip install -r requirements.txt
```

3. Executar simulação:

```powershell
python .\src\main.py            # padrão: tabelas + gráficos + resumo
python .\src\main.py --tabelas  # apenas CSVs (modo de teste)
python .\src\main.py --graficos # apenas gráficos
python .\src\main.py --resumo   # apenas resumo em texto
```

4. Executar testes:

```powershell
pip install -r requirements-dev.txt
pytest -q --maxfail=1
```

## Modo de desenvolvimento e qualidade de código

- Utilize `pre-commit` para aplicar formatação e linters antes de commitar:

```powershell
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
```

- Comandos de correção automática:

```powershell
black .
isort .
ruff --fix .
```

- A pipeline de CI (`.github/workflows/ci.yml`) instala dependências, executa `black --check`, `isort --check-only`, `ruff check` e roda os testes (gera `pytest-report.xml`).

## Dicas de extensão e manutenção

- Persistência das filas (`data/filas/`): atualmente são placeholders. Para persistência entre execuções, implemente funções de `save/load` na pasta `data/filas` que serializam as filas (por exemplo, em JSON ou pickle).

- Para adicionar um novo tipo de atendimento (ex.: `FINANCEIRO`):
  1. Atualize o enum/tipos em `src/solicitacao.py` e `src/atendente.py`.
  2. Atualize a lógica de roteamento em `src/simulacao.py`.
  3. Adicione testes que cobrem alocação e realocação para o novo tipo.

- Para instrumentar mais métricas: adicione funções em `src/logs.py` para contar latência por atendimento, tempo médio na fila e exporte essas colunas nos CSVs.

## Logs e resolução de problemas comuns

- Estouro de buffer (buffer overflow): ocorrerá se `capacidade_buffer` for excedido no timestep. A simulação registra um snapshot prévio (`_registrar_status_preemptivo`) para diagnóstico. Solução: reduzir `min_requisicoes`/`max_requisicoes`, aumentar `capacidade_buffer` ou ajustar número de atendentes iniciais.

- Linters falhando na CI (`black`, `isort`, `ruff`): execute `pre-commit run --all-files` localmente e corrija os erros antes de abrir PR.

- Ferramentas não encontradas na CI: verifique se `requirements-dev.txt` é instalado na job de CI (o workflow atual tenta instalar se o arquivo existir).

## Como contribuir

- Fluxo sugerido:
  1. Fork e clone do repositório.
  2. Crie uma branch descritiva: `feature/nome-curto` ou `fix/descricao`.
  3. Rode `pre-commit run --all-files` e os testes localmente.
  4. Abra um Pull Request descrevendo as mudanças.

- Mensagem de commit: seja conciso e descritivo — exemplo: `corrige realocacao quando servidor cair`.

---

**Grupo:** Byte 5
**Membros do grupo:** Jamili Gabriela, Emílio Gaspar, Wesley Albuquerque
**Data:** 2025-12-02
