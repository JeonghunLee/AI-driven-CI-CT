import json

from test_envs.tools.local_llm import Analysis
from test_envs.tools.result_normalizer import ResultStore

from . import MkDocsReporter


def main() -> None:
    store = ResultStore()
    result_path = store.latest()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    result = store.load(result_path)
    analysis = Analysis(**payload["analysis"])
    print(MkDocsReporter().generate(result, analysis, publish_docs=True))


if __name__ == "__main__":
    main()
