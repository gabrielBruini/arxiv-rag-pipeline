import json

import redis
from rag.domain.interfaces.session_store import SessionStore


class RedisSessionStore(SessionStore):

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        ttl_seconds: int = 86400,
        max_messages: int = 50,
        key_prefix: str = "session:",
    ):
        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._ttl = ttl_seconds
        self._max = max_messages
        self._prefix = key_prefix

    def _key(self, session_id: str) -> str:
        return f"{self._prefix}{session_id}"

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        items = self._client.lrange(self._key(session_id), 0, -1)
        return [json.loads(item) for item in items]

    def append_message(self, session_id: str, role: str, content: str) -> None:
        key = self._key(session_id)
        pipe = self._client.pipeline()
        pipe.rpush(key, json.dumps({"role": role, "content": content}))
        if self._max:
            pipe.ltrim(key, -self._max, -1)
        if self._ttl:
            pipe.expire(key, self._ttl)
        pipe.execute()

    def is_healthy(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:
            return False
