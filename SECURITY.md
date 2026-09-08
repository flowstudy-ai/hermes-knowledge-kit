# Segurança

## Escopo

O núcleo escreve somente em `<HERMES_HOME>/knowledge-kit/`. Não lê `.env`, autenticação, sessões, bancos de memória ou outros profiles; não usa rede; não cria crons; não muda `config.yaml`, SOUL.md, USER.md, MEMORY.md, AGENTS.md ou MAPA.md preexistentes fora da área.

## Garantias e limites

- Manifesto e journal têm schema e paths allowlisted.
- Symlinks, hardlinks e arquivos especiais são recusados na árvore gerida.
- Hash SHA-256 detecta alteração; não prova autoria ou autenticidade.
- Locks são cooperativos e não defendem contra processo malicioso com o mesmo UID.
- AGENTS.md orienta o modelo; não impõe permissões técnicas às ferramentas do Hermes.
- O scanner de testes reduz risco de vazamento conhecido, mas não detecta todo segredo possível.

## Relato de vulnerabilidade

Antes da publicação, registre o achado localmente sem incluir segredo ou dado pessoal. Após existir repositório público, habilite *Private vulnerability reporting* no GitHub e substitua este parágrafo pelo canal definitivo. Não abra issue pública contendo exploit funcional contra dados reais.

Inclua: versão, sistema operacional, comando mínimo, resultado esperado/observado e fixture fictícia. Nunca envie token, `.env`, `auth.json`, sessão ou banco real.

## Suporte

Somente Linux, Python 3.11+ e Hermes 0.21.0 entram na matriz inicial, condicionados aos testes documentados. Outros ambientes são não testados.
