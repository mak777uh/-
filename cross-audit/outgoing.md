# Исходящие аудиты

Здесь лежат аудиты чужих проектов владельца. **Доставить их внутрь репозиториев не удалось**:
все ключи в `~/.ssh` (`gh_agent_audits`, `gh_agent_specter`, `gh_agent_specter-diy`, `gh_agent_cases`,
`gh_deploy_morph`) дают **только чтение** — `git push` отвергается с «Permission denied to deploy key»
по всем четырём репозиториям. Нужен либо ключ с правом записи, либо добавление `gh_agent_audits.pub`
в каждый репозиторий с доступом write, либо ручное копирование.

| репозиторий | файл |
|---|---|
| 29 | [2026-10-29-herness-audit.md](outgoing/2026-10-29-herness-audit.md) |
| 29 | [2026-10-29-lexspec-audit.md](outgoing/2026-10-29-lexspec-audit.md) |
| 29 | [2026-10-29-VecDHT-audit.md](outgoing/2026-10-29-VecDHT-audit.md) |
