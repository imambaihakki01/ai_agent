# NEXUS AI CLI

Local-first hybrid TypeScript + Python coding-agent foundation with a browser dashboard for model configuration.

NEXUS is an independent project inspired by common terminal coding-agent workflows. It is not affiliated with Anthropic or OpenClaude and does not copy their proprietary branding or implementation.

## Requirements
- Node.js 20.11+
- Python 3.11+
- A model API key or a local OpenAI-compatible server such as Ollama / LM Studio

## Quick start
1. npm install
2. npm run build
3. python -m venv .venv
4. Activate the venv, then run pip install -e ./python
5. Start dashboard: node dist/cli.js dashboard
6. Configure an OpenAI-compatible provider at http://127.0.0.1:4317
7. In another terminal start agent: python -m nexus_agent.main
8. Run node dist/cli.js chat

Development: npm run dev -- dashboard or npm run dev -- chat.

## Provider configuration
Any OpenAI-compatible Chat Completions endpoint can be configured: OpenAI, OpenRouter, DeepSeek, Groq, Mistral, Ollama, LM Studio and custom gateways. Enter base URL, model ID and API key in the dashboard. Ollama can omit the key. API keys are encrypted using AES-256-GCM and stored in ~/.nexus; the master key is owner-only where supported. Decrypted keys are not returned to the browser.

## CLI
- nexus dashboard — start the local dashboard/API
- nexus chat — interactive coding-agent session
- nexus doctor — inspect agent availability
- nexus skills — list bundled skills
- /allow-write — explicitly enable workspace file writes for the current session
- /allow-shell — explicitly enable shell execution for the current session
- /help and /exit — help and quit

Both write and shell permissions start disabled. Only enable them in a workspace you trust. Shell commands execute in the selected workspace with a 60-second maximum timeout.

## Agent tools
The bounded tool loop supports listing files, reading files, text search, writing files (approval required), and shell commands (approval required). Tool execution is capped at eight rounds per user request. Project CLAUDE.md and AGENTS.md instructions and discovered SKILL.md files are included as context, but are treated as untrusted input and cannot override safety rules.

## Skills
Bundled skills: deep-research, code-architect, fullstack-engineer, debug-master, code-review, test-engineer, security-auditor, database-architect and git-master. Add project skills under .nexus/skills/<name>/SKILL.md or user skills under ~/.nexus/skills/<name>/SKILL.md.

## Safety and current scope
The dashboard binds to 127.0.0.1 by default. Do not expose it publicly. Workspace tools reject paths outside the selected workspace. This is an initial functional agent foundation, not full OpenClaude feature parity. MCP integration, provider-native adapters beyond OpenAI-compatible chat, robust token streaming, durable sessions, checkpoints, subagent orchestration, task planning UI and richer approval UX remain to be implemented and tested.

## Development
npm run typecheck
npm run build
pip install -e ./python
pytest python/tests
