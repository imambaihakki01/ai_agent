"""Provider request normalization and bounded retry handling."""
from __future__ import annotations
import asyncio
from typing import Any
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

async def complete(client: httpx.AsyncClient, provider: dict[str,Any], messages: list[dict[str,Any]], tools: list[dict[str,Any]]) -> dict[str,Any]:
    headers={"content-type":"application/json"}
    if provider.get("apiKey"):
        headers["authorization"]="Bearer "+provider["apiKey"]
    payload={"model":provider["model"],"messages":messages,"temperature":provider.get("temperature",.2),
             "max_tokens":provider.get("maxTokens",4096)}
    if tools:
        payload["tools"]=tools
        payload["tool_choice"]="auto"
    for attempt in range(3):
        try:
            response=await client.post(chat_url(provider["baseUrl"]),headers=headers,json=payload)
            if response.status_code in {408,429,500,502,503,504} and attempt < 2:
                await asyncio.sleep(.5*(2**attempt))
                continue
            response.raise_for_status()
            data=response.json()
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
