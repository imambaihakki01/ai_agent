from contextlib import asynccontextmanager
from html import escape
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import connect, initialize_database
from app.nvidia import ask_nvidia
from app.security import is_authenticated, password_matches

settings = get_settings()
ROOT = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Facebook AI Agent", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.app_secret_key,
    session_cookie="fbai_session",
    max_age=settings.session_max_age,
    same_site="strict",
    https_only=settings.cookie_secure,
)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


def require_login(request: Request) -> None:
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Silakan login kembali.")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "facebook-ai-agent"}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=303)
    with connect() as db:
        rows = db.execute(
            "SELECT role, content, created_at FROM messages ORDER BY id DESC LIMIT 30"
        ).fetchall()
    messages = list(reversed([dict(row) for row in rows]))
    items = "".join(
        f'<article class="message {m["role"]}"><b>{m["role"].title()}</b><p>{escape(m["content"])}</p></article>'
        for m in messages
    )
    html = (ROOT / "templates" / "dashboard.html").read_text(encoding="utf-8")
    return HTMLResponse(html.replace("<!--MESSAGES-->", items))


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse((ROOT / "templates" / "login.html").read_text(encoding="utf-8"))


@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if not password_matches(password, settings.dashboard_password):
        raise HTTPException(status_code=401, detail="Password salah.")
    request.session.clear()
    request.session["authenticated"] = True
    return RedirectResponse("/", status_code=303)


@app.post("/logout")
async def logout(request: Request):
    require_login(request)
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.post("/api/chat")
async def chat(request: Request, prompt: str = Form(...)):
    require_login(request)
    prompt = prompt.strip()
    if not prompt or len(prompt) > 8000:
        raise HTTPException(status_code=400, detail="Pesan kosong atau terlalu panjang.")
    with connect() as db:
        history_rows = db.execute(
            "SELECT role, content FROM messages ORDER BY id DESC LIMIT 12"
        ).fetchall()
        history = [dict(row) for row in reversed(history_rows)]
        db.execute("INSERT INTO messages(role, content) VALUES('user', ?)", (prompt,))
    try:
        answer = await ask_nvidia(prompt, history)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gagal menghubungi NVIDIA NIM: {exc}") from exc
    with connect() as db:
        db.execute("INSERT INTO messages(role, content) VALUES('assistant', ?)", (answer,))
    return {"reply": answer}
