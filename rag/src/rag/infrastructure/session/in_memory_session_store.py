from collections import defaultdict

from rag.domain.interfaces.session_store import SessionStore


class InMemorySessionStore(SessionStore):

    def __init__(self):
        self._sessions: dict[str, list[dict[str, str]]] = defaultdict(list)

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        return self._sessions[session_id]

    def append_message(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id].append({"role": role, "content": content})

    def is_healthy(self) -> bool:
        return True
