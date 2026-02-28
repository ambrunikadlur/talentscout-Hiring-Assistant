import requests
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi"   # lightweight model
def generate_llm_response(messages):
    try:
        prompt = ""
        for msg in messages:
            prompt += f"{msg['role'].upper()}: {msg['content']}\n\n"
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 200   # limits output → faster
            }
        }
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180
        )
        response.raise_for_status()
        return response.json().get("response", "No response generated.")
    except requests.exceptions.Timeout:
        return "⚠ Model timed out. Try shorter input."
    except requests.exceptions.RequestException as e:
        return f"⚠ API Error: {str(e)}"