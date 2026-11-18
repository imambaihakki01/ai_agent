from app.security import password_matches


def test_password_matches():
    assert password_matches("strong-secret", "strong-secret")
    assert not password_matches("wrong", "strong-secret")
    assert not password_matches("CHANGE_ME", "CHANGE_ME")
