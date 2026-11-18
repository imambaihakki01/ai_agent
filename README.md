# Facebook AI Agent (VPS)

A cautious, phone-friendly AI workspace for drafting and reviewing Facebook content on your existing Instanbox VPS. The first milestone provides a protected FastAPI dashboard and an NVIDIA NIM chat connection. Browser control and Facebook actions are intentionally not enabled by default.

## Current scope
- FastAPI backend and responsive dashboard.
- NVIDIA NIM Chat Completions client using the OpenAI-compatible API.
- SQLite conversation history.
- Password-protected dashboard with signed, HttpOnly session cookie.
- Health endpoint.
- No Facebook password, cookie, browser profile, API key, or other secret is stored in Git.

## Safety boundaries
- Sign in to Facebook manually in the local Chromium profile; never send Facebook credentials or session cookies to the model.
- This project does not bypass CAPTCHA, 2FA, platform limits, or Facebook safeguards.
- Do not assume a browser login authorizes automated posting, messaging, or scraping. Prefer official/authorized interfaces; require explicit human approval for consequential actions.
- No arbitrary shell tool is exposed to the model.
- The dashboard must be served over HTTPS in production. Keep FastAPI bound to 127.0.0.1:8000 behind the reverse proxy on port 8443.

## VPS layout
- Code: /opt/facebook-ai
- Runtime data: /data/facebook-ai
- Dashboard public entry: HTTPS port 8443
- Internal API: 127.0.0.1:8000

## Quick start
1. Create a Python 3.13 virtual environment.
2. Install requirements.txt.
3. Copy .env.example to .env, set a long random APP_SECRET_KEY, a strong DASHBOARD_PASSWORD, and NVIDIA_API_KEY.
4. Set COOKIE_SECURE=true when served over HTTPS.
5. Run uvicorn app.main:app --host 127.0.0.1 --port 8000.

Never commit .env. Do not bind port 8000 to a public interface.

## NVIDIA NIM
Default base URL: https://integrate.api.nvidia.com/v1
Default model: nvidia/nemotron-3-ultra-550b-a55b

Model/API availability and tool-calling support should be verified against the current NVIDIA model page before enabling agent tools. The initial chat endpoint is text chat only and does not execute tools.

## Development
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open the dashboard through your HTTPS reverse proxy. For local-only testing, use an SSH tunnel rather than exposing port 8000.
