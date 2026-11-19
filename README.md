# Facebook AI Agent — VPS Edition

Dashboard kerja Facebook berbasis AI untuk VPS Debian 13/Ubuntu, memakai NVIDIA NIM dan Chromium persisten.

## Fitur
- Dashboard responsif untuk HP/desktop dengan autentikasi, CSRF, cookie aman, dan pembatasan login.
- Chat AI NVIDIA NIM dan riwayat SQLite.
- Bantuan ide konten, caption, hashtag, kalender publikasi, serta analisis teks komentar/pesan yang pengguna berikan.
- Panel browser Chromium persisten untuk membuka Facebook dan login manual langsung oleh pemilik akun.
- Interaksi browser manual: refresh tampilan, klik, dan mengetik. Browser hanya mengizinkan domain Facebook resmi melalui HTTPS.
- Satu service systemd `facebook-ai`, satu direktori aplikasi `/opt/facebook-ai`, data persisten di `/data/facebook-ai`.

## Instalasi baru
Jalankan sebagai root di VPS:

    git clone https://github.com/imambaihakki01/ai_agent.git
    cd ai_agent
    bash deploy/install.sh

Installer menyiapkan Python, Chromium, Nginx, systemd, virtualenv, direktori data, dan konfigurasi TLS. Installer meminta password dashboard (minimal 14 karakter) dan NVIDIA API Key. Rahasia disimpan di `/opt/facebook-ai/.env`, tidak di Git.

## Mengganti instalasi yang sudah ada
Jangan hapus `/data/facebook-ai` karena berisi database, profil browser, dan sesi login. Untuk mengganti kode, hentikan service, backup konfigurasi rahasia, lalu update kode di direktori yang sama. Jangan menjalankan service kedua.

## Akses
1. Publish TCP port **8443** di panel Instanbox.
2. Buka `https://IP-VPS:8443`.
3. Sertifikat awal self-signed sehingga browser memberi peringatan. Gunakan domain dan sertifikat TLS valid untuk menghilangkan peringatan.
4. Jangan publikasikan port 8000, 5901, atau 9222.

## Operasional

    systemctl status facebook-ai nginx
    journalctl -u facebook-ai -f
    systemctl restart facebook-ai

Update kode:

    cd /opt/facebook-ai
    git pull --ff-only origin main
    .venv/bin/pip install -r requirements.txt
    systemctl restart facebook-ai

Backup berkala: `/data/facebook-ai` dan file rahasia `/opt/facebook-ai/.env`.

## NVIDIA NIM
- Base URL: `https://integrate.api.nvidia.com/v1`
- Model default: `nvidia/nemotron-3-ultra-550b-a55b`

## Batas keamanan dan Facebook
Login dilakukan manual di panel browser. Jangan membagikan password, OTP, cookie, atau token sesi kepada AI. Aplikasi tidak melakukan bypass CAPTCHA/2FA, scraping tersembunyi, auto-post, auto-message, atau tindakan massal. Semua tindakan akun tetap dikendalikan pengguna dan harus mengikuti aturan Meta.
