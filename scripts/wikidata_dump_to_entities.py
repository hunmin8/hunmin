#!/usr/bin/env python3
"""Convert a Wikidata JSON dump stream into Hunmin entity JSONL.

Input can be `.json`, `.json.bz2`, `.json.gz`, or JSONL. The script expects
Wikidata item objects with `id`, `labels`, `aliases`, `claims`, and `sitelinks`.

Example:
    python scripts/wikidata_dump_to_entities.py latest-all.json.bz2 \
      --output output/wikidata_entities_sample.jsonl \
      --limit 100000 --langs en,ko,ja,zh,ru
"""
from __future__ import annotations

import argparse
import bz2
import gzip
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


DEFAULT_LANGS = ["en", "ko", "ja", "zh", "ru"]


TYPE_MAP = {
    # company / organization
    "Q4830453": "company",       # business
    "Q6881511": "company",       # enterprise
    "Q43229": "organization",    # organization
    "Q167037": "organization",   # corporation
    "Q891723": "organization",   # public company
    # person / place
    "Q5": "person",
    "Q515": "place",             # city
    "Q6256": "place",            # country
    "Q82794": "place",           # geographic region
    # products / brands / medical
    "Q431289": "brand",
    "Q2424752": "product",
    "Q28885102": "product",
    "Q11173": "chemical",
    "Q12140": "drug",
    "Q7187": "gene",
    "Q8054": "protein",
    "Q12136": "disease",
}


def open_text(path: Path):
    if str(path).endswith(".bz2"):
        return bz2.open(path, "rt", encoding="utf-8")
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open(encoding="utf-8")


def iter_wikidata_items(path: Path) -> Iterable[dict[str, Any]]:
    with open_text(path) as f:
        for line in f:
            line = line.strip()
            if not line or line in {"[", "]"}:
                continue
            if line.endswith(","):
                line = line[:-1]
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") == "item" and row.get("id", "").startswith("Q"):
                yield row


def text_value(obj: dict[str, Any] | None) -> str:
    if not obj:
        return ""
    return str(obj.get("value") or "").strip()


def collect_aliases(row: dict[str, Any], langs: list[str]) -> tuple[str, dict[str, list[str]]]:
    labels = row.get("labels") or {}
    aliases = row.get("aliases") or {}

    label = text_value(labels.get("en")) or text_value(next(iter(labels.values()), None)) or row["id"]
    out: dict[str, list[str]] = {}
    for lang in langs:
        values = []
        label_value = text_value(labels.get(lang))
        if label_value:
            values.append(label_value)
        for alias in aliases.get(lang) or []:
            value = text_value(alias)
            if value:
                values.append(value)
        values = list(dict.fromkeys(v for v in values if len(v) <= 120))
        if values:
            out[lang] = values
    return label, out


def claim_qids(row: dict[str, Any], prop: str) -> list[str]:
    values = []
    for claim in (row.get("claims") or {}).get(prop) or []:
        mainsnak = claim.get("mainsnak") or {}
        datavalue = mainsnak.get("datavalue") or {}
        value = datavalue.get("value")
        if isinstance(value, dict):
            numeric_id = value.get("numeric-id")
            if numeric_id is not None:
                values.append(f"Q{numeric_id}")
    return values


def infer_type(row: dict[str, Any]) -> str:
    qids = [*claim_qids(row, "P31"), *claim_qids(row, "P279")]
    for qid in qids:
        if qid in TYPE_MAP:
            return TYPE_MAP[qid]
    return "entity"


def popularity(row: dict[str, Any]) -> int:
    sitelinks = row.get("sitelinks") or {}
    return min(100, int(len(sitelinks) * 2))


def enough_signal(aliases: dict[str, list[str]], min_langs: int, min_aliases: int) -> bool:
    alias_count = sum(len(v) for v in aliases.values())
    return len(aliases) >= min_langs and alias_count >= min_aliases


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--langs", default=",".join(DEFAULT_LANGS))
    ap.add_argument("--types", default="", help="optional comma list: company,person,place,brand,product,drug,chemical,disease")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-langs", type=int, default=2)
    ap.add_argument("--min-aliases", type=int, default=2)
    args = ap.parse_args()

    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    type_filter = {x.strip() for x in args.types.split(",") if x.strip()}
    args.output.parent.mkdir(parents=True, exist_ok=True)

    counts = Counter()
    written = 0
    with args.output.open("w", encoding="utf-8") as out:
        for row in iter_wikidata_items(args.dump):
            ent_type = infer_type(row)
            if type_filter and ent_type not in type_filter:
                counts["skip_type"] += 1
                continue
            label, aliases = collect_aliases(row, langs)
            if not enough_signal(aliases, args.min_langs, args.min_aliases):
                counts["skip_signal"] += 1
                continue
            item = {
                "id": row["id"],
                "label": label,
                "type": ent_type,
                "aliases": aliases,
                "popularity": popularity(row),
            }
            out.write(json.dumps(item, ensure_ascii=False) + "\n")
            written += 1
            counts[f"type_{ent_type}"] += 1
            if args.limit and written >= args.limit:
                break

    print(json.dumps({"output": str(args.output), "written": written, "counts": counts}, ensure_ascii=False, default=dict))


if __name__ == "__main__":
    main()
