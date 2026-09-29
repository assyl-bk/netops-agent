import time
import httpx
from dataclasses import dataclass
from app.core.config import settings

BASE = "https://generativelanguage.googleapis.com/v1beta/models"


@dataclass
class ToolCall:
    name: str
    args: dict


@dataclass
class LLMResponse:
    text: str
    tool_calls: list[ToolCall]
    raw_content: dict  # the model's message, appended to history UNCHANGED


def user_msg(text: str) -> dict:
    return {"role": "user", "parts": [{"text": text}]}


def tool_result_msg(name: str, result: dict) -> dict:
    return {"role": "user",
            "parts": [{"functionResponse": {"name": name, "response": result}}]}


def chat(contents: list[dict], tools: list[dict] | None = None,
         system: str | None = None, retries: int = 3) -> LLMResponse:
    body: dict = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if tools:
        body["tools"] = [{"functionDeclarations": tools}]

    url = f"{BASE}/{settings.llm_model}:generateContent"
    headers = {"x-goog-api-key": settings.llm_api_key}

    for attempt in range(retries):
        r = httpx.post(url, headers=headers, json=body, timeout=60)
        if r.status_code in (429, 503) and attempt < retries - 1:
            time.sleep(2 ** attempt * 5)   # simple backoff: 5s, 10s
            continue
        r.raise_for_status()
        break

    content = r.json()["candidates"][0]["content"]
    parts = content.get("parts", [])
    text = "".join(p["text"] for p in parts if "text" in p and not p.get("thought"))
    calls = [ToolCall(p["functionCall"]["name"], p["functionCall"].get("args", {}))
             for p in parts if "functionCall" in p]
    return LLMResponse(text, calls, content)