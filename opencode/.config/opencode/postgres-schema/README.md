# OpenCode PostgreSQL Schema Inspector

Safe PostgreSQL schema inspection CLI used by the global OpenCode `postgres_schema` tool.

Install from dotfiles:

```bash
cd /Users/ngogiahuy/dotfiles
stow --restow --target="$HOME" opencode
```

Run directly from a configured project:

```bash
uv run --project ~/.config/opencode/postgres-schema postgres-schema \
  --schema mapping_test \
  --table p_daily_ssps \
  --include-ddl
```

The CLI searches upward from the current directory for `.opencode/postgres-schema.json`. It loads `.env` from that project root when present, without overriding existing environment variables. It refuses to connect when project policy or required connection env vars are missing. Project config stores env-var names for host, port, database, user, and password; the tool builds the PostgreSQL URL internally.

Stdout is always JSON. Diagnostics go to stderr and must not contain credentials.
