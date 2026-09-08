# Como contribuir

Obrigado por ajudar o Hermes Knowledge Kit.

## Antes de abrir um PR

1. Abra uma issue descrevendo o problema ou melhoria.
2. Mantenha o escopo pequeno e sem dependências novas quando a biblioteca padrão bastar.
3. Use apenas exemplos fictícios; nunca inclua credenciais, sessões, caminhos privados ou dados pessoais.
4. Rode:

```bash
python3 -m compileall -q src tests scripts
python3 -m unittest discover -s tests -v
python3 scripts/check_release_tree.py
```

## Princípios do projeto

- dry-run não escreve;
- instalação e reinstalação são idempotentes;
- conflito preserva o arquivo do usuário;
- operações destrutivas obedecem ao manifesto e aos hashes;
- erros críticos fecham com código diferente de zero;
- mudanças de comportamento incluem teste de regressão.

Ao contribuir, você concorda que sua contribuição será licenciada sob a licença MIT do repositório.
