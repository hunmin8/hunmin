"""Phonetic entity resolver tests."""
from pathlib import Path

from hunmin import PhoneticEntityIndex
from hunmin.entity import keyset


FIXTURE = Path(__file__).resolve().parents[1] / "hunmin" / "data" / "entities" / "sample_entities.jsonl"


def test_entity_exports_available():
    idx = PhoneticEntityIndex.from_jsonl(FIXTURE)
    assert len(idx.entities) >= 10


def test_multilingual_company_aliases_resolve_to_same_entity():
    idx = PhoneticEntityIndex.from_jsonl(FIXTURE)
    for query in ["samsung", "samzung elec", "삼성전자", "ㅅㅅㅈㅈ", "サムスン電子"]:
        match = idx.search(query, top_k=1)[0]
        assert match.id == "Q67"
        assert match.label == "Samsung Electronics"


def test_japanese_drug_and_company_transcription_keys():
    ibu = keyset("イブプロフェン", lang="ja")
    pfizer = keyset("ファイザー", lang="ja")
    assert "이부프로펜" in ibu["ko"]
    assert "화이자" in pfizer["ko"]


def test_japanese_aliases_resolve():
    idx = PhoneticEntityIndex.from_jsonl(FIXTURE)
    assert idx.search("イブプロフェン", top_k=1)[0].id == "Q207"
    assert idx.search("ファイザー", top_k=1)[0].id == "Q206212"
    assert idx.search("ノバルティス", top_k=1)[0].id == "Q383126"
    assert idx.search("アリアンツ", top_k=1)[0].id == "Q487"


def test_korean_typo_resolves_by_phonetic_key():
    idx = PhoneticEntityIndex.from_jsonl(FIXTURE)
    assert idx.search("아세트아미노팬", top_k=1)[0].id == "Q206921"
    assert idx.search("이부프로팬", top_k=1)[0].id == "Q207"
