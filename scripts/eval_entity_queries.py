#!/usr/bin/env python3
"""Evaluate Hunmin phonetic entity resolution gold queries."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hunmin.entity import PhoneticEntityIndex, match_to_dict  # noqa: E402

DEFAULT_ENTITIES = ROOT / "hunmin" / "data" / "entities" / "sample_entities.jsonl"
DEFAULT_GOLD = ROOT / "tests" / "gold" / "entity_queries_100.jsonl"


def iter_gold(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not row.get("query") or not row.get("expected_id"):
                raise ValueError(f"{path}:{line_no}: query and expected_id are required")
            rows.append(row)
    return rows


def load_index(args: argparse.Namespace) -> PhoneticEntityIndex:
    if args.index and args.index.exists():
        return PhoneticEntityIndex.from_index_jsonl(args.index)
    return PhoneticEntityIndex.from_jsonl(args.entities)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    ap.add_argument("--entities", type=Path, default=DEFAULT_ENTITIES)
    ap.add_argument("--index", type=Path)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--min-score", type=float, default=0.25)
    ap.add_argument("--use-type-filter", action="store_true")
    ap.add_argument("--max-failures", type=int, default=20)
    args = ap.parse_args()

    index = load_index(args)
    rows = iter_gold(args.gold)
    top1 = 0
    topk = 0
    failures = []
    for row in rows:
        type_filter = row.get("type") if args.use_type_filter else None
        matches = index.search(
            row["query"],
            top_k=args.top_k,
            type_filter=type_filter,
            min_score=args.min_score,
            lang=row.get("lang"),
        )
        ids = [m.id for m in matches]
        if ids[:1] == [row["expected_id"]]:
            top1 += 1
        if row["expected_id"] in ids:
            topk += 1
        elif len(failures) < args.max_failures:
            failures.append(
                {
                    "query": row["query"],
                    "expected_id": row["expected_id"],
                    "type": row.get("type"),
                    "matches": [match_to_dict(m) for m in matches],
                }
            )

    total = len(rows)
    result = {
        "gold": str(args.gold),
        "total": total,
        "top1_accuracy": round(top1 / total, 4) if total else 0.0,
        "top5_accuracy": round(topk / total, 4) if total else 0.0,
        "top1": top1,
        "top5": topk,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
