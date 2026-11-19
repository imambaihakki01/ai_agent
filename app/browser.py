import base64
import threading
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

_lock = threading.RLock()
_playwright = None
_context = None
_page = None
_allowed_hosts = {"facebook.com", "www.facebook.com", "m.facebook.com", "web.facebook.com"}

def _ensure_page():
    global _playwright, _context, _page
    if _page is not None and not _page.is_closed():
        return _page
    from app.config import get_settings
    settings = get_settings()
    profile = settings.data_dir / "browser-profile"
    profile.mkdir(parents=True, exist_ok=True, mode=0o700)
    executable = "/usr/bin/chromium"
    if not Path(executable).exists():
        executable = None
    _playwright = sync_playwright().start()
    _context = _playwright.chromium.launch_persistent_context(
        user_data_dir=str(profile),
        executable_path=executable,
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        viewport={"width": 1365, "height": 900},
        locale="id-ID",
    )
    _page = _context.pages[0] if _context.pages else _context.new_page()
    _page.set_default_timeout(10000)
    return _page

def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in _allowed_hosts:
        raise ValueError("Browser hanya boleh membuka https://facebook.com dan subdomain resminya.")
    return url

def status():
    with _lock:
        if _page is None or _page.is_closed():
            return {"running": False, "url": "", "title": ""}
        return {"running": True, "url": _page.url, "title": _page.title()}

def open_facebook(url: str = "https://www.facebook.com/"):
    with _lock:
        page = _ensure_page()
        page.goto(_validate_url(url), wait_until="domcontentloaded", timeout=45000)
        return {"running": True, "url": page.url, "title": page.title()}

def screenshot():
    with _lock:
        page = _ensure_page()
        image = page.screenshot(type="jpeg", quality=65, full_page=False)
        return {"running": True, "url": page.url, "title": page.title(),
                "image": "data:image/jpeg;base64," + base64.b64encode(image).decode("ascii"),
                "width": 1365, "height": 900}

def click(x: int, y: int):
    if not (0 <= x <= 1365 and 0 <= y <= 900):
        raise ValueError("Koordinat klik di luar area browser.")
    with _lock:
        page = _ensure_page()
        if page.url == "about:blank":
            raise ValueError("Buka Facebook terlebih dahulu.")
        page.mouse.click(x, y)
        return {"ok": True}

def type_text(value: str):
    if not value or len(value) > 2000:
        raise ValueError("Teks harus berisi 1-2000 karakter.")
    with _lock:
        page = _ensure_page()
        if page.url == "about:blank":
            raise ValueError("Buka Facebook terlebih dahulu.")
        page.keyboard.insert_text(value)
        return {"ok": True}

def press_key(key: str):
    allowed = {"Enter", "Escape", "Tab", "Backspace", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"}
    if key not in allowed:
        raise ValueError("Tombol keyboard tidak diizinkan.")
    with _lock:
        page = _ensure_page()
        if page.url == "about:blank":
            raise ValueError("Buka Facebook terlebih dahulu.")
        page.keyboard.press(key)
        return {"ok": True}

def close_browser():
    global _playwright, _context, _page
    with _lock:
        if _context is not None:
            _context.close()
        if _playwright is not None:
            _playwright.stop()
        _context = _page = _playwright = None
        return {"running": False}
