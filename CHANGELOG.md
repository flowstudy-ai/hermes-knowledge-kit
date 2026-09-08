# Changelog

Todas as mudanças relevantes serão registradas aqui. O formato segue Keep a Changelog; o projeto usa versionamento semântico após a primeira publicação.

## [0.1.0] — 2026-09-08

### Adicionado
- CLI `doctor`, `plan`, `install`, `verify`, `status`, `uninstall` e `rollback`.
- Dry-run sem mutação e fixture fictícia opt-in.
- Manifesto com hashes, journal de interrupção e lock cooperativo.
- Rejeição de path relativo, traversal, symlink, hardlink, arquivo especial e manifesto adulterado.
- Templates locais AGENTS/MAPA/context/projects/procedures.
- Testes stdlib, zipapp instalável e CI sem credenciais.

### Limites
- Auditoria documental rica, Holographic e backup foram adiados.
- Windows e macOS não foram testados.
