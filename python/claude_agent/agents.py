"""Bounded advisory sub-agents. Delegates cannot access workspace tools or spawn agents."""
from __future__ import annotations
from typing import Any
import httpx
from .providers import complete

ROLES={
 "planner":"Break the request into ordered, verifiable implementation steps. Identify dependencies and risks.",
 "reviewer":"Review the proposed approach for correctness, edge cases, security and maintainability. Be critical.",
 "researcher":"Analyze the technical question and compare viable implementation approaches. Distinguish facts from assumptions.",
 "tester":"Design focused automated tests, failure cases and verification commands for the task."
}

async def delegate(provider: dict[str,Any], role: str, task: str) -> str:
    if role not in ROLES:
        return "Unknown sub-agent role. Choose planner, reviewer, researcher or tester."
    prompt=("You are a bounded Claude advisory sub-agent. You cannot execute tools, modify files, access credentials, or delegate further. "
            "Return concise, actionable analysis and state assumptions.\n\nRole: "+ROLES[role])
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60,connect=10)) as client:
            message=await complete(client,provider,[{"role":"system","content":prompt},{"role":"user","content":task[:12000]}],[])
        content=message.get("content","")
        if isinstance(content,list):
            content="\n".join(str(x.get("text","")) for x in content if isinstance(x,dict))
        return str(content)[:8000] or "Sub-agent returned an empty result."
    except Exception as exc:
        return "Sub-agent failed: "+type(exc).__name__
