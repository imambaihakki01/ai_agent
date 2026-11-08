from claude_agent.providers import (
    chat_url, anthropic_url, is_anthropic, to_anthropic_messages,
    anthropic_tools, from_anthropic_message,
)

def test_chat_url_normalization():
    assert chat_url("https://api.example/v1")=="https://api.example/v1/chat/completions"
    assert chat_url("http://localhost:11434")=="http://localhost:11434/v1/chat/completions"
    assert chat_url("https://proxy/v1/chat/completions")=="https://proxy/v1/chat/completions"

def test_native_anthropic_endpoint_detection():
    assert is_anthropic("https://api.anthropic.com")
    assert not is_anthropic("https://openrouter.ai/api/v1")
    assert anthropic_url("https://api.anthropic.com/v1")=="https://api.anthropic.com/v1/messages"

def test_openai_tool_messages_convert_to_anthropic_blocks():
    system, messages=to_anthropic_messages([
        {"role":"system","content":"Be concise"},
        {"role":"user","content":"List files"},
        {"role":"assistant","content":"","tool_calls":[{"id":"c1","function":{"name":"list_files","arguments":"{}"}}]},
        {"role":"tool","tool_call_id":"c1","content":"[a.py]"},
    ])
    assert system=="Be concise"
    assert messages[1]["content"][0]["type"]=="tool_use"
    assert messages[2]["content"][0]["type"]=="tool_result"

def test_anthropic_tools_and_response_normalization():
    tools=anthropic_tools([{"type":"function","function":{"name":"read_file","description":"Read","parameters":{"type":"object","properties":{"path":{"type":"string"}}}}}])
    assert tools[0]["input_schema"]["type"]=="object"
    message=from_anthropic_message({"content":[{"type":"text","text":"Done"},{"type":"tool_use","id":"t1","name":"read_file","input":{"path":"a.py"}}]})
    assert message["content"]=="Done"
    assert message["tool_calls"][0]["function"]["name"]=="read_file"
