# Arquitetura

## Componentes

1. **CLI stdlib** (`src/hermes_knowledge_kit/cli.py`): resolve destino, diagnostica Hermes e executa o ciclo de vida.
2. **Área local** (`<home>/knowledge-kit/`): único root gerido; contém contexto e documentos.
3. **Estado técnico** (`.kit-state/`): manifesto, journal transitório e lock transitório.
4. **Zipapp** (`scripts/build_zipapp.py`): artefato executável sem `pip` nem dependência de runtime além de Python.

## Fronteira de escrita

O CLI recebe o diretório exato do profile por `--home` ou `HERMES_HOME`; sem ambos usa `$HOME/.hermes`. Nunca procura ou enumera outros profiles. Todas as escritas são descendentes de `knowledge-kit/`.

## Ativação no Hermes

O núcleo usa `AGENTS.md` descoberto a partir do CWD, mecanismo público do Hermes. Não instala skill no profile porque isso teria alcance global. O usuário abre uma sessão com CWD na área instalada.

## Transação

`install` cria lock exclusivo, persiste journal antes dos templates, grava cada arquivo em temporário exclusivo com `fsync` e `os.replace`, grava manifesto e remove journal/lock. Uma interrupção deixa evidência recuperável. `rollback` só remove arquivo cujo hash ainda corresponde ao journal.

## Estados

- `absent`: área não existe.
- `installed`: manifesto válido e arquivos intactos.
- `drift`: editado, ausente ou extra.
- `interrupted`: journal presente.
- `conflict`: operação preservou conteúdo divergente.

Erros estruturais (manifesto inválido, links, arquivo especial, área ocupada sem manifesto) falham fechados com código 2.

## Alternativas recusadas

- Plugin/provider: acoplamento e superfície de risco maiores.
- Skill global automática: contradiz isolamento.
- Banco vetorial/embeddings/SaaS: desnecessários para validar navegação Markdown.
- GUI: amplia escopo antes de evidência de uso.
