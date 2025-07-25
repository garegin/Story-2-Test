import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def ollama_generate_prompt(prompt: str, model: str = "llama3:8b") -> str:
    """
    Generate a response from the Ollama API for a given prompt and model.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json().get("response", "").strip()

def ollama_healthcheck() -> bool:
    """
    Check if the Ollama API is reachable.
    """
    try:
        # Minimal prompt for health check
        payload = {
            "model": "llama3:8b",
            "prompt": "say hello world",
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        return False