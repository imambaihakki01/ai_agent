import hmac
import secrets
import time
from fastapi import Request

def password_matches(candidate: str, expected: str) -> bool:
    if not expected or expected in {"CHANGE_ME", "REPLACE_WITH_A_LONG_UNIQUE_PASSWORD"}:
        return False
    return hmac.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8"))

def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated") is True

def csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not isinstance(token, str) or len(token) < 32:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token

def valid_csrf(request: Request, candidate: str) -> bool:
    expected = request.session.get("csrf_token", "")
    return bool(expected and candidate and hmac.compare_digest(str(expected), candidate))

def login_allowed(db, client_key: str) -> bool:
    row = db.execute("SELECT window_start, attempts FROM login_attempts WHERE client_key=?", (client_key,)).fetchone()
    now = int(time.time())
    if row is None:
        return True
    if now - row["window_start"] >= 900:
        db.execute("DELETE FROM login_attempts WHERE client_key=?", (client_key,))
        return True
    return row["attempts"] < 8

def record_login_failure(db, client_key: str) -> None:
    now = int(time.time())
    db.execute("""
        INSERT INTO login_attempts(client_key, window_start, attempts) VALUES(?,?,1)
        ON CONFLICT(client_key) DO UPDATE SET
          attempts=CASE WHEN ? - window_start >= 900 THEN 1 ELSE attempts + 1 END,
          window_start=CASE WHEN ? - window_start >= 900 THEN ? ELSE window_start END
    """, (client_key, now, now, now, now))
