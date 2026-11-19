from contextlib import asynccontextmanager
import asyncio
from html import escape
from pathlib import Path
import logging

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app import browser as fb_browser
from app.database import connect, initialize_database
from app.nvidia import ask_nvidia
from app.security import csrf_token, is_authenticated, login_allowed, password_matches, record_login_failure, valid_csrf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("facebook-ai")
settings = get_settings()
ROOT = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.app_secret_key in {"CHANGE_ME", "REPLACE_WITH_A_LONG_RANDOM_SECRET"} or len(settings.app_secret_key) < 32:
        raise RuntimeError("APP_SECRET_KEY belum aman. Jalankan installer.")
    if settings.dashboard_password in {"CHANGE_ME", "REPLACE_WITH_A_LONG_UNIQUE_PASSWORD"} or len(settings.dashboard_password) < 14:
        raise RuntimeError("DASHBOARD_PASSWORD belum aman. Jalankan installer.")
    initialize_database()
    yield

app = FastAPI(title="Facebook AI Agent", version="1.0.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key, session_cookie="fbai_session", max_age=settings.session_max_age, same_site="strict", https_only=settings.cookie_secure)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

@app.middleware("http")
async def security_headers_and_csrf(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response

def require_login(request: Request) -> None:
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Silakan login kembali.")


@app.get("/api/browser/status")
async def browser_status(request: Request):
    require_login(request)
    return await asyncio.to_thread(fb_browser.status)

@app.post("/api/browser/open")
async def browser_open(request: Request, url: str = Form("https://www.facebook.com/"), csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    try:
        return await asyncio.to_thread(fb_browser.open_facebook, url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/api/browser/screenshot")
async def browser_screenshot(request: Request):
    require_login(request)
    try:
        return await asyncio.to_thread(fb_browser.screenshot)
    except Exception:
        logger.exception("Browser screenshot failed")
        raise HTTPException(status_code=503, detail="Browser belum siap. Tekan Buka Facebook.")

@app.post("/api/browser/click")
async def browser_click(request: Request, x: int = Form(...), y: int = Form(...), csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    try:
        return await asyncio.to_thread(fb_browser.click, x, y)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/browser/type")
async def browser_type(request: Request, value: str = Form(...), csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    try:
        return await asyncio.to_thread(fb_browser.type_text, value)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/browser/key")
async def browser_key(request: Request, key: str = Form(...), csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    try:
        return await asyncio.to_thread(fb_browser.press_key, key)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/browser/close")
async def browser_close(request: Request, csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    return await asyncio.to_thread(fb_browser.close_browser)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "facebook-ai-agent"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=303)
    with connect() as db:
        rows = db.execute("SELECT role, content, created_at FROM messages ORDER BY id DESC LIMIT 40").fetchall()
    items = "".join(
        f'<article class="message {m["role"]}"><b>{m["role"].title()}</b><p>{escape(m["content"])}</p><small>{escape(m["created_at"])}</small></article>'
        for m in reversed([dict(row) for row in rows])
    )
    html = (ROOT / "templates" / "dashboard.html").read_text(encoding="utf-8")
    html = html.replace("<!--MESSAGES-->", items).replace("__CSRF__", escape(csrf_token(request)))
    return HTMLResponse(html)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse("/", status_code=303)
    html = (ROOT / "templates" / "login.html").read_text(encoding="utf-8")
    return HTMLResponse(html.replace("__CSRF__", escape(csrf_token(request))))

@app.post("/login")
async def login(request: Request, password: str = Form(...), csrf_token: str = Form(...)):
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid. Muat ulang halaman.")
    client_key = request.client.host if request.client else "unknown"
    with connect() as db:
        if not login_allowed(db, client_key):
            raise HTTPException(status_code=429, detail="Terlalu banyak percobaan. Coba lagi setelah 15 menit.")
        if not password_matches(password, settings.dashboard_password):
            record_login_failure(db, client_key)
            raise HTTPException(status_code=401, detail="Password salah.")
        db.execute("DELETE FROM login_attempts WHERE client_key=?", (client_key,))
    request.session.clear()
    request.session["authenticated"] = True
    request.session["csrf_token"] = csrf_token
    return RedirectResponse("/", status_code=303)

@app.post("/logout")
async def logout(request: Request, csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

@app.post("/api/chat")
async def chat(request: Request, prompt: str = Form(...), csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    prompt = prompt.strip()
    if not prompt or len(prompt) > settings.max_prompt_chars:
        raise HTTPException(status_code=400, detail="Pesan kosong atau terlalu panjang.")
    with connect() as db:
        history_rows = db.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT 12").fetchall()
        history = [dict(row) for row in reversed(history_rows)]
    try:
        answer = await ask_nvidia(prompt, history)
    except Exception:
        logger.exception("NVIDIA NIM request failed")
        raise HTTPException(status_code=502, detail="Gagal menghubungi NVIDIA NIM. Periksa API key, kuota, dan koneksi VPS.")
    with connect() as db:
        db.execute("INSERT INTO messages(role, content) VALUES('user', ?)", (prompt,))
        db.execute("INSERT INTO messages(role, content) VALUES('assistant', ?)", (answer,))
    return {"reply": answer}

@app.post("/api/clear")
async def clear_history(request: Request, csrf_token: str = Form(...)):
    require_login(request)
    if not valid_csrf(request, csrf_token):
        raise HTTPException(status_code=403, detail="Token keamanan tidak valid.")
    with connect() as db:
        db.execute("DELETE FROM messages")
    return RedirectResponse("/", status_code=303)
