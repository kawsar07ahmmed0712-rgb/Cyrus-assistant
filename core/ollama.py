import requests

url = "http://localhost:11434/v1/completions"

data = {
    "model": "gemma3:4b",
    "prompt": "Write a short poem about AI ",
    "max_tokens": 150
}

response = requests.post(url, json=data)
result = response.json()

# এখন 'choices' list থেকে 'text' নাও
print(result["choices"][0]["text"])
