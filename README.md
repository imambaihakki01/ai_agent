# Claude CLI

An independent, local-first Claude-style coding-agent CLI built with TypeScript and Python, with a browser dashboard, OpenAI-compatible model routing, persistent sessions, workspace tools, MCP stdio integration and an extensible skills system.

Claude CLI is an independent project inspired by terminal coding-agent workflows. It is not affiliated with Anthropic, is not the official Claude Code product, and does not copy OpenClaude's proprietary branding or implementation.

## Requirements

- Node.js 20.11+
- Python 3.11+
- A model API key or a local OpenAI-compatible server (Ollama / LM Studio)

## Quick start

```bash
git clone https://github.com/imambaihakki01/ai_agent.git
cd ai_agent
npm install
npm run build
npm link
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -e "./python[dev]"
```

Start the dashboard and configure a model profile:

```bash
claude dashboard
```

Open http://127.0.0.1:4317, add a provider, and save it. In another terminal (with the Python environment activated), start the agent runtime:

```bash
python -m claude_agent.main
```

Then start the CLI:

```bash
claude
```

Development: `npm run dev -- dashboard` or `npm run dev -- chat`. Use `claude --help` and `claude --version` for CLI help and version.

## Providers

The dashboard accepts OpenAI-compatible Chat Completions endpoints, including OpenAI, OpenRouter, DeepSeek, Groq, Mistral, Ollama, LM Studio and compatible gateways. Configure the base URL, model ID and optional API key. The runtime normalizes common base URL forms and retries transient network / rate-limit / server errors up to three attempts.

API keys are encrypted with AES-256-GCM and stored under `~/.claude-cli`; the master key is owner-only where supported. Decrypted keys are not returned to the browser. Provider-native APIs that do not expose an OpenAI-compatible chat endpoint are not yet supported.

## CLI

- `claude dashboard` — start the local dashboard/API
- `claude chat` — interactive coding-agent session (session history persists)
- `claude doctor` — inspect agent availability
- `claude skills` — list bundled skills
- `/allow-write` — toggle workspace file writes for the current CLI session
- `/allow-shell` — toggle shell execution for the current CLI session
- `/help` and `/exit` — help and quit

Write and shell permissions start disabled. Only enable them in a workspace you trust. Shell commands run in the selected workspace with a 60-second maximum timeout.

## Agent runtime

The bounded tool loop supports listing files, reading files, text search, writing files (approval required), shell commands (approval required), tools discovered from configured MCP servers, and bounded advisory sub-agents (planner, reviewer, researcher and tester). Sub-agents have no workspace tools and cannot recursively delegate. Tool execution is capped at eight rounds per user request.

Sessions, messages and file-write checkpoints are stored in `~/.claude-cli/sessions.sqlite3`. Session history is scoped to its canonical workspace path. Checkpoints retain the previous contents of a file before an agent write; this is a recovery record, not an automatic rollback feature.

Project `CLAUDE.md` / `AGENTS.md` instructions and discovered `SKILL.md` files are included as context but are treated as untrusted input and cannot override runtime safety rules.

## MCP stdio servers

MCP servers are opt-in and configured through the `CLAUDE_MCP_SERVERS` environment variable as JSON. Example:

```bash
export CLAUDE_MCP_SERVERS='{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/absolute/path/to/workspace"]
  }
}'
```

Restart the Python runtime after changing this variable. Claude CLI starts configured commands as local subprocesses without a shell, performs MCP initialization and tool discovery, then invokes the selected tool. Only configure commands and environment values you trust. MCP server tools execute with the operating-system permissions of the Claude CLI process; review server documentation and access scopes before enabling them.

## Skills

Bundled skills: deep-research, code-architect, fullstack-engineer, debug-master, code-review, test-engineer, security-auditor, database-architect and git-master.

Add project skills under `./.claude-cli/skills/<name>/SKILL.md` or user skills under `~/.claude-cli/skills/<name>/SKILL.md`.

## Security notes

- Dashboard and agent runtime bind to loopback by default. Do not expose them directly to the public internet.
- Workspace file helpers reject paths outside the selected workspace.
- File writes and shell execution are disabled by default in each CLI session.
- MCP commands are arbitrary local programs selected by the operator; only configure trusted servers.
- Keep `~/.claude-cli` private. It contains encrypted provider credentials and conversation history.
- Checkpoints store prior file contents in the local SQLite database. Protect and back up that directory accordingly.

## Development and CI

```bash
npm install
npm run typecheck
npm run build
pip install -e "./python[dev]"
pytest -q python/tests
```

GitHub Actions runs TypeScript type-check/build and Python tests on pushes to `main` and pull requests.

## Current scope

Claude CLI now includes a persistent coding-agent loop, workspace tools, local provider dashboard, encrypted keys, session history, write checkpoints, MCP stdio tool discovery and CI automation. This is an independent community project, not an official Anthropic product or a claim of complete OpenClaude feature parity or a certified production release. Streaming UX, native provider-specific adapters, interactive per-tool approval prompts, reliable rollback/restore UI, persistent specialist agents with independent contexts, richer task planning, broad platform testing and a security review remain future work. Validate the CI run and test against the actual providers and MCP servers you intend to use before relying on it for important repositories.
