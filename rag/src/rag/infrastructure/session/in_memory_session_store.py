from collections import defaultdict


class InMemorySessionStore:
    """
    Guarda o histórico de mensagens por sessão, em memória.

    Simples e funcional para uso local/desenvolvimento. Se o processo reiniciar,
    todo o histórico se perde — para produção, trocar por Redis/Postgres depois.
    """

    def __init__(self):
        self._sessions: dict[str, list[dict[str, str]]] = defaultdict(list)

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        return self._sessions[session_id]

    def append_message(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id].append({"role": role, "content": content})