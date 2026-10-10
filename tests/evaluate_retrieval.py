import json
from pathlib import Path
from portfolio_agent.rag_service import search_portfolio

CASES = json.loads(Path(__file__).with_name("evaluation_questions.json").read_text(encoding="utf-8"))
passed = 0
for case in CASES:
    result = search_portfolio(case["question"], top_k=5)
    actual = {item["source"] for item in result.get("results", [])}
    expected = set(case["expected_sources"])
    ok = bool(actual & expected)
    passed += int(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {case['question']} | {sorted(actual)}")
print(f"{passed}/{len(CASES)} retrieval checks passed")
raise SystemExit(0 if passed == len(CASES) else 1)
