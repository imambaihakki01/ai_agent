from pathlib import Path
def load_project_instructions(workspace:Path)->str:
    parts=[]
    for name in ("CLAUDE.md","AGENTS.md"):
        p=workspace/name
        if p.is_file():
            try: parts.append("## "+name+"\n"+p.read_text(encoding="utf-8")[:10000])
            except OSError: pass
    return "\n\n".join(parts)
def discover_skills(workspace:Path)->list[dict[str,str]]:
    roots=[workspace/".nexus"/"skills",Path.home()/".nexus"/"skills",Path(__file__).resolve().parents[2]/"skills"];found={}
    for root in roots:
        if root.is_dir():
            for p in root.glob("*/SKILL.md"):
                try: found[p.parent.name]={"name":p.parent.name,"content":p.read_text(encoding="utf-8")}
                except OSError: pass
    return list(found.values())
