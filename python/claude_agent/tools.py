from pathlib import Path
import subprocess
import json

class WorkspaceTools:
    """Workspace-confined file and search tools plus opt-in shell execution."""
    IGNORED = {".git", "node_modules", ".venv", "__pycache__", ".next", "dist"}

    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()

    def resolve(self, relative: str) -> Path:
        target = (self.workspace / relative).resolve()
        if target != self.workspace and self.workspace not in target.parents:
            raise ValueError("Path escapes workspace")
        return target

    def read_file(self, path: str, limit: int = 200000) -> str:
        target = self.resolve(path)
        if not target.is_file():
            raise FileNotFoundError(path)
        return target.read_text(encoding="utf-8")[:limit]

    def write_file(self, path: str, content: str) -> None:
        target = self.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def list_files(self, path: str = ".") -> list[str]:
        root = self.resolve(path)
        found = []
        for item in root.rglob("*"):
            if any(part in self.IGNORED or part.startswith(".") for part in item.relative_to(root).parts):
                continue
            if item.is_file():
                found.append(str(item.relative_to(self.workspace)))
            if len(found) >= 500:
                break
        return found

    def search_files(self, query: str, path: str = ".", limit: int = 50) -> list[dict[str, str]]:
        if not query:
            return []
        root = self.resolve(path)
        matches = []
        for item in root.rglob("*"):
            if any(part in self.IGNORED or part.startswith(".") for part in item.relative_to(root).parts):
                continue
            if not item.is_file() or item.stat().st_size > 500_000:
                continue
            try:
                for number, line in enumerate(item.read_text(encoding="utf-8").splitlines(), 1):
                    if query.casefold() in line.casefold():
                        matches.append({"path": str(item.relative_to(self.workspace)), "line": str(number), "text": line[:500]})
                        if len(matches) >= limit:
                            return matches
            except (OSError, UnicodeDecodeError):
                continue
        return matches

    def git_status(self) -> str:
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=self.workspace, text=True, capture_output=True, timeout=10, check=False,
        )
        if result.returncode:
            return (result.stderr or "Not a Git repository").strip()[:4000]
        return (result.stdout or "Working tree clean").strip()[:4000]

    def git_diff(self, staged: bool = False) -> str:
        command = ["git", "diff", "--no-ext-diff", "--"]
        if staged:
            command = ["git", "diff", "--cached", "--no-ext-diff", "--"]
        result = subprocess.run(
            command, cwd=self.workspace, text=True, capture_output=True,
            timeout=15, check=False,
        )
        if result.returncode:
            raise RuntimeError((result.stderr or "git diff failed")[:1000])
        return result.stdout[:30000] or "No changes."

    def run_shell(self, command: str, approved: bool = False, timeout: int = 30) -> str:
        if not approved:
            raise PermissionError("Shell execution requires explicit approval")
        result = subprocess.run(command, cwd=self.workspace, shell=True, text=True,
                                capture_output=True, timeout=min(timeout, 60), check=False)
        return (result.stdout + result.stderr)[:20000]
