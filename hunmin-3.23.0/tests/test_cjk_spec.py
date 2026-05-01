"""CJK NIKL convention regression test (v3.3).

Ja/zh/ko 전사 결정성 + NIKL 외래어 표기 컨벤션 회귀 테스트.

Run: pytest tests/test_cjk_spec.py -v
"""
import pytest
from hunmin import transcribe


# ============== Japanese — NIKL ==============
JA_GOLD = [
    # 도/현/부 (행정구역) — NIKL 컨벤션
    ('東京', '도쿄'),
    ('大阪', '오사카'),
    ('京都', '교토'),
    ('神戸', '고베'),
    ('福岡', '후쿠오카'),
    ('札幌', '삿포로'),
    ('北海道', '홋카이도'),
    ('名古屋', '나고야'),
    # 인사 표현
    ('こんにちは', '곤니치와'),
    ('ありがとう', '아리가토'),
    ('さようなら', '사요나라'),
    # 한자+가나
    ('東京都', '도쿄도'),
    ('大阪府', '오사카부'),
    ('青森県', '아오모리현'),
]


# ============== Chinese (Mandarin) — NIKL ==============
ZH_GOLD = [
    ('中国', '중궈'),
    ('上海', '상하이'),
    ('北京', '베이징'),
    ('天津', '톈진'),
    ('广州', '광저우'),
    ('深圳', '선전'),
    ('习近平', '시진핑'),
    ('毛泽东', '마오쩌둥'),  # v3.4: NIKL ze→쩌 fix applied
    ('邓小平', '덩샤오핑'),
    ('武汉', '우한'),
    ('成都', '청두'),
    ('西安', '시안'),
]


# ============== Korean (한자+native) ==============
KO_GOLD = [
    ('학교', '학교'),
    ('서울', '서울'),
    ('대한민국', '대한민국'),
    ('한국', '한국'),
]


@pytest.mark.parametrize("text,expected", JA_GOLD)
def test_japanese_nikl(text, expected):
    """일본어 NIKL 외래어 표기."""
    try:
        out = transcribe(text, 'ja', level=1)
    except ImportError:
        pytest.skip("pykakasi not installed")
    assert out == expected, f"{text!r} → {out!r}, expected {expected!r}"


@pytest.mark.parametrize("text,expected", ZH_GOLD)
def test_chinese_nikl(text, expected):
    """중국어(만다린) NIKL 외래어 표기."""
    try:
        out = transcribe(text, 'zh', level=1)
    except ImportError:
        pytest.skip("pypinyin not installed")
    assert out == expected, f"{text!r} → {out!r}, expected {expected!r}"


@pytest.mark.parametrize("text,expected", KO_GOLD)
def test_korean_native(text, expected):
    """한국어 — pass-through 또는 hanja 전사."""
    try:
        out = transcribe(text, 'ko', level=1)
    except ImportError:
        pytest.skip("hanja not installed")
    assert out == expected, f"{text!r} → {out!r}, expected {expected!r}"


def test_cjk_determinism():
    """CJK 전사 결정성 — 같은 입력 → 같은 출력 50회."""
    cases = [('東京', 'ja'), ('中国', 'zh'), ('서울', 'ko')]
    for text, lang in cases:
        try:
            first = transcribe(text, lang, level=1)
        except ImportError:
            continue
        for _ in range(49):
            out = transcribe(text, lang, level=1)
            assert out == first, f"Non-deterministic on ({text!r}, {lang!r})"


def test_cjk_return_tokens_unsupported():
    """CJK는 return_tokens=True 미지원 — 명시적 ValueError."""
    for lang in ('ja', 'zh', 'ko'):
        with pytest.raises(ValueError, match='미지원'):
            transcribe('test', lang, return_tokens=True)
