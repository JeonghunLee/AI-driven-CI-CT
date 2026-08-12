import json

from tools.ollama import Analysis
from tools.result_normalizer import ResultStore

from . import MkDocsReporter


def main() -> None:
    store = ResultStore()
    result = store.load()
    analysis_path = store.root / "json" / "latest-analysis.json"
    analysis = Analysis(**json.loads(analysis_path.read_text(encoding="utf-8")))
    print(MkDocsReporter().generate(result, analysis))


if __name__ == "__main__":
    main()

