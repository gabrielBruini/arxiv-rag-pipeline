from unittest.mock import MagicMock, patch

from shared.infrastructure.embedding import sentence_transformer_repository as mod
from shared.infrastructure.embedding.sentence_transformer_repository import (
    SentenceTransformerRepository,
)


def test_load_model_uses_cache_first():
    fake_model = MagicMock()
    with patch.object(mod, "SentenceTransformer", return_value=fake_model) as st:
        out = SentenceTransformerRepository._load_model("m", None, False)
    assert out is fake_model
    st.assert_called_once()
    assert st.call_args.kwargs["local_files_only"] is True


def test_load_model_falls_back_to_online_when_cache_misses():
    fake_model = MagicMock()
    with patch.object(
        mod, "SentenceTransformer", side_effect=[Exception("no cache"), fake_model]
    ) as st:
        out = SentenceTransformerRepository._load_model("m", None, False)
    assert out is fake_model
    assert st.call_count == 2
    assert st.call_args_list[1].kwargs["local_files_only"] is False


def test_load_model_forced_offline_does_not_retry():
    fake_model = MagicMock()
    with patch.object(mod, "SentenceTransformer", return_value=fake_model) as st:
        out = SentenceTransformerRepository._load_model("m", None, True)
    assert out is fake_model
    st.assert_called_once()
    assert st.call_args.kwargs["local_files_only"] is True
