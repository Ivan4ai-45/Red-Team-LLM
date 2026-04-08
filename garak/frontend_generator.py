from garak.generators import Generator
import requests
import json

class FrontendGenerator(Generator):
    def __init__(self, name="FrontendGenerator"):
        self.name = name
        self.base_url = "http://10.8.1.18:3000/ollama/api/chat"
        self.headers = {
            "Content-Type": "text/event-stream",
            "Authorization": "Bearer",  # Optional
        }

    def generate(self, prompt, **kwargs):
        # Формируем запрос: отправляем только один user-запрос (без истории)
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": "redteam-omega-secure:latest",
            "messages": messages,
            "guardrailsEnabled": True,
            "options": {}
        }
        response = requests.post(self.base_url, headers=self.headers, json=payload, stream=True)
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        full_response += chunk["message"]["content"]
                    if chunk.get("done"):
                        break
                except:
                    continue
        return full_response