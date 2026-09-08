# Hermes Knowledge Kit

[![CI](https://github.com/flowstudy/hermes-knowledge-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/flowstudy/hermes-knowledge-kit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Kit local e reversível para transformar documentos Markdown usados com Hermes Agent em conhecimento recuperável, auditável e portátil — sem banco vetorial, SaaS, cron ou alteração da identidade do agente.

> Versão 0.1 para Linux. Ainda não validada por usuários externos.

## O que entrega

- `doctor`, `plan`, `install --dry-run`, `install`, `verify`, `status`, `uninstall` e `rollback`;
- área única em `<HERMES_HOME>/knowledge-kit/`;
- AGENTS.md e MAPA.md locais, templates de contexto/projetos/procedimentos;
- manifesto com SHA-256, journal de interrupção e lock cooperativo;
- preservação de arquivos editados pelo usuário;
- fixture inteiramente fictícia e opt-in para QA;
- artefato `.pyz` sem dependências Python externas.

## Requisitos comprovados localmente

| Item | Estado |
|---|---|
| Linux | testado no ambiente de desenvolvimento |
| Python 3.11+ | exigido; testes locais executados em 3.13 |
| Hermes 0.21.0 | `doctor`, ciclo do zipapp e E2E LLM executados localmente |
| macOS/Windows | não testados; sem suporte anunciado |

## Instalação rápida

Baixe `hermes-knowledge-kit.pyz` na página de [Releases](https://github.com/flowstudy/hermes-knowledge-kit/releases), confira o SHA-256 publicado e execute:

```bash
python3 hermes-knowledge-kit.pyz doctor
python3 hermes-knowledge-kit.pyz install --dry-run
python3 hermes-knowledge-kit.pyz install
```

## Desenvolvimento

### Executar do checkout

```bash
PYTHONPATH=src python3 -m hermes_knowledge_kit doctor
PYTHONPATH=src python3 -m hermes_knowledge_kit plan
PYTHONPATH=src python3 -m hermes_knowledge_kit install --dry-run
PYTHONPATH=src python3 -m hermes_knowledge_kit install
```

### Construir artefato portátil

```bash
python3 scripts/build_zipapp.py
python3 dist/hermes-knowledge-kit.pyz doctor
python3 dist/hermes-knowledge-kit.pyz install --dry-run
python3 dist/hermes-knowledge-kit.pyz install
```

O destino é `HERMES_HOME` quando definido; senão `$HOME/.hermes`. Para um profile descartável, use um path absoluto:

```bash
python3 dist/hermes-knowledge-kit.pyz --home /tmp/hermes-qa install --fixture
```

`--home` e `--allow-untested-hermes` vêm **antes** do subcomando.

## Uso

```bash
python3 dist/hermes-knowledge-kit.pyz status
python3 dist/hermes-knowledge-kit.pyz verify
python3 dist/hermes-knowledge-kit.pyz uninstall
python3 dist/hermes-knowledge-kit.pyz rollback
```

- Código `0`: operação limpa/concluída.
- Código `2`: entrada ou estado inseguro; nenhuma ação destrutiva deve ser presumida.
- Código `3`: drift/conflito; arquivos divergentes foram preservados.

Depois de instalar, abra uma sessão Hermes com CWD em `<HERMES_HOME>/knowledge-kit/`. O contexto local orienta o agente a começar por MAPA.md e citar fontes. O kit não ativa política global.

## Onde cada conhecimento vive

| Conteúdo | Lugar |
|---|---|
| identidade e tom do agente | SOUL.md existente — o kit não toca |
| preferências estáveis do usuário | USER.md existente — o kit não toca |
| contexto geral curto | MEMORY.md existente — o kit não toca |
| conhecimento extenso e fontes | `knowledge-kit/context/` ou `projects/` |
| procedimentos maduros | skills, por instalação separada e consciente |
| histórico | `session_search` do Hermes |
| hashes/journal/lock | `.kit-state/` — estado técnico, não conhecimento |

## Segurança

O CLI não lê credenciais, sessões ou bancos e não usa rede. Recusa destino relativo, traversal, symlink, hardlink, arquivo especial, manifesto fora da allowlist e área ocupada sem manifesto. Uninstall e rollback removem somente conteúdo ainda igual ao hash registrado.

Isso não é sandbox: um agente com acesso geral ao filesystem pode contornar instruções Markdown. SHA-256 detecta mudança, não autoria. Veja [SECURITY.md](SECURITY.md) e [Arquitetura](docs/ARQUITETURA.md).

## Testes

```bash
python3 -m compileall -q src tests scripts
python3 -m unittest discover -s tests -v
```

A CI escrita não é CI remota executada. O E2E com modelo é separado dos testes determinísticos e exige ambiente autenticado mínimo e isolado.

## Documentação

- [Arquitetura](docs/ARQUITETURA.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Roteiro de piloto](docs/PILOTO.md)
- [Changelog](CHANGELOG.md)

## Fora do 0.1

Auditoria documental rica, Holographic, backup, GUI, embeddings, banco vetorial, integrações externas, sincronização e migração complexa de profiles. Holographic não indexa Markdown automaticamente e não substitui RAG.

## Licença e atribuições

Código sob licença MIT; veja [LICENSE](LICENSE). Runtime: somente biblioteca padrão do Python. Nenhum código, dado, sessão ou configuração privada foi redistribuído. Hermes Agent é projeto da Nous Research e não faz parte deste repositório; consulte a [documentação oficial](https://hermes-agent.nousresearch.com/docs/).

Contribuições e relatos de uso são bem-vindos por issues e pull requests.
