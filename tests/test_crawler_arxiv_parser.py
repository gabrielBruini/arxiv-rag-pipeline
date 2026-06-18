from lxml import etree

from infrastructure.crawler.arxiv_repository import ArxivRepository
from infrastructure.crawler.http_client import HttpClient

_SAMPLE = """<?xml version="1.0"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
 <ListRecords>
  <record><metadata>
   <arXiv xmlns="http://arxiv.org/OAI/arXiv/">
    <id>2401.00001</id>
    <title>Sample Title</title>
    <abstract>Sample abstract.</abstract>
    <authors><author><keyname>Doe</keyname></author><author><keyname>Roe</keyname></author></authors>
    <categories>cs.AI cs.LG</categories>
   </arXiv>
  </metadata></record>
  <resumptionToken>TOKEN123</resumptionToken>
 </ListRecords>
</OAI-PMH>"""

_EMPTY = """<?xml version="1.0"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><ListRecords></ListRecords></OAI-PMH>"""


def _repo():
    return ArxivRepository(HttpClient())


def test_parses_record_into_paper():
    root = etree.fromstring(_SAMPLE.encode("utf-8"))
    papers = _repo()._parse_records(root)
    assert len(papers) == 1
    p = papers[0]
    assert p.arxiv_id == "2401.00001"
    assert p.title == "Sample Title"
    assert p.categories == ["cs.AI", "cs.LG"]
    assert p.authors == ["Doe", "Roe"]
    assert p.is_valid


def test_extracts_resumption_token():
    root = etree.fromstring(_SAMPLE.encode("utf-8"))
    assert _repo()._extract_resumption_token(root) == "TOKEN123"


def test_no_resumption_token_returns_none():
    root = etree.fromstring(_EMPTY.encode("utf-8"))
    assert _repo()._extract_resumption_token(root) is None


def test_build_params_first_page_uses_set_and_prefix():
    params = _repo()._build_params(None)
    assert params["verb"] == "ListRecords"
    assert params["set"] == "cs"
    assert "metadataPrefix" in params


def test_build_params_with_token_uses_only_token():
    assert _repo()._build_params("TK") == {
        "verb": "ListRecords",
        "resumptionToken": "TK",
    }


def test_build_params_includes_date_filters():
    params = _repo()._build_params(None, from_date="2024-01-01", until_date="2024-02-01")
    assert params["from"] == "2024-01-01"
    assert params["until"] == "2024-02-01"


def test_build_params_omits_dates_when_absent():
    params = _repo()._build_params(None)
    assert "from" not in params
    assert "until" not in params


def test_build_params_with_token_ignores_dates():
    assert _repo()._build_params("TK", from_date="2024-01-01") == {
        "verb": "ListRecords",
        "resumptionToken": "TK",
    }
