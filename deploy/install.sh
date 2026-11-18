#!/usr/bin/env bash
set -euo pipefail
if [[ "$EUID" -ne 0 ]]; then echo "Jalankan sebagai root: bash deploy/install.sh"; exit 1; fi
APP_DIR="/opt/facebook-ai"
DATA_DIR="/data/facebook-ai"
REPO="https://github.com/imambaihakki01/ai_agent.git"
echo "== Facebook AI Agent installer =="
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 python3-venv python3-pip nginx openssl
if ! id facebook-ai >/dev/null 2>&1; then useradd --system --home "$DATA_DIR" --shell /usr/sbin/nologin facebook-ai; fi
mkdir -p "$DATA_DIR" /etc/ssl/facebook-ai
chmod 700 "$DATA_DIR"
if [[ -d "$APP_DIR/.git" ]]; then
  git -C "$APP_DIR" fetch origin
  git -C "$APP_DIR" checkout main
  git -C "$APP_DIR" pull --ff-only origin main
else
  if [[ -e "$APP_DIR" ]]; then mv "$APP_DIR" "${APP_DIR}.backup.$(date +%Y%m%d%H%M%S)"; fi
  git clone --depth 1 "$REPO" "$APP_DIR"
fi
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
if [[ ! -f "$APP_DIR/.env" ]]; then
  echo
  read -rsp "Buat password dashboard (minimal 14 karakter): " DASH_PASS; echo
  if [[ "$(printf %s "$DASH_PASS" | wc -c)" -lt 14 ]]; then echo "Password terlalu pendek."; exit 1; fi
  read -rsp "Masukkan NVIDIA API Key: " NVIDIA_KEY; echo
  if [[ -z "$NVIDIA_KEY" ]]; then echo "NVIDIA API Key wajib diisi."; exit 1; fi
  export APP_SECRET="$(openssl rand -hex 48)" DASH_PASS NVIDIA_KEY DATA_DIR
  python3 - <<'PY'
import json, os
p="/opt/facebook-ai/.env"
values={"APP_ENV":"production","APP_HOST":"127.0.0.1","APP_PORT":"8000","APP_SECRET_KEY":os.environ["APP_SECRET"],"DASHBOARD_PASSWORD":os.environ["DASH_PASS"],"COOKIE_SECURE":"true","SESSION_MAX_AGE":"43200","DATA_DIR":os.environ["DATA_DIR"],"NVIDIA_API_KEY":os.environ["NVIDIA_KEY"],"NVIDIA_BASE_URL":"https://integrate.api.nvidia.com/v1","NVIDIA_MODEL":"nvidia/nemotron-3-ultra-550b-a55b","NVIDIA_TIMEOUT_SECONDS":"120"}
with open(p,"w") as f:
    for k,v in values.items(): f.write(f"{k}={json.dumps(v)}\n")
PY
  chmod 600 "$APP_DIR/.env"
fi
if [[ ! -s /etc/ssl/facebook-ai/privkey.pem ]]; then
  openssl req -x509 -nodes -newkey rsa:3072 -days 825 -keyout /etc/ssl/facebook-ai/privkey.pem -out /etc/ssl/facebook-ai/fullchain.pem -subj "/CN=$(hostname -f 2>/dev/null || hostname)" -addext "subjectAltName=IP:127.0.0.1,DNS:localhost"
  chmod 600 /etc/ssl/facebook-ai/privkey.pem
fi
install -m 644 "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/facebook-ai
ln -sfn /etc/nginx/sites-available/facebook-ai /etc/nginx/sites-enabled/facebook-ai
rm -f /etc/nginx/sites-enabled/default
nginx -t
install -m 644 "$APP_DIR/deploy/facebook-ai.service" /etc/systemd/system/facebook-ai.service
chown -R facebook-ai:facebook-ai "$DATA_DIR"
chown -R root:facebook-ai "$APP_DIR"
chmod 750 "$APP_DIR"
chmod 640 "$APP_DIR/.env"
systemctl daemon-reload
systemctl enable --now facebook-ai
systemctl enable --now nginx
echo
echo "INSTALL SELESAI"
echo "Buka: https://IP-VPS:8443"
echo "Sertifikat awal self-signed; browser menampilkan peringatan sertifikat."
echo "Di panel Instanbox, publish TCP port 8443. Jangan publish 8000, 5901, atau 9222."
echo "Status: systemctl status facebook-ai nginx"
