![CI](https://github.com/Jamilinha29/miniprojeto-3/actions/workflows/ci.yml/badge.svg)

Projeto: Miniprojeto 3 — Simulação de Atendimento Distribuído

Visão geral
- Simula um sistema de atendimento distribuído com vários servidores (A, B, C), atendentes por tipo (suporte, vendas), filas separadas, injeção de falhas e realocação automática.
- Gera relatórios em CSV em `data/tabelas/` e um resumo em texto em `data/relatorios/resumo_simulacao.txt`.
- Gera gráficos analíticos em `data/graficos/` (barras, linhas, pizza) a partir dos dados da simulação.

Instalação
1. Crie um ambiente virtual (opcional mas recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

Como executar
- Executa simulação completa (padrão: gera tabelas, gráficos e resumo):

```powershell
python .\src\main.py
```

- Flags disponíveis (CLI):
  - `--tabelas` : gera apenas os CSVs em `data/tabelas/` (modo de teste aplica ajustes automáticos de parâmetros para evitar estouros imediatos)
  - `--graficos` : gera apenas os PNGs em `data/graficos/`
  - `--resumo` : gera apenas `data/relatorios/resumo_simulacao.txt`

Exemplo (apenas tabelas):
```powershell
python .\src\main.py --tabelas
```

Arquivos gerados
- `data/tabelas/status_servidores.csv` — tabela de status por timestep (tamanho das filas, servidores e atendentes ativos, realocações por timestep).
- `data/tabelas/transferencias.csv` — registro das realocações/redirecionamentos entre servidores.
- `data/relatorios/resumo_simulacao.txt` — resumo em texto equivalente ao que aparece no terminal.
- `data/graficos/*` — gráficos PNG: `atendimentos_por_servidor.png`, `falhas_por_timestep.png`, `percentual_redirecionamentos.png`.

Observações sobre `data/filas/`
- A pasta `data/filas/` contém placeholders (`fila_tecnico.py`, `fila_vendas.py`). Atualmente são arquivos vazios usados como marcadores ou para futuras implementações de persistência de filas. Se desejar persistir ou reusar filas entre execuções, podemos implementar os módulos nessa pasta para carregar/salvar estados.

Design e garantia
- Os gráficos são gerados a partir dos dados da simulação (objetos em memória) que são também persistidos em CSVs. Os gráficos refletem a saída final da simulação.
- A simulação registra eventos (`logs`) com `atendimento`, `falha_servidor`, `falha_atendente`, `realocacao`, `entrada_atendente`, `saida_atendente`.

Alterações notáveis
- Implementado `step()` em `SimulacaoAtendimentoDistribuido` para execução por timestep.
- `Supervisor` executa a simulação passo a passo para monitoramento.
- Quando `--tabelas` é usado, parâmetros são ajustados automaticamente para testes rápidos (evita estouro de buffer imediato).

Testes
- A suíte de testes usa `pytest`. Execute:

```powershell

```

Próximos passos sugeridos
- Implementar persistência real das filas em `data/filas` se quiser recuperar estado entre execuções.
- Adicionar mais testes unitários cobrindo falhas programadas e realocações.

Contato
- Se quiser que eu altere o comportamento do modo de teste (`--tabelas`) ou que adicione documentação adicional, me diga e eu atualizo.

Commit e pre-commit
-------------------

Siga estes passos para manter o histórico de commits limpo e garantir que os hooks de qualidade sejam executados automaticamente antes de cada commit.

- **Instalar dependências de desenvolvimento**:

  ```powershell
  python -m pip install --upgrade pip
  pip install -r requirements-dev.txt
  ```

- **Instalar os hooks do `pre-commit`** (uma vez por máquina/clone):

  ```powershell
  pre-commit install
  ```

- **Rodar os hooks manualmente** (útil antes de commitar):

  ```powershell
  pre-commit run --all-files
  ```

- **Fluxo de commit recomendado**:

  ```powershell
  git add .
  git commit -m "Mensagem curta e descritiva do que mudou"
  git push origin <sua-branch>
  ```

  Os hooks configurados em `.pre-commit-config.yaml` serão executados automaticamente ao dar `git commit`. Caso algum hook fpytest -qalhe, corrija os problemas apontados, adicione as alterações e tente commitar novamente.

- **Atualizar hooks**:

  ```powershell
  pre-commit autoupdate
  ```

- **Dica**: a pipeline CI também executa linters e testes no push/PR. Certifique-se de que os hooks locais passam antes de abrir um pull request para reduzir feedbacks da CI.

Se quiser que eu adicione instruções adicionais (ex.: git hooks customizados, commit message template, ou integração com ferramentas de CI/CD), me avise.
