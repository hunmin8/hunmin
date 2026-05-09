#!/usr/bin/env python3
"""Build Hunmin entity JSONL from Wikidata SPARQL + wbgetentities.

SPARQL is used only to select candidate QIDs by type and sitelink popularity.
Labels and aliases are fetched in batches through the Wikidata entity API to
avoid expensive alias joins in the SPARQL service.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_LANGS = ["en", "ko", "ja", "zh", "ru"]

TYPE_CLASSES = {
    "company": ["Q4830453", "Q6881511", "Q167037", "Q891723"],
    "brand": ["Q431289"],
    "drug": ["Q12140"],
    "chemical": [
        "Q11173",      # chemical compound
        "Q59199015",   # group of stereoisomers
        "Q113145171",  # type of chemical entity
    ],
    "place": ["Q515", "Q6256", "Q82794"],
}

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
ENTITY_ENDPOINT = "https://www.wikidata.org/w/api.php"
USER_AGENT = "hunmin-entity-builder/3.45 (+https://github.com/meshpop/hunmin)"


def http_json(url: str, params: dict[str, str], timeout: int = 60, retries: int = 4) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{url}?{query}",
        headers={"Accept": "application/sparql-results+json, application/json", "User-Agent": USER_AGENT},
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - network-dependent CLI
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"request failed after {retries} attempts: {last_error}")


def sparql_candidates(entity_type: str, limit: int, offset: int = 0, direct_instance_only: bool = True) -> list[tuple[str, int]]:
    classes = TYPE_CLASSES[entity_type]
    values = " ".join(f"wd:{qid}" for qid in classes)
    instance_path = "wdt:P31" if direct_instance_only else "wdt:P31/wdt:P279*"
    query = f"""
SELECT ?item ?sitelinks WHERE {{
  VALUES ?class {{ {values} }}
  ?item {instance_path} ?class .
  ?item wikibase:sitelinks ?sitelinks .
}}
GROUP BY ?item ?sitelinks
ORDER BY DESC(?sitelinks)
LIMIT {int(limit)}
OFFSET {int(offset)}
"""
    data = http_json(SPARQL_ENDPOINT, {"query": query, "format": "json"}, timeout=90)
    rows: list[tuple[str, int]] = []
    for binding in data.get("results", {}).get("bindings", []):
        uri = binding["item"]["value"]
        qid = uri.rsplit("/", 1)[-1]
        sitelinks = int(binding.get("sitelinks", {}).get("value") or 0)
        rows.append((qid, sitelinks))
    return rows


def batched(values: list[str], size: int) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def fetch_entities(qids: list[str], langs: list[str]) -> dict[str, Any]:
    data = http_json(
        ENTITY_ENDPOINT,
        {
            "action": "wbgetentities",
            "ids": "|".join(qids),
            "props": "labels|aliases",
            "languages": "|".join(langs),
            "format": "json",
        },
        timeout=60,
    )
    return data.get("entities", {})


def text_value(obj: dict[str, Any] | None) -> str:
    if not obj:
        return ""
    return str(obj.get("value") or "").strip()


def entity_row(qid: str, ent_type: str, popularity: int, entity: dict[str, Any], langs: list[str]) -> dict[str, Any] | None:
    labels = entity.get("labels") or {}
    aliases = entity.get("aliases") or {}
    label = text_value(labels.get("en")) or text_value(next(iter(labels.values()), None)) or qid

    out_aliases: dict[str, list[str]] = {}
    for lang in langs:
        values: list[str] = []
        label_value = text_value(labels.get(lang))
        if label_value:
            values.append(label_value)
        for alias in aliases.get(lang) or []:
            value = text_value(alias)
            if value:
                values.append(value)
        values = list(dict.fromkeys(v for v in values if len(v) <= 120))
        if values:
            out_aliases[lang] = values

    if sum(len(v) for v in out_aliases.values()) < 2:
        return None
    return {"id": qid, "label": label, "type": ent_type, "aliases": out_aliases, "popularity": min(100, popularity * 2)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--types", default="company,brand,drug,chemical,place")
    ap.add_argument("--langs", default=",".join(DEFAULT_LANGS))
    ap.add_argument("--limit", type=int, default=100000)
    ap.add_argument("--per-type-limit", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=50)
    ap.add_argument("--subclass-expanded", action="store_true", help="use wdt:P31/wdt:P279* instead of direct P31")
    args = ap.parse_args()

    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    types = [x.strip() for x in args.types.split(",") if x.strip()]
    unknown = [x for x in types if x not in TYPE_CLASSES]
    if unknown:
        raise ValueError(f"unknown types: {unknown}")

    per_type_limit = args.per_type_limit or max(args.limit // max(len(types), 1), 1)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    written = 0
    counts = Counter()
    with args.output.open("w", encoding="utf-8") as out:
        for ent_type in types:
            candidates = sparql_candidates(ent_type, per_type_limit, direct_instance_only=not args.subclass_expanded)
            counts[f"candidate_{ent_type}"] = len(candidates)
            popularity = {qid: sitelinks for qid, sitelinks in candidates}
            qids = [qid for qid, _ in candidates if qid not in seen]
            for batch in batched(qids, args.batch_size):
                entities = fetch_entities(batch, langs)
                for qid in batch:
                    seen.add(qid)
                    row = entity_row(qid, ent_type, popularity[qid], entities.get(qid) or {}, langs)
                    if not row:
                        counts["skip_signal"] += 1
                        continue
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
                    written += 1
                    counts[f"type_{ent_type}"] += 1
                    if written >= args.limit:
                        print(json.dumps({"output": str(args.output), "written": written, "counts": counts}, ensure_ascii=False, default=dict))
                        return
                time.sleep(0.1)

    print(json.dumps({"output": str(args.output), "written": written, "counts": counts}, ensure_ascii=False, default=dict))


if __name__ == "__main__":
    main()
