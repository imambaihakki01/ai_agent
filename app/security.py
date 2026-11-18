import hmac

from fastapi import Request


def password_matches(candidate: str, expected: str) -> bool:
    if not expected or expected == "CHANGE_ME":
        return False
    return hmac.compare_digest(candidate.encode(), expected.encode())


def is_authenticated(request: Request) -> bool:
    return request.session.get("authenticated") is True
