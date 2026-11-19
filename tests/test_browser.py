import pytest
from app.browser import _validate_url

def test_facebook_https_hosts_allowed():
    assert _validate_url("https://www.facebook.com/") == "https://www.facebook.com/"
    assert _validate_url("https://m.facebook.com/") == "https://m.facebook.com/"

@pytest.mark.parametrize("url", [
    "http://www.facebook.com/",
    "https://facebook.com.evil.example/",
    "https://evil.example/",
    "file:///etc/passwd",
])
def test_non_facebook_urls_rejected(url):
    with pytest.raises(ValueError):
        _validate_url(url)
