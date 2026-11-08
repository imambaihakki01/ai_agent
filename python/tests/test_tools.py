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

def test_symlink_to_external_file_is_excluded_from_listing_and_search(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "private.txt"
    outside.write_text("sensitive-workspace-marker", encoding="utf-8")
    link = workspace / "linked-secret.txt"
    try:
        link.symlink_to(outside)
    except (NotImplementedError, OSError):
        pytest.skip("Symlinks are unavailable on this platform")

    tools = WorkspaceTools(workspace)
    assert "linked-secret.txt" not in tools.list_files()
    assert tools.search_files("sensitive-workspace-marker") == []

    with pytest.raises(ValueError, match="Path escapes workspace"):
        tools.read_file("linked-secret.txt")

def test_shell_requires_approval(tmp_path: Path):
    with pytest.raises(PermissionError):
        WorkspaceTools(tmp_path).run_shell("echo unsafe")
