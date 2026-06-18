import json
from unittest.mock import MagicMock, patch

from rag.infrastructure.session import redis_session_store as mod
from rag.infrastructure.session.redis_session_store import RedisSessionStore


def _store(client):
    with patch.object(mod.redis.Redis, "from_url", return_value=client):
        return RedisSessionStore(max_messages=5, ttl_seconds=100)


def test_get_history_parses_json_items():
    client = MagicMock()
    client.lrange.return_value = [
        json.dumps({"role": "user", "content": "hi"}),
        json.dumps({"role": "assistant", "content": "yo"}),
    ]
    store = _store(client)
    assert store.get_history("s") == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "yo"},
    ]
    client.lrange.assert_called_once_with("session:s", 0, -1)


def test_append_message_pushes_trims_and_sets_ttl():
    client = MagicMock()
    pipe = MagicMock()
    client.pipeline.return_value = pipe
    store = _store(client)
    store.append_message("s", "user", "hi")
    assert pipe.rpush.call_args.args[0] == "session:s"
    assert json.loads(pipe.rpush.call_args.args[1]) == {"role": "user", "content": "hi"}
    pipe.ltrim.assert_called_once_with("session:s", -5, -1)
    pipe.expire.assert_called_once_with("session:s", 100)
    pipe.execute.assert_called_once()


def test_is_healthy_true_when_ping_ok():
    client = MagicMock()
    client.ping.return_value = True
    assert _store(client).is_healthy() is True


def test_is_healthy_false_when_ping_raises():
    client = MagicMock()
    client.ping.side_effect = Exception("down")
    assert _store(client).is_healthy() is False
