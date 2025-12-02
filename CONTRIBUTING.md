## Contribuindo para o projeto

Obrigado por contribuir! Siga estas instruções simples para garantir que suas PRs sejam aceitas rapidamente.

1. Faça um fork do repositório e crie uma branch com a feature/bugfix.
2. Execute os testes localmente: `pytest -q`.
3. Formate o código e verifique linters (pre-commit fará isso automaticamente):
   - Instale hooks: `pip install pre-commit && pre-commit install`
   - Rode manualmente: `pre-commit run --all-files`
4. Abra um Pull Request descrevendo a mudança e referencie issues relacionados.

Regras básicas:
- Escreva testes para bugs ou features relevantes.
- Mantenha o estilo consistente (Black + isort + ruff).
- Não comite dados sensíveis.
