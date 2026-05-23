import os
import time
import uuid
import logging
import requests

from typing import Optional, Dict, Any

from garak import _config
from garak.generators.base import Generator
from garak.attempt import Message, Conversation, Turn


class FrontendChainGenerator(Generator):
    """Garak generator для Open WebUI frontend-chain:
    1. POST /api/v1/chats/new
    2. POST /api/chat/completions
    3. GET /api/v1/chats/{chat_id}
    """

    generator_family_name = "FrontendChain"
    supports_multiple_generations = False

    DEFAULT_PARAMS = Generator.DEFAULT_PARAMS | {
        "base_url": "http://10.40.240.103:3030",
        "model": "llama3.2:1b",
        "request_timeout": 120,
        "poll_interval": 1.0,
    }

    def __init__(self, name="FrontendChainGenerator", config_root=_config):
        super().__init__(name=name, config_root=config_root)

        self.log = logging.getLogger(__name__)
        self.base_url = self.base_url.rstrip("/")

        self.token = os.getenv("GARAK_BEARER_TOKEN")
        if not self.token:
            self.log.warning("GARAK_BEARER_TOKEN не задан — запросы могут вернуть 401")

        self.headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Cookie": f"token={self.token}" if self.token else "",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Garak-SecurityScanner/1.0",
        }

    def _create_chat(self, prompt: str):
        user_msg_id = str(uuid.uuid4())
        assistant_msg_id = str(uuid.uuid4())
        timestamp = int(time.time())

        user_msg = {
            "id": user_msg_id,
            "role": "user",
            "content": prompt,
            "timestamp": timestamp,
            "models": [self.model],
            "childrenIds": [assistant_msg_id],
        }

        assistant_msg = {
            "id": assistant_msg_id,
            "role": "assistant",
            "content": "",
            "parentId": user_msg_id,
            "childrenIds": [],
            "model": self.model,
            "modelName": self.model,
            "modelIdx": 0,
            "done": False,
            "timestamp": timestamp + 1,
        }

        payload = {
            "chat": {
                "title": "garak-test",
                "models": [self.model],
                "messages": [user_msg, assistant_msg],
                "history": {
                    "currentId": assistant_msg_id,
                    "messages": {
                        user_msg_id: user_msg,
                        assistant_msg_id: assistant_msg,
                    },
                },
                "params": {},
                "files": [],
                "tags": [],
            }
        }

        resp = requests.post(
            f"{self.base_url}/api/v1/chats/new",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        resp.raise_for_status()
        data = resp.json()

        chat_id = data.get("id")
        if not chat_id:
            raise RuntimeError(f"No chat id in /api/v1/chats/new response: {data}")

        return chat_id, user_msg_id, assistant_msg_id

    def _start_completion(self, prompt: str, chat_id: str, assistant_msg_id: str):
        session_id = str(uuid.uuid4())

        payload = {
            "model": self.model,
            "stream": False,
            "chat_id": chat_id,
            "id": assistant_msg_id,
            "session_id": session_id,
            "parent_id": None,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "params": {},
            "files": [],
            "tool_servers": [],
            "features": {
                "voice": False,
                "image_generation": False,
                "code_interpreter": False,
                "web_search": False,
            },
            "background_tasks": {
                "title_generation": False,
                "tags_generation": False,
                "follow_up_generation": False,
            },
        }

        resp = requests.post(
            f"{self.base_url}/api/chat/completions",
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        resp.raise_for_status()
        data = resp.json()

        if not data.get("status"):
            self.log.warning(f"Completion returned unexpected response: {data}")

        return data

    def _extract_assistant_answer(
        self,
        data: Dict[str, Any],
        assistant_msg_id: str,
    ) -> Optional[str]:
        messages = data.get("chat", {}).get("history", {}).get("messages", {})

        assistant_msg = messages.get(assistant_msg_id)
        if not assistant_msg:
            return None

        if assistant_msg.get("done") is not True:
            return None

        content = assistant_msg.get("content", "")
        if content:
            return content

        outputs = assistant_msg.get("output", [])
        for out in outputs:
            if out.get("type") == "message" and out.get("content"):
                for c in out["content"]:
                    if c.get("type") == "output_text":
                        text = c.get("text", "")
                        if text:
                            return text

        return None

    def _wait_for_completion(self, chat_id: str, assistant_msg_id: str) -> str:
        start_time = time.time()

        while time.time() - start_time < self.request_timeout:
            try:
                resp = requests.get(
                    f"{self.base_url}/api/v1/chats/{chat_id}",
                    headers=self.headers,
                    timeout=10,
                )

                if resp.status_code != 200:
                    self.log.debug(
                        f"GET /api/v1/chats/{chat_id} returned "
                        f"{resp.status_code}: {resp.text[:300]}"
                    )
                    time.sleep(self.poll_interval)
                    continue

                data = resp.json()
                answer = self._extract_assistant_answer(data, assistant_msg_id)

                if answer:
                    return answer

                time.sleep(self.poll_interval)

            except Exception as e:
                self.log.debug(f"Ошибка при опросе чата {chat_id}: {e}")
                time.sleep(self.poll_interval)

        self.log.error(
            f"Таймаут {self.request_timeout} сек при ожидании ответа "
            f"для chat_id={chat_id}, assistant_msg_id={assistant_msg_id}"
        )
        return "[ERROR: Timeout waiting for model response]"

    def _frontend_request(self, prompt: str) -> str:
        try:
            chat_id, user_msg_id, assistant_msg_id = self._create_chat(prompt)

            self.log.debug(
                f"Chat created: chat_id={chat_id}, "
                f"user_msg_id={user_msg_id}, assistant_msg_id={assistant_msg_id}"
            )

            completion_resp = self._start_completion(
                prompt=prompt,
                chat_id=chat_id,
                assistant_msg_id=assistant_msg_id,
            )

            self.log.debug(f"Completion started: {completion_resp}")

            return self._wait_for_completion(
                chat_id=chat_id,
                assistant_msg_id=assistant_msg_id,
            )

        except requests.exceptions.RequestException as e:
            self.log.error(f"HTTP error while calling Open WebUI: {e}")
            return f"[ERROR: {e}]"

        except Exception as e:
            self.log.error(f"Frontend chain error: {e}")
            return f"[ERROR: {e}]"

    def _prompt_to_text(self, prompt) -> str:
        if isinstance(prompt, Conversation):
            try:
                last_user_message = prompt.last_message(role="user")
                return last_user_message.text or ""
            except Exception:
                try:
                    return prompt.turns[-1].content.text or ""
                except Exception:
                    return str(prompt)

        if isinstance(prompt, Message):
            return prompt.text or ""

        return str(prompt)

    def generate(self, prompt, generations_this_call: int = 1):
        """Совместимость с garak 0.14.x: если buff передал строку/Message,
        оборачиваем её в Conversation.
        """

        if isinstance(prompt, str):
            prompt = Conversation(
                turns=[
                    Turn(
                        role="user",
                        content=Message(text=prompt),
                    )
                ]
            )

        elif isinstance(prompt, Message):
            prompt = Conversation(
                turns=[
                    Turn(
                        role="user",
                        content=prompt,
                    )
                ]
            )

        return super().generate(
            prompt,
            generations_this_call=generations_this_call,
        )

    def _call_model(self, prompt, generations_this_call: int = 1):
        prompt_text = self._prompt_to_text(prompt)
        answer = self._frontend_request(prompt_text)
        return [Message(text=answer)]


DEFAULT_CLASS = "FrontendChainGenerator"