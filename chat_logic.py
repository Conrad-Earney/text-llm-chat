import requests

def generate_reply(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "custom_1", "prompt": prompt, "stream": False}
    )
    return r.json().get("response", "")
