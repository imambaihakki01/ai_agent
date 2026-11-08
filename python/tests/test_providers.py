from nexus_agent.providers import chat_url

def test_chat_url_normalization():
    assert chat_url("https://api.example/v1")=="https://api.example/v1/chat/completions"
    assert chat_url("http://localhost:11434")=="http://localhost:11434/v1/chat/completions"
    assert chat_url("https://proxy/v1/chat/completions")=="https://proxy/v1/chat/completions"
