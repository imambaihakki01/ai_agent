import sqlite3
from app.security import password_matches, login_allowed, record_login_failure

def test_password_matches():
    assert password_matches("strong-secret-123", "strong-secret-123")
    assert not password_matches("wrong", "strong-secret-123")
    assert not password_matches("CHANGE_ME", "CHANGE_ME")

def test_login_attempt_limit():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE login_attempts(client_key TEXT PRIMARY KEY, window_start INTEGER, attempts INTEGER)")
    assert login_allowed(db, "127.0.0.1")
    for _ in range(8):
        record_login_failure(db, "127.0.0.1")
    assert not login_allowed(db, "127.0.0.1")
    db.close()
