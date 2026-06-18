from shared.domain.entities.paper import Paper


def test_is_valid_true_with_title_and_abstract():
    assert Paper(arxiv_id="1", title="T", abstract="A").is_valid


def test_is_valid_false_without_abstract():
    assert not Paper(arxiv_id="1", title="T", abstract="").is_valid


def test_is_valid_false_without_title():
    assert not Paper(arxiv_id="1", title="", abstract="A").is_valid


def test_primary_category_returns_first():
    p = Paper(arxiv_id="1", title="T", abstract="A", categories=["cs.AI", "cs.LG"])
    assert p.primary_category == "cs.AI"


def test_primary_category_none_when_empty():
    assert Paper(arxiv_id="1", title="T", abstract="A").primary_category is None


def test_to_chunk_text_contains_all_fields():
    p = Paper(
        arxiv_id="1",
        title="Deep Nets",
        abstract="We study X.",
        categories=["cs.AI"],
        authors=["Doe"],
    )
    text = p.to_chunk_text()
    assert "Deep Nets" in text
    assert "We study X." in text
    assert "cs.AI" in text
    assert "Doe" in text
