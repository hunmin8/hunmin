#!/usr/bin/env python3
"""Build a complete-first Hunmin entity file from a Wikidata JSON dump.

This is intended for product indexes where some domains must not be sampled.
Chemical and drug entities are collected exhaustively from expanded Wikidata
classes and external-id signals, while broad domains such as companies, brands,
and places can still be capped by popularity.
"""
from __future__ import annotations

import argparse
import bz2
import gzip
import json
import re
import subprocess
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable


DEFAULT_LANGS = ["en", "ko", "ja", "zh", "ru"]

COMPANY_CLASSES = {
    "Q4830453",   # business
    "Q6881511",   # enterprise
    "Q43229",     # organization
    "Q167037",    # corporation
    "Q891723",    # public company
}
BRAND_CLASSES = {"Q431289"}
PLACE_CLASSES = {"Q515", "Q6256", "Q82794"}
DRUG_CLASSES = {
    "Q12140",     # drug
}
CHEMICAL_CLASSES = {
    "Q11173",      # chemical compound
    "Q59199015",   # group of stereoisomers
    "Q113145171",  # type of chemical entity
}

# External-id properties are often more reliable than P31 for chemical/drug
# coverage because many items are typed as specific chemical subcategories.
CHEMICAL_EXTERNAL_ID_PROPS = {
    "P662",     # PubChem CID
    "P665",     # KEGG ID
    "P231",     # CAS Registry Number
    "P232",     # EC number
    "P235",     # InChIKey
    "P234",     # InChI
    "P592",     # ChEMBL ID
    "P683",     # ChEBI ID
    "P1579",    # Reaxys registry number
    "P3117",    # DSSTox substance ID
}
DRUG_EXTERNAL_ID_PROPS = {
    "P267",     # ATC code
    "P2175",    # medical condition treated
    "P715",     # DrugBank ID
    "P2313",    # NDF-RT ID
    "P3345",    # RxNorm CUI
    "P3775",    # disruptive drug target
    "P595",     # Guide to Pharmacology Ligand ID
}

TYPE_CLASS_MAP = {
    "company": COMPANY_CLASSES,
    "brand": BRAND_CLASSES,
    "place": PLACE_CLASSES,
    "drug": DRUG_CLASSES,
    "chemical": CHEMICAL_CLASSES,
}


@contextmanager
def open_text(path: Path):
    if str(path).endswith(".bz2"):
        proc = subprocess.Popen(
            ["bzcat", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1024 * 1024,
        )
        try:
            if proc.stdout is None:
                raise RuntimeError("failed to open bzcat stdout")
            yield proc.stdout
        finally:
            if proc.stdout is not None:
                proc.stdout.close()
            proc.wait()
        return
    if str(path).endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            yield f
        return
    with path.open(encoding="utf-8") as f:
        yield f


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
            if row.get("type") == "item" and str(row.get("id", "")).startswith("Q"):
                yield row


def text_value(obj: dict[str, Any] | None) -> str:
    if not obj:
        return ""
    return str(obj.get("value") or "").strip()


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


def has_claim(row: dict[str, Any], props: set[str]) -> bool:
    claims = row.get("claims") or {}
    return any(prop in claims for prop in props)


def infer_types(row: dict[str, Any]) -> set[str]:
    qids = set(claim_qids(row, "P31")) | set(claim_qids(row, "P279"))
    out = {ent_type for ent_type, classes in TYPE_CLASS_MAP.items() if qids & classes}
    if has_claim(row, DRUG_EXTERNAL_ID_PROPS):
        out.add("drug")
    if has_claim(row, CHEMICAL_EXTERNAL_ID_PROPS):
        out.add("chemical")
    if "drug" in out:
        out.add("chemical")
    return out


def popularity(row: dict[str, Any]) -> int:
    sitelinks = row.get("sitelinks") or {}
    return min(100, int(len(sitelinks) * 2))


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


def enough_signal(aliases: dict[str, list[str]], min_langs: int, min_aliases: int) -> bool:
    alias_count = sum(len(v) for v in aliases.values())
    return len(aliases) >= min_langs and alias_count >= min_aliases


def should_keep(ent_type: str, kept: Counter, caps: dict[str, int]) -> bool:
    cap = caps.get(ent_type, 0)
    return cap <= 0 or kept[ent_type] < cap


def parse_caps(raw: str) -> dict[str, int]:
    caps: dict[str, int] = {}
    if not raw:
        return caps
    for part in raw.split(","):
        if not part.strip():
            continue
        key, value = part.split("=", 1)
        caps[key.strip()] = int(value.strip())
    return caps


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--langs", default=",".join(DEFAULT_LANGS))
    ap.add_argument("--types", default="chemical,drug,company,brand,place")
    ap.add_argument("--caps", default="company=25000,brand=25000,place=25000", help="comma list like company=25000,brand=25000; 0/unset means uncapped")
    ap.add_argument("--min-langs", type=int, default=1)
    ap.add_argument("--min-aliases", type=int, default=1)
    ap.add_argument("--progress-every", type=int, default=250000)
    args = ap.parse_args()

    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    wanted = [x.strip() for x in args.types.split(",") if x.strip()]
    caps = parse_caps(args.caps)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    counts = Counter()
    kept = Counter()
    seen_ids: set[str] = set()
    with args.output.open("w", encoding="utf-8") as out:
        for scanned, row in enumerate(iter_wikidata_items(args.dump), start=1):
            ent_types = [x for x in wanted if x in infer_types(row)]
            if not ent_types:
                counts["skip_type"] += 1
                continue
            label, aliases = collect_aliases(row, langs)
            if not enough_signal(aliases, args.min_langs, args.min_aliases):
                counts["skip_signal"] += 1
                continue

            for ent_type in ent_types:
                if not should_keep(ent_type, kept, caps):
                    counts[f"skip_cap_{ent_type}"] += 1
                    continue
                row_id = row["id"] if len(ent_types) == 1 else f"{row['id']}:{ent_type}"
                if row_id in seen_ids:
                    continue
                seen_ids.add(row_id)
                item = {
                    "id": row["id"],
                    "label": label,
                    "type": ent_type,
                    "aliases": aliases,
                    "popularity": popularity(row),
                }
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
                kept[ent_type] += 1
                counts[f"type_{ent_type}"] += 1

            if args.progress_every and scanned % args.progress_every == 0:
                print(json.dumps({"scanned": scanned, "kept": kept, "counts": counts}, ensure_ascii=False, default=dict), file=sys.stderr, flush=True)

    print(json.dumps({"output": str(args.output), "kept": kept, "counts": counts}, ensure_ascii=False, default=dict))


if __name__ == "__main__":
    main()
