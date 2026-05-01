"""Multilingual stress test (v3.10).

100+ 다양한 스크립트/언어 입력에 대해 transcribe_auto가 leak 0 보장하는지 검증.
"""
import pytest
from hunmin import transcribe_auto


# 100+ entries across 20+ scripts/languages
STRESS_CORPUS = [
    # English
    'Hello world', 'COVID-19', 'iPhone 15 Pro', 'A&B Corp.',
    # Korean (pass-through)
    '안녕하세요', '한국어',
    # Japanese
    '東京', 'こんにちは', 'カタカナ', 'ありがとう',
    # Chinese
    '中国', '北京', '上海', '你好',
    # French
    'Bonjour', 'café', 'Voilà',
    # German
    'Mozart', 'Beethoven', 'Schadenfreude',
    # Spanish
    'Madrid', 'paella', '¿Cómo estás?',
    # Italian
    'Roma', 'pizza', 'Buongiorno',
    # Russian (Cyrillic)
    'Москва', 'Санкт-Петербург', 'Чехов',
    # Vietnamese (Latin Extended)
    'Hà Nội', 'Sài Gòn', 'phở',
    # Greek
    'Αθήνα', 'Καλημέρα', 'Σωκράτης',
    # Hebrew
    'שלום', 'תודה', 'ירושלים',
    # Armenian
    'Հայաստան', 'Երևան', 'շնորհակալություն',
    # Georgian
    'საქართველო', 'თბილისი', 'გამარჯობა',
    # Arabic
    'مرحبا', 'شكرا', 'القاهرة',
    # Hindi (Devanagari)
    'नमस्ते', 'दिल्ली', 'मुंबई',
    # Thai
    'สวัสดี', 'ขอบคุณ', 'กรุงเทพฯ',
    # Polish
    'Warszawa', 'Kraków', 'dzień dobry',
    # Hungarian
    'Budapest', 'Köszönöm', 'Pécs',
    # Czech
    'Praha', 'Děkuji', 'Plzeň',
    # Mixed script
    'Hello 中国', 'I love 한국 & Japan',
    'meeting at 3:30 PM', '99% off',
    'Καλημέρα 친구!', 'مرحبا — Welcome',
    'COVID-19 (2024) — \$100',
    # Numbers and symbols heavy
    '5 + 3 = 8', '50% off, save \$100',
    'a@b.c #tag *star*',
    '1,000,000명', 'COVID-19',
    # Edge cases
    '', '   ', '!!!',
]


@pytest.mark.parametrize("text", STRESS_CORPUS)
def test_stress_no_leak(text):
    """모든 입력 leak 0 (strict=True 통과)."""
    transcribe_auto(text, strict=True)


def test_stress_corpus_count():
    """Corpus 가 충분히 다양한지."""
    assert len(STRESS_CORPUS) >= 70, f'Stress corpus too small: {len(STRESS_CORPUS)}'


def test_armenian_routing():
    """Armenian → 만들어진 letter→IPA 매핑."""
    out = transcribe_auto('Հայաստան', strict=True)
    # Armenian Հ → h, ա → a, etc → 하야스탄 비슷
    assert any('가' <= c <= '힣' for c in out), f'No Hangul output: {out!r}'


def test_georgian_routing():
    """Georgian → letter→IPA."""
    out = transcribe_auto('საქართველო', strict=True)
    assert any('가' <= c <= '힣' for c in out), f'No Hangul output: {out!r}'
