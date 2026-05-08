"""Phonetic entity resolution built on Hunmin transcription.

This layer is for names, aliases, brands, companies, drugs, and places.
It does not train an embedding model. It expands each alias into lexical and
Hunmin phonetic keys, then fuzzy-matches queries to canonical entity ids.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .api import transcribe
from .core.cjk import hangul_to_jamo

HANGUL_INITIALS = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"


def detect_entity_lang(text: str) -> str:
    """Small script detector for alias-key generation."""
    for ch in str(text):
        cp = ord(ch)
        if 0xAC00 <= cp <= 0xD7AF:
            return "ko"
        if 0x3040 <= cp <= 0x30FF:
            return "ja"
        if 0x4E00 <= cp <= 0x9FFF:
            return "zh"
        if 0x0400 <= cp <= 0x04FF:
            return "ru"
        if 0x0600 <= cp <= 0x06FF:
            return "fa"
    return "en"


def strip_accents(text: str) -> str:
    stripped = "".join(
        ch for ch in unicodedata.normalize("NFD", text)
        if unicodedata.category(ch) != "Mn"
    )
    return unicodedata.normalize("NFC", stripped)


def normalize_text(text: str) -> str:
    text = strip_accents(unicodedata.normalize("NFKC", str(text))).lower()
    return re.sub(r"[^0-9a-z가-힣ㄱ-ㅎㅏ-ㅣ一-龥ぁ-ゟ゠-ヿа-яё]+", "", text)


def normalize_jamo_key(text: str) -> str:
    return re.sub(r"[^0-9a-zㄱ-ㅎㅏ-ㅣ]+", "", str(text).lower())


def hangul_initials(text: str) -> str:
    out: list[str] = []
    for ch in str(text):
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            out.append(HANGUL_INITIALS[(code - 0xAC00) // 588])
        elif ch in HANGUL_INITIALS:
            out.append(ch)
    return "".join(out)


def safe_transcribe(text: str, lang: str | None = None) -> str:
    lang = lang or detect_entity_lang(text)
    if lang == "ko":
        return str(text)
    try:
        return transcribe(str(text), lang=lang)
    except Exception:
        return str(text)


def keyset(text: str, lang: str | None = None) -> dict[str, set[str]]:
    raw = str(text).strip()
    norm = normalize_text(raw)
    ko_text = safe_transcribe(raw, lang=lang)
    ko = normalize_text(ko_text)
    jamo = normalize_jamo_key(hangul_to_jamo(ko_text))
    initial = hangul_initials(ko_text) or hangul_initials(raw)
    return {
        "raw": {raw} if raw else set(),
        "norm": {norm} if norm else set(),
        "ko": {ko} if ko else set(),
        "jamo": {jamo} if jamo else set(),
        "initial": {initial} if initial else set(),
    }


def flatten_aliases(aliases: Any) -> list[tuple[str | None, str]]:
    if aliases is None:
        return []
    if isinstance(aliases, list):
        return [(None, str(x)) for x in aliases if str(x).strip()]
    if isinstance(aliases, dict):
        out: list[tuple[str | None, str]] = []
        for lang, values in aliases.items():
            if isinstance(values, list):
                out.extend((str(lang), str(x)) for x in values if str(x).strip())
            elif values:
                out.append((str(lang), str(values)))
        return out
    return [(None, str(aliases))]


def char_ngrams(text: str, n: int = 2) -> set[str]:
    if not text:
        return set()
    if len(text) <= n:
        return {text}
    return {text[i : i + n] for i in range(len(text) - n + 1)}


def jaccard(a: str, b: str) -> float:
    aa, bb = char_ngrams(a), char_ngrams(b)
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / len(aa | bb)


def string_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if len(a) >= 3 and len(b) >= 3 and (a in b or b in a):
        return 0.86
    return max(SequenceMatcher(None, a, b).ratio(), jaccard(a, b))


@dataclass
class Entity:
    id: str
    label: str
    type: str = "entity"
    aliases: dict[str, list[str]] = field(default_factory=dict)
    popularity: float = 0.0
    keys: dict[str, set[str]] = field(default_factory=dict)

    @property
    def all_aliases(self) -> list[tuple[str | None, str]]:
        return [(None, self.label), *flatten_aliases(self.aliases)]


@dataclass
class EntityMatch:
    id: str
    label: str
    type: str
    score: float
    matched_alias: str
    match_level: str
    query_key: str
    entity_key: str
    aliases: dict[str, list[str]]


class PhoneticEntityIndex:
    def __init__(self, entities: list[Entity]):
        self.entities = entities
        for ent in self.entities:
            if not ent.keys:
                ent.keys = self._build_keys(ent)

    @staticmethod
    def _build_keys(entity: Entity) -> dict[str, set[str]]:
        merged: dict[str, set[str]] = {"raw": set(), "norm": set(), "ko": set(), "jamo": set(), "initial": set()}
        for lang, alias in entity.all_aliases:
            for level, values in keyset(alias, lang=lang).items():
                merged[level].update(values)
        return merged

    @classmethod
    def from_jsonl(cls, path: Path | str) -> "PhoneticEntityIndex":
        entities: list[Entity] = []
        path = Path(path)
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                ent_id = row.get("id") or row.get("qid") or row.get("uri")
                if not ent_id:
                    raise ValueError(f"{path}:{line_no}: missing id/qid/uri")
                entities.append(
                    Entity(
                        id=str(ent_id),
                        label=str(row.get("label") or ent_id),
                        type=str(row.get("type") or "entity"),
                        aliases=row.get("aliases") or {},
                        popularity=float(row.get("popularity") or 0.0),
                    )
                )
        return cls(entities)

    def to_jsonl(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for ent in self.entities:
                row = {
                    "id": ent.id,
                    "label": ent.label,
                    "type": ent.type,
                    "aliases": ent.aliases,
                    "popularity": ent.popularity,
                    "keys": {k: sorted(v) for k, v in ent.keys.items()},
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    @classmethod
    def from_index_jsonl(cls, path: Path | str) -> "PhoneticEntityIndex":
        entities: list[Entity] = []
        with Path(path).open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                entities.append(
                    Entity(
                        id=str(row["id"]),
                        label=str(row["label"]),
                        type=str(row.get("type") or "entity"),
                        aliases=row.get("aliases") or {},
                        popularity=float(row.get("popularity") or 0.0),
                        keys={k: set(v) for k, v in (row.get("keys") or {}).items()},
                    )
                )
        return cls(entities)

    @staticmethod
    def _find_alias_for_key(ent: Entity, entity_key: str) -> str:
        if not entity_key:
            return ""
        for lang, alias in ent.all_aliases:
            for values in keyset(alias, lang=lang).values():
                if entity_key in values:
                    return alias
        return entity_key

    def _score_entity(self, query_keys: dict[str, set[str]], ent: Entity) -> tuple[float, dict[str, str]]:
        weights = {"norm": 1.0, "ko": 0.96, "jamo": 0.9, "initial": 0.78}
        best = {"score": 0.0, "level": "", "query_key": "", "entity_key": ""}
        for level, weight in weights.items():
            for query_key in query_keys.get(level, set()):
                for entity_key in ent.keys.get(level, set()):
                    if level == "initial" and query_key != entity_key:
                        continue
                    score = string_similarity(query_key, entity_key) * weight
                    if level == "initial" and query_key:
                        score = 0.93
                    if score > best["score"]:
                        best = {"score": score, "level": level, "query_key": query_key, "entity_key": entity_key}

        if ent.popularity > 0 and best["score"] > 0:
            best["score"] = min(1.0, best["score"] + min(ent.popularity, 100.0) / 10000.0)
        return best["score"], {**best, "alias_hit": self._find_alias_for_key(ent, best["entity_key"])}

    def search(
        self,
        query: str,
        top_k: int = 10,
        type_filter: str | None = None,
        min_score: float = 0.25,
        lang: str | None = None,
    ) -> list[EntityMatch]:
        query_keys = keyset(query, lang=lang)
        matches: list[EntityMatch] = []
        for ent in self.entities:
            if type_filter and ent.type != type_filter:
                continue
            score, detail = self._score_entity(query_keys, ent)
            if score < min_score:
                continue
            matches.append(
                EntityMatch(
                    id=ent.id,
                    label=ent.label,
                    type=ent.type,
                    score=round(score, 4),
                    matched_alias=detail["alias_hit"],
                    match_level=detail["level"],
                    query_key=detail["query_key"],
                    entity_key=detail["entity_key"],
                    aliases=ent.aliases,
                )
            )
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:top_k]


def match_to_dict(match: EntityMatch) -> dict[str, Any]:
    return {
        "id": match.id,
        "label": match.label,
        "type": match.type,
        "score": match.score,
        "matched_alias": match.matched_alias,
        "match_level": match.match_level,
        "query_key": match.query_key,
        "entity_key": match.entity_key,
        "aliases": match.aliases,
    }


__all__ = [
    "Entity",
    "EntityMatch",
    "PhoneticEntityIndex",
    "detect_entity_lang",
    "keyset",
    "match_to_dict",
    "normalize_text",
]
