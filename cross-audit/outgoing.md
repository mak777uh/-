# Исходящие аудиты

Аудиты четырёх проектов владельца. **Доставить внутрь репозиториев нельзя**: все ключи в `~/.ssh`
(`gh_agent_audits`, `gh_agent_specter`, `gh_agent_specter-diy`, `gh_agent_cases`, `gh_deploy_morph`)
дают **только чтение** — `git push` отвергается с «Permission denied to deploy key» по всем репозиториям.
Нужен либо ключ с правом записи, либо ручное копирование (файлы самодостаточные).

| репозиторий | находок | файл |
|---|---|---|
| flowguard-spec | 30 (5 ломающих) | [2026-10-29-flowguard-spec-audit.md](outgoing/2026-10-29-flowguard-spec-audit.md) |
| herness | 25 (6 ломающих) | [2026-10-29-herness-audit.md](outgoing/2026-10-29-herness-audit.md) |
| lexspec | 16 (3 ломающих) | [2026-10-29-lexspec-audit.md](outgoing/2026-10-29-lexspec-audit.md) |
| VecDHT | 16 (3 ломающих) | [2026-10-29-VecDHT-audit.md](outgoing/2026-10-29-VecDHT-audit.md) |

Кладут как `<repo>/cross-audit/2026-10-29-deepseek-audit.md`.
