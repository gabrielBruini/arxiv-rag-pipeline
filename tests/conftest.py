import sys
from pathlib import Path

_CRAWLER_SRC = Path(__file__).resolve().parent.parent / "crawler" / "src"
if str(_CRAWLER_SRC) not in sys.path:
    sys.path.insert(0, str(_CRAWLER_SRC))
