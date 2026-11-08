import json
import pytest
from claude_agent.mcp import configured_servers, MCPError

def test_mcp_server_configuration(monkeypatch):
    monkeypatch.setenv("CLAUDE_MCP_SERVERS", json.dumps({
        "local_fs": {"command":"python","args":["-m","fake_server"],"env":{"MODE":"test"}},
        "bad name": {"command":"ignored","args":[]},
        "invalid": {"command":None,"args":[]}
    }))
    servers=configured_servers()
    assert list(servers)==["local_fs"]
    assert servers["local_fs"]["args"]==["-m","fake_server"]

def test_invalid_mcp_configuration(monkeypatch):
    monkeypatch.setenv("CLAUDE_MCP_SERVERS","{not json")
    with pytest.raises(MCPError):
        configured_servers()
