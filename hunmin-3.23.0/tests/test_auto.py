"""transcribe_auto regression test (v3.9).

mixed-script auto-routing + digit/symbol transliteration의 leak-0 보장 검증.
"""
import pytest
from hunmin import transcribe_auto, HUNMIN_NIKL, UHPS_CORE


# ============== Script auto-routing ==============
SCRIPT_ROUTING = [
    # (input, expected substring)
    ('Hello',      '헬로'),         # Latin/en
    ('Москва',     '모스크바'),     # Cyrillic/ru
    ('東京',       '징'),           # CJK alone → zh (둥징)
    ('東京 です',  '도쿄'),         # CJK + kana → ja (도쿄)
    ('こんにちは', '곤니치와'),       # Hiragana
    ('안녕',       '안녕'),         # Hangul (pass-through)
]

@pytest.mark.parametrize("text,expected", SCRIPT_ROUTING)
def test_script_routing(text, expected):
    out = transcribe_auto(text, strict=False)
    assert expected in out, f"{text!r} → {out!r}, expected {expected!r}"


# ============== Mixed-script (leak 0) ==============
def test_mixed_no_leak():
    """모든 입력 char가 한글/구두점/공백 안에 있어야 함."""
    cases = [
        'Hello 中国 5 apples',
        'I love 한국 & Japan',
        'COVID-19 (2024)',
        'A&B Corp. $100',
    ]
    for text in cases:
        out = transcribe_auto(text, strict=False)
        for ch in out:
            ok = (
                '가' <= ch <= '힣' or 'ㄱ' <= ch <= 'ㅎ' or 'ㅏ' <= ch <= 'ㅣ' or
                ch in ' .,!?;:"\'-()' or
                'ᄀ' <= ch <= 'ᇿ' or '㄰' <= ch <= '㆏' or
                ch in '·〮〯ːˑ¯↗↘↓¹²³⁴^_'
            )
            assert ok, f"Leak char {ch!r} in {out!r} from {text!r}"


# ============== Digit transliteration ==============
DIGIT_CASES = [
    ('5',     'sino', '오'),
    ('5',     'native', '다섯'),
    ('5',     'keep', '5'),
    ('100',   'sino', '일영영'),
    ('2024',  'sino', '이영이사'),
    ('5명',   'sino', '오명'),
]

@pytest.mark.parametrize("text,mode,expected", DIGIT_CASES)
def test_digits(text, mode, expected):
    out = transcribe_auto(text, digits=mode)
    assert expected in out, f"{text!r} digits={mode!r} → {out!r}, expected {expected!r}"


# ============== Symbol transliteration ==============
SYMBOL_CASES = [
    ('A & B',       'kor',   '앤드'),
    ('$100',        'kor',   '달러'),
    ('50%',         'kor',   '퍼센트'),
    ('cat@email',   'kor',   '앳'),
    ('a+b',         'kor',   '플러스'),
    ('A & B',       'drop',  '아  비'),  # double space (& dropped, spaces kept)
    ('A & B',       'keep',  '&'),
]

@pytest.mark.parametrize("text,mode,expected", SYMBOL_CASES)
def test_symbols(text, mode, expected):
    out = transcribe_auto(text, symbols=mode)
    assert expected in out, f"{text!r} symbols={mode!r} → {out!r}, expected {expected!r}"


# ============== Strict mode ==============
def test_strict_pass():
    """일반 입력은 strict=False 통과해야 함."""
    cases = [
        'Hello 中国 5',
        'Καλημέρα',
        'Hà Nội',
        'мерси',
        'COVID-19 50%',
    ]
    for c in cases:
        # 에러 없이 통과
        transcribe_auto(c, strict=False)


def test_strict_fails_on_unknown():
    """알 수 없는 emoji 등은 strict=True 시 ValueError."""
    with pytest.raises(ValueError):
        transcribe_auto('Hello 🔥 world', strict=True)


def test_strict_false_passes_through():
    """strict=False면 unknown char는 pass-through."""
    out = transcribe_auto('Hello 🔥 world', strict=False)
    assert '🔥' in out


# ============== Mode propagation ==============
def test_mode_uhps_core():
    """mode=UHPS_CORE면 옛한글 자모 사용."""
    out = transcribe_auto('father', mode=UHPS_CORE)
    # /f/ → ㆄ in UHPS-core
    assert 'ㆄ' in out, f'Expected ㆄ in {out!r}'


def test_mode_default_is_nikl():
    """mode 미지정 → HUNMIN_NIKL."""
    out_default = transcribe_auto('Hello')
    out_nikl = transcribe_auto('Hello', mode=HUNMIN_NIKL)
    assert out_default == out_nikl


# ============== CJK heuristic (ja vs zh) ==============
def test_cjk_with_kana_routes_japanese():
    """텍스트에 hiragana/katakana 있으면 한자 chunk도 ja로."""
    out = transcribe_auto('東京 はとても')
    # 東京 → 도쿄 (ja) not 둥징 (zh)
    assert '도쿄' in out


def test_cjk_only_routes_chinese():
    """한자만 있으면 zh로."""
    out = transcribe_auto('中国')
    assert '중궈' in out or '중국' in out  # zh transcription


# ============== Determinism ==============
def test_determinism():
    """Same input → same output (50 calls)."""
    text = 'Hello 中国 5 apples & Καλημέρα'
    first = transcribe_auto(text)
    for _ in range(49):
        out = transcribe_auto(text)
        assert out == first


# ============== Edge cases ==============
def test_empty_string():
    assert transcribe_auto('') == ''


def test_only_spaces():
    assert transcribe_auto('   ') == '   '


def test_only_digits():
    assert '오' in transcribe_auto('555', digits='sino')


def test_only_symbols():
    out = transcribe_auto('&&&', symbols='kor')
    assert '앤드' in out
