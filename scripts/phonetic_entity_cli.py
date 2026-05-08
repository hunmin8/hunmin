#!/usr/bin/env python3
"""Build and query Hunmin phonetic entity indexes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hunmin.entity import PhoneticEntityIndex, keyset, match_to_dict  # noqa: E402

DEFAULT_ENTITIES = ROOT / "hunmin" / "data" / "entities" / "sample_entities.jsonl"


def load_index(args) -> PhoneticEntityIndex:
    if args.index and args.index.exists():
        return PhoneticEntityIndex.from_index_jsonl(args.index)
    return PhoneticEntityIndex.from_jsonl(args.entities)


def cmd_build(args) -> None:
    index = PhoneticEntityIndex.from_jsonl(args.entities)
    index.to_jsonl(args.output)
    print(json.dumps({"built": str(args.output), "entities": len(index.entities)}, ensure_ascii=False))


def cmd_search(args) -> None:
    index = load_index(args)
    query = " ".join(args.query).strip()
    if args.show_keys:
        print(json.dumps({"query": query, "query_keys": {k: sorted(v) for k, v in keyset(query, lang=args.lang).items()}}, ensure_ascii=False))
    for match in index.search(query, top_k=args.top_k, type_filter=args.type_filter, min_score=args.min_score, lang=args.lang):
        row = match_to_dict(match)
        if not args.with_aliases:
            row.pop("aliases", None)
        print(json.dumps(row, ensure_ascii=False))


def cmd_demo(args) -> None:
    index = load_index(args)
    queries = [
        "samsung", "samzung elec", "삼성전자", "ㅅㅅㅈㅈ",
        "アルリアンツ", "アリアンツ", "알리안스", "Allianz",
        "イブプロフェン", "이부프로팬", "ファイザー", "화이자",
        "아세트아미노팬", "루이뷔통", "도꾜",
    ]
    for query in queries:
        print(f"\n# {query}")
        for match in index.search(query, top_k=args.top_k, min_score=args.min_score):
            row = match_to_dict(match)
            row.pop("aliases", None)
            print(json.dumps(row, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build", help="build key-expanded JSONL index")
    build.add_argument("--entities", type=Path, default=DEFAULT_ENTITIES)
    build.add_argument("--output", type=Path, required=True)
    build.set_defaults(func=cmd_build)

    search = sub.add_parser("search", help="search entities")
    search.add_argument("query", nargs="+")
    search.add_argument("--entities", type=Path, default=DEFAULT_ENTITIES)
    search.add_argument("--index", type=Path)
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--type", dest="type_filter")
    search.add_argument("--lang")
    search.add_argument("--min-score", type=float, default=0.25)
    search.add_argument("--show-keys", action="store_true")
    search.add_argument("--with-aliases", action="store_true")
    search.set_defaults(func=cmd_search)

    demo = sub.add_parser("demo", help="run fixed sample queries")
    demo.add_argument("--entities", type=Path, default=DEFAULT_ENTITIES)
    demo.add_argument("--index", type=Path)
    demo.add_argument("--top-k", type=int, default=3)
    demo.add_argument("--min-score", type=float, default=0.25)
    demo.set_defaults(func=cmd_demo)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
