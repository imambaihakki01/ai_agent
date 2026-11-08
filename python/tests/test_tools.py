from pathlib import Path
import pytest
from claude_agent.tools import WorkspaceTools

def test_parent_escape_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        WorkspaceTools(tmp_path).resolve("../secret.txt")

def test_write_and_read_inside_workspace(tmp_path: Path):
    tools = WorkspaceTools(tmp_path)
    tools.write_file("src/demo.txt", "hello")
    assert tools.read_file("src/demo.txt") == "hello"

def test_shell_requires_approval(tmp_path: Path):
    with pytest.raises(PermissionError):
        WorkspaceTools(tmp_path).run_shell("echo unsafe")
