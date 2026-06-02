"""
Garak generator for custom agent API (POST /api/agent/chat)
"""
import logging
import requests

from garak import _config
from garak.generators.base import Generator
from garak.attempt import Message


class AgentApiGenerator(Generator):
    """
    Generator that sends prompts to a simple JSON API:
    POST /api/agent/chat with {"message": "text"}
    Expects {"answer": "response text", "contexts": [...]}
    """

    generator_family_name = "AgentAPI"
    supports_multiple_generations = False

    DEFAULT_PARAMS = Generator.DEFAULT_PARAMS | {
        "base_url": "http://10.40.240.103:8000",
        "api_endpoint": "/api/agent/chat",
        "request_timeout": 60,
    }

    def __init__(self, name="AgentApiGenerator", config_root=_config):
        super().__init__(name=name, config_root=config_root)

        self.log = logging.getLogger(__name__)
        self.base_url = self.base_url.rstrip("/")
        self.api_url = f"{self.base_url}{self.api_endpoint}"
        self.headers = {"Content-Type": "application/json"}

    def _call_model(self, prompt, generations_this_call: int = 1):
        # Garak может передавать prompt как Conversation, Message или строку.
        # Извлекаем чистый текст.
        prompt_text = self._prompt_to_text(prompt)

        self.log.debug(f"Sending prompt to {self.api_url}: {prompt_text[:100]}...")

        try:
            resp = requests.post(
                self.api_url,
                json={"message": prompt_text},
                headers=self.headers,
                timeout=self.request_timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("answer", "")
            self.log.debug(f"Received answer: {answer[:100]}...")
        except Exception as e:
            self.log.error(f"API request failed: {e}")
            answer = f"[ERROR: {e}]"

        return [Message(text=answer)]

    def _prompt_to_text(self, prompt) -> str:
        # Поддержка разных форматов Garak
        if hasattr(prompt, 'turns'):          # Conversation
            for turn in reversed(prompt.turns):
                if turn.role == "user":
                    return turn.content.text or ""
        if hasattr(prompt, 'text'):           # Message
            return prompt.text or ""
        return str(prompt)


DEFAULT_CLASS = "AgentApiGenerator"