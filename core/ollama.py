"""
A small example script for quick testing of an Ollama server.
Not used by the main app directly; prefer core/ollama_engine for integration.
"""
if __name__ == "__main__":
    import requests
    url = "http://localhost:11434/v1/completions"
    data = {
        "model": "gemma3:4b",
        "prompt": "Write a short poem about AI ",
        "max_tokens": 150
    }
    r = requests.post(url, json=data)
    print(r.json())
