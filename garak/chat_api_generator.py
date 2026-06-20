"""
Garak generator for RAG chat endpoint: POST /api/v1/chat
"""

import logging
import requests

from garak import _config
from garak.generators.base import Generator
from garak.attempt import Message


class ChatApiGenerator(Generator):
    """
    Generator that sends prompts to the RAG chat API:
    POST /api/v1/chat with JSON:
    {
        "message": "user prompt",
        "thread_id": "optional thread id",
        "use_rag": true,
        "top_k": 6
    }
    Expects response with "answer" field.
    """

    generator_family_name = "ChatAPI"
    supports_multiple_generations = False

    DEFAULT_PARAMS = Generator.DEFAULT_PARAMS | {
        "base_url": "http://10.40.240.103:8000",
        "api_endpoint": "/api/v1/chat",
        "request_timeout": 60,
        "thread_id": None,          # статический thread_id, если нужен постоянный диалог
        "use_rag": True,
        "top_k": 6,
    }

    def __init__(self, name="ChatApiGenerator", config_root=_config):
        super().__init__(name=name, config_root=config_root)

        self.log = logging.getLogger(__name__)
        self.base_url = self.base_url.rstrip("/")
        self.api_url = f"{self.base_url}{self.api_endpoint}"
        self.headers = {"Content-Type": "application/json"}

    def _call_model(self, prompt, generations_this_call: int = 1):
        prompt_text = self._prompt_to_text(prompt)

        # Формируем тело запроса
        payload = {"message": prompt_text}
        if self.thread_id is not None:
            payload["thread_id"] = self.thread_id
        if self.use_rag is not None:
            payload["use_rag"] = self.use_rag
        if self.top_k is not None:
            payload["top_k"] = self.top_k

        self.log.debug(f"Sending to {self.api_url}: {prompt_text[:100]}...")

        try:
            resp = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=self.request_timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("answer", "")
            self.log.debug(f"Answer received (first 100 chars): {answer[:100]}")
        except Exception as e:
            self.log.error(f"API request failed: {e}")
            answer = f"[ERROR: {e}]"

        return [Message(text=answer)]

    def _prompt_to_text(self, prompt) -> str:
        # Универсальное извлечение текста из форматов Garak
        if hasattr(prompt, "turns"):          # garak.attempt.Conversation
            for turn in reversed(prompt.turns):
                if turn.role == "user":
                    return turn.content.text or ""
        if hasattr(prompt, "text"):           # garak.attempt.Message
            return prompt.text or ""
        return str(prompt)


DEFAULT_CLASS = "ChatApiGenerator"