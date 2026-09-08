# Troubleshooting

## `Hermes não encontrado no PATH`

Instale o Hermes Agent pelo procedimento oficial e confirme `hermes --version`. O kit não instala nem autentica Hermes.

## `versão Hermes não testada`

Consulte a matriz do README. Para diagnóstico consciente, coloque `--allow-untested-hermes` antes do subcomando. Isso não transforma a versão em suportada.

## `área ocupada` ou `manifesto inválido`

Não apague conteúdo automaticamente. Rode `status`, preserve seus arquivos fora da área e inspecione `.kit-state/manifest.json` sem inserir paths novos. O CLI não tem `force`.

## `interrupted`

Rode `rollback`. Arquivos iguais ao journal são removidos; divergentes são preservados e retornam `conflict`.

## `drift` / código 3

O kit encontrou arquivo editado, ausente ou extra. `uninstall` remove somente artefatos intactos e preserva o restante.

## `lock ativo`

Não mate processo automaticamente. Confirme se há outra operação em curso. Somente `rollback` lida com lock stale acompanhado de journal válido.

## Sessão não usa o mapa

Inicie a sessão com CWD no diretório `knowledge-kit/`. O kit não altera a configuração global nem instala skill no profile.
