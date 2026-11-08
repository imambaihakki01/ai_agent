from pathlib import Path
import subprocess
class WorkspaceTools:
    """Workspace-confined file tools and explicitly approved shell."""
    def __init__(self,workspace:Path): self.workspace=workspace.resolve()
    def resolve(self,relative:str)->Path:
        target=(self.workspace/relative).resolve()
        if target!=self.workspace and self.workspace not in target.parents: raise ValueError("Path escapes workspace")
        return target
    def read_file(self,path:str,limit:int=200000)->str:
        p=self.resolve(path)
        if not p.is_file(): raise FileNotFoundError(path)
        return p.read_text(encoding="utf-8")[:limit]
    def write_file(self,path:str,content:str)->None:
        p=self.resolve(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding="utf-8")
    def list_files(self,path:str=".")->list[str]:
        return [str(p.relative_to(self.workspace)) for p in self.resolve(path).rglob("*") if p.is_file()][:500]
    def run_shell(self,command:str,approved:bool=False,timeout:int=30)->str:
        if not approved: raise PermissionError("Shell execution requires explicit approval")
        r=subprocess.run(command,cwd=self.workspace,shell=True,text=True,capture_output=True,timeout=min(timeout,60),check=False)
        return (r.stdout+r.stderr)[:20000]
