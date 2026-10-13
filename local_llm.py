import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LocalLLMError(RuntimeError):
    pass


def generate_response(prompt, system_prompt=None, temperature=0.5):
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }).encode("utf-8")
    request = Request(
        f"{host}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise LocalLLMError(f"Ollama returned HTTP {error.code}: {detail}") from error
    except (URLError, TimeoutError) as error:
        raise LocalLLMError(
            "Ollama is not responding. Install and start Ollama, then download "
            f"the model with `ollama pull {model}`."
        ) from error
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise LocalLLMError("Ollama returned an invalid response.") from error

    try:
        return result["message"]["content"].strip()
    except (KeyError, TypeError, AttributeError) as error:
        raise LocalLLMError("Ollama returned an empty response.") from error
