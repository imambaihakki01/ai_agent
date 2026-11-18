# Security

- Keep `.env`, SQLite database, logs, backups, and browser profiles out of Git.
- Installer generates a unique secret and asks for a strong dashboard password.
- Dashboard must use HTTPS. Initial self-signed certificate is bootstrap-only; use a trusted certificate for regular access.
- Expose only TCP 8443 through the provider panel. Keep 8000, 5901, and 9222 private.
- Uvicorn binds to 127.0.0.1 and runs as unprivileged user facebook-ai.
- Session cookie is HttpOnly, SameSite=Strict, Secure; POST forms require CSRF token.
- Login attempts are limited per client address.
- NVIDIA API key stays in the .env file and is never sent in model prompts.
- Never store Facebook passwords, OTPs, or session cookies in this application.
- No arbitrary shell tool or automatic Facebook action is exposed to the model.
