# NEXUS AI CLI

Local-first hybrid TypeScript + Python coding-agent foundation with a local browser dashboard for model configuration.

NEXUS is an independent project inspired by common terminal coding-agent workflows. It is not affiliated with Anthropic or OpenClaude and does not copy their proprietary branding or implementation.

## Requirements
- Node.js 20.11+
- Python 3.11+
- Model API key or local OpenAI-compatible server (Ollama / LM Studio)

## Quick start
1. npm install
2. npm run build
3. python -m venv .venv
4. Activate the venv, then: pip install -e ./python
5. Start dashboard: node dist/cli.js dashboard
6. Configure a provider at http://127.0.0.1:4317
7. In another terminal start agent: python -m nexus_agent.main
8. Run node dist/cli.js chat

Development: npm run dev -- dashboard or npm run dev -- chat.

## Providers
Any OpenAI-compatible Chat Completions endpoint can be configured: OpenAI, OpenRouter, DeepSeek, Groq, Mistral, Ollama, LM Studio and custom gateways. Enter base URL, model ID and API key in the dashboard. Ollama can omit the key. API keys are encrypted using AES-256-GCM and stored in ~/.nexus; the master key is owner-only where supported. Decrypted keys are never sent to the browser.

## Commands
nexus dashboard | nexus chat | nexus doctor | nexus skills

## Safety and current scope
Dashboard binds to 127.0.0.1 by default. Do not expose it publicly. Workspace file helpers reject path traversal and shell execution requires explicit approval. The initial chat endpoint provides model-backed guidance and skill context; autonomous tool loops, streaming, MCP, durable sessions, checkpoints and subagent routing are future milestones. This is a runnable foundation, not a claim of full feature parity.

## Development
npm run typecheck && npm run build
pip install -e ./python
pytest python/tests
