import json

from tools.deepseek import Analysis
from tools.result_normalizer import ResultStore

from . import MkDocsReporter


def main() -> None:
    store = ResultStore()
    result = store.load()
    analysis_path = store.latest().parent / "analysis.json"
    analysis = Analysis(**json.loads(analysis_path.read_text(encoding="utf-8")))
    print(MkDocsReporter().generate(result, analysis, publish_docs=True))


if __name__ == "__main__":
    main()
