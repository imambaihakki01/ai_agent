# Security notes

- Keep the .env file, database files, logs, and Chromium profile outside Git.
- Use a unique high-entropy APP_SECRET_KEY and strong dashboard password.
- Set COOKIE_SECURE=true only when HTTPS is correctly configured; production must use HTTPS.
- Bind Uvicorn to 127.0.0.1 and expose only the reverse proxy port.
- Do not publish VNC (5901), FastAPI (8000), or Chromium debugging (9222).
- Restrict VPS SSH access at the provider firewall where possible.
- Do not store Facebook credentials or session cookies in prompts, logs, or model context.
- Browser automation is not implemented in this initial milestone. Add it only with explicit allowlisted actions, user approval, audit logs, and compliance with platform rules.
