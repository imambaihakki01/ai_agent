"""Minimal MCP stdio client for explicitly configured local servers."""
from __future__ import annotations
import asyncio, json, os, re
from typing import Any

class MCPError(RuntimeError):
    pass

def configured_servers() -> dict[str,dict[str,Any]]:
    raw=os.getenv("NEXUS_MCP_SERVERS","{}")
    try:
        value=json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MCPError("NEXUS_MCP_SERVERS must be valid JSON") from exc
    if not isinstance(value,dict):
        raise MCPError("NEXUS_MCP_SERVERS must be an object")
    result={}
    for name,spec in value.items():
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}",name) or not isinstance(spec,dict):
            continue
        command=spec.get("command")
        args=spec.get("args",[])
        if isinstance(command,str) and command and isinstance(args,list) and all(isinstance(x,str) for x in args):
            result[name]={"command":command,"args":args,"env":spec.get("env",{}) if isinstance(spec.get("env",{}),dict) else {}}
    return result

async def _rpc(proc: asyncio.subprocess.Process, request_id: int, method: str, params: dict[str,Any] | None = None) -> dict[str,Any]:
    if not proc.stdin or not proc.stdout:
        raise MCPError("MCP process streams unavailable")
    packet={"jsonrpc":"2.0","id":request_id,"method":method,"params":params or {}}
    proc.stdin.write((json.dumps(packet)+"\n").encode())
    await proc.stdin.drain()
    async def read():
        while True:
            line=await proc.stdout.readline()
            if not line:
                raise MCPError("MCP server closed stdout")
            try:
                data=json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("id")==request_id:
                if "error" in data:
                    raise MCPError(str(data["error"])[:500])
                return data.get("result",{})
    return await asyncio.wait_for(read(),timeout=15)

async def _start(spec: dict[str,Any]):
    env=os.environ.copy()
    env.update({str(k):str(v) for k,v in spec.get("env",{}).items()})
    proc=await asyncio.create_subprocess_exec(spec["command"],*spec["args"],stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL,env=env)
    await _rpc(proc,1,"initialize",{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"nexus-ai-cli","version":"0.3.0"}})
    if proc.stdin:
        proc.stdin.write((json.dumps({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})+"\n").encode())
        await proc.stdin.drain()
    return proc

async def list_tools() -> list[dict[str,Any]]:
    tools=[]
    for server,spec in configured_servers().items():
        proc=None
        try:
            proc=await _start(spec)
            result=await _rpc(proc,2,"tools/list")
            for item in result.get("tools",[]):
                name=item.get("name")
                if isinstance(name,str) and re.fullmatch(r"[a-zA-Z0-9_-]{1,80}",name):
                    tools.append({"type":"function","function":{"name":f"mcp__{server}__{name}",
                        "description":str(item.get("description","MCP tool"))[:1000],
                        "parameters":item.get("inputSchema") or {"type":"object","properties":{}}}})
        except Exception:
            continue
        finally:
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()
    return tools[:40]

async def call_tool(full_name: str, arguments: dict[str,Any]) -> str:
    parts=full_name.split("__",2)
    if len(parts)!=3 or parts[0]!="mcp":
        raise MCPError("Invalid MCP tool name")
    servers=configured_servers()
    if parts[1] not in servers:
        raise MCPError("MCP server is not configured")
    proc=None
    try:
        proc=await _start(servers[parts[1]])
        result=await _rpc(proc,2,"tools/call",{"name":parts[2],"arguments":arguments})
        content=result.get("content",[])
        text="\n".join(str(x.get("text","")) for x in content if isinstance(x,dict))
        if result.get("isError"):
            return "MCP tool error: "+text[:5000]
        return text[:20000] or json.dumps(result)[:20000]
    except Exception as exc:
        return "MCP error: "+str(exc)[:500]
    finally:
        if proc and proc.returncode is None:
            proc.kill()
            await proc.wait()
