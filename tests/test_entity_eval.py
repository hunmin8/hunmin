"""Evaluation utility coverage for phonetic entity queries."""
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "tests" / "gold" / "entity_queries_100.jsonl"


def test_entity_query_gold_has_100_rows():
    rows = [json.loads(line) for line in GOLD.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 100
    assert all(row["query"] and row["expected_id"] for row in rows)


def test_entity_eval_cli_sample_gold():
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "eval_entity_queries.py"),
            "--gold",
            str(GOLD),
            "--use-type-filter",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    result = json.loads(proc.stdout)
    assert result["total"] == 100
    assert result["top1_accuracy"] >= 0.95
    assert result["top5_accuracy"] == 1.0
