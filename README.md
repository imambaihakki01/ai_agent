# Facebook AI Agent — VPS Ready

Dashboard AI responsif untuk HP, berjalan pada VPS Debian/Ubuntu dan memakai NVIDIA NIM.

## Fitur
- Dashboard mobile pada HTTPS port 8443.
- Login dashboard, cookie HttpOnly/SameSite/Secure, CSRF protection, pembatasan percobaan login.
- Chat NVIDIA NIM dengan riwayat SQLite.
- Pintasan ide konten, caption, dan kalender konten.
- Installer otomatis: Nginx, systemd, virtualenv, database, dan direktori data.
- Aplikasi berjalan sebagai user Linux non-root.

## Instalasi

Di VPS sebagai root:

    git clone https://github.com/imambaihakki01/ai_agent.git
    cd ai_agent
    bash deploy/install.sh

Installer meminta password dashboard dan NVIDIA API Key. Kunci disimpan hanya di `/opt/facebook-ai/.env`, tidak di Git.

Setelah selesai:
1. Di panel Instanbox, publish TCP port **8443**.
2. Buka `https://IP-VPS:8443` dari HP.
3. Sertifikat awal self-signed sehingga browser menampilkan peringatan. Untuk akses normal tanpa peringatan, pasang domain dan sertifikat TLS valid.
4. Jangan publikasikan port 8000, 5901, atau 9222.

## Operasional

    systemctl status facebook-ai nginx
    journalctl -u facebook-ai -f
    systemctl restart facebook-ai

Update:

    cd /opt/facebook-ai
    git pull --ff-only origin main
    .venv/bin/pip install -r requirements.txt
    systemctl restart facebook-ai

Backup berkala: direktori `/data/facebook-ai`.

## NVIDIA NIM

- Base URL: `https://integrate.api.nvidia.com/v1`
- Model: `nvidia/nemotron-3-ultra-550b-a55b`

## Batas Facebook

Aplikasi ini membantu menulis dan menganalisis konten yang pengguna berikan. Login Facebook dilakukan manual. Tidak ada pengambilan password/cookie, bypass CAPTCHA/2FA, scraping tersembunyi, atau auto-post/auto-message. Draf ditinjau dan diposting sendiri oleh pengguna.
