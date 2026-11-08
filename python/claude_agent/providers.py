"""OpenAI-compatible and native Anthropic Messages API adapters."""
from __future__ import annotations
import asyncio
import json
from typing import Any
from urllib.parse import urlparse
import httpx

class ProviderError(RuntimeError):
    pass

def chat_url(base_url: str) -> str:
    base=base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"

def is_anthropic(base_url: str) -> bool:
    host=(urlparse(base_url).hostname or "").lower()
    return host == "api.anthropic.com" or host.endswith(".anthropic.com")

def anthropic_url(base_url: str) -> str:
    base=base_url.rstrip("/")
    if base.endswith("/messages"):
        return base
    if base.endswith("/v1"):
        return base + "/messages"
    return base + "/v1/messages"

def _text(value: Any) -> str:
    if isinstance(value,str):
        return value
    if isinstance(value,list):
        return "\n".join(str(x.get("text","")) for x in value if isinstance(x,dict) and x.get("type")=="text")
    return ""

def to_anthropic_messages(messages: list[dict[str,Any]]) -> tuple[str,list[dict[str,Any]]]:
    system_parts=[]
    converted=[]
    pending_results=[]
    def flush_results():
        if pending_results:
            converted.append({"role":"user","content":pending_results.copy()})
            pending_results.clear()
    for msg in messages:
        role=msg.get("role")
        if role=="system":
            system_parts.append(_text(msg.get("content","")))
            continue
        if role=="tool":
            pending_results.append({"type":"tool_result","tool_use_id":str(msg.get("tool_call_id","")),"content":_text(msg.get("content",""))})
            continue
        flush_results()
        if role not in {"user","assistant"}:
            continue
        blocks=[]
        content=_text(msg.get("content",""))
        if content:
            blocks.append({"type":"text","text":content})
        for call in msg.get("tool_calls") or []:
            fn=call.get("function",{})
            try:
                args=json.loads(fn.get("arguments") or "{}")
            except (TypeError,ValueError):
                args={}
            if not isinstance(args,dict):
                args={}
            blocks.append({"type":"tool_use","id":str(call.get("id","")),"name":str(fn.get("name","")),"input":args})
        if blocks:
            converted.append({"role":role,"content":blocks})
    flush_results()
    return "\n\n".join(x for x in system_parts if x),converted

def anthropic_tools(tools: list[dict[str,Any]]) -> list[dict[str,Any]]:
    result=[]
    for item in tools:
        fn=item.get("function",{})
        if not isinstance(fn,dict) or not fn.get("name"):
            continue
        schema=fn.get("parameters")
        if not isinstance(schema,dict) or schema.get("type")!="object":
            schema={"type":"object","properties":{}}
        result.append({"name":fn["name"],"description":str(fn.get("description",""))[:1000],"input_schema":schema})
    return result

def from_anthropic_message(data: dict[str,Any]) -> dict[str,Any]:
    text_parts=[]
    calls=[]
    for index,block in enumerate(data.get("content",[])):
        if not isinstance(block,dict):
            continue
        if block.get("type")=="text":
            text_parts.append(str(block.get("text","")))
        elif block.get("type")=="tool_use":
            calls.append({"id":str(block.get("id") or f"tool_{index}"),"type":"function",
                          "function":{"name":str(block.get("name","")),"arguments":json.dumps(block.get("input") or {})}})
    message={"role":"assistant","content":"\n".join(text_parts)}
    if calls:
        message["tool_calls"]=calls
    return message

async def complete(client: httpx.AsyncClient, provider: dict[str,Any], messages: list[dict[str,Any]], tools: list[dict[str,Any]]) -> dict[str,Any]:
    base=provider["baseUrl"]
    anthropic=is_anthropic(base)
    if anthropic:
        system,conversation=to_anthropic_messages(messages)
        payload={"model":provider["model"],"messages":conversation,"max_tokens":provider.get("maxTokens",4096)}
        if system:
            payload["system"]=system
        if provider.get("temperature") is not None:
            payload["temperature"]=provider.get("temperature",.2)
        native_tools=anthropic_tools(tools)
        if native_tools:
            payload["tools"]=native_tools
        headers={"content-type":"application/json","x-api-key":provider.get("apiKey",""),"anthropic-version":"2023-06-01"}
        url=anthropic_url(base)
    else:
        payload={"model":provider["model"],"messages":messages,"temperature":provider.get("temperature",.2),
                 "max_tokens":provider.get("maxTokens",4096)}
        if tools:
            payload["tools"]=tools
            payload["tool_choice"]="auto"
        headers={"content-type":"application/json"}
        if provider.get("apiKey"):
            headers["authorization"]="Bearer "+provider["apiKey"]
        url=chat_url(base)
    for attempt in range(3):
        try:
            response=await client.post(url,headers=headers,json=payload)
            if response.status_code in {408,429,500,502,503,504} and attempt < 2:
                await asyncio.sleep(.5*(2**attempt))
                continue
            response.raise_for_status()
            data=response.json()
            if anthropic:
                if not isinstance(data.get("content"),list):
                    raise ProviderError("Anthropic returned an invalid message")
                return from_anthropic_message(data)
            if not isinstance(data.get("choices"),list) or not data["choices"]:
                raise ProviderError("Provider returned no choices")
            return data["choices"][0]["message"]
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"Provider HTTP {exc.response.status_code}: {exc.response.text[:300]}") from exc
        except (httpx.TimeoutException,httpx.NetworkError) as exc:
            if attempt == 2:
                raise ProviderError("Provider request failed after 3 attempts: "+type(exc).__name__) from exc
            await asyncio.sleep(.5*(2**attempt))
        except (ValueError,KeyError,TypeError) as exc:
            raise ProviderError("Invalid provider response") from exc
    raise ProviderError("Provider request failed")
