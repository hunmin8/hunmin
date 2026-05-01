"""UHPS Spec compliance test (v3.2).

Verifies that the implementation matches UHPS_SPEC.md §3 (mapping table) and §4 (mergers).
This is THE meaningful accuracy metric for hunmin — not NIKL conformance.

Run: pytest tests/test_uhps_spec.py -v
"""
import pytest
from hunmin import transcribe


# ============== §3 IPA → UHPS phoneme mapping ==============
# 각 단일 IPA → 단일 UHPS jamo (token kind + value)
# 'V' / 'C' / 'OLD' kind 구분 무시 — value만 검증

PHONEME_TABLE = [
    # === §3.1 Plosives ===
    ('p', 'ㅍ'), ('b', 'ㅂ'),
    ('t', 'ㅌ'), ('d', 'ㄷ'),
    ('k', 'ㅋ'), ('ɡ', 'ㄱ'), ('g', 'ㄱ'),
    ('q', 'ㅋ'),       # merger #1: q → k
    ('ʔ', 'ㆆ'),
    # === §3.2 Nasals ===
    ('m', 'ㅁ'), ('n', 'ㄴ'),
    ('ɲ', 'ㅥ'),
    ('ŋ', 'ㆁ'),
    ('ɴ', 'ㆁ'),       # merger #3
    ('ɱ', 'ㅱ'),
    # === §3.3 Fricatives ===
    ('f', 'ㆄ'), ('v', 'ㅸ'),
    ('ɸ', 'ㆄ'), ('β', 'ㅸ'),  # merger #4
    ('s', 'ㅅ'), ('z', 'ㅿ'),
    ('θ', 'ㅼ'), ('ð', 'ㅽ'),
    ('ʃ', 'ᄾ'), ('ʒ', 'ᄶ'),
    ('ɕ', 'ᄾ'), ('ʑ', 'ᄶ'),  # merger #5
    ('ʂ', 'ᄾ'), ('ʐ', 'ᄶ'),  # merger #5
    ('h', 'ㅎ'), ('ɦ', 'ㅎ'),
    ('x', 'ㆅ'),
    ('ɣ', 'ㆅ'),       # merger #6
    ('ç', 'ㆅ'),       # merger #6
    ('χ', 'ㆅ'),       # merger #6
    ('ħ', 'ㆅ'),       # merger #6
    ('ʁ', 'ᄛ'), ('ʀ', 'ᄛ'),
    # === §3.5 Liquids/glides — multi-phoneme contexts; skip single-token check ===
    # === §3.6 Vowels (front) ===
    ('i', 'ㅣ'), ('ɪ', 'ㅣ'),    # merger #10
    ('e', 'ㅔ'), ('ɛ', 'ㅔ'),
    ('æ', 'ㅐ'),
    ('a', 'ㅏ'), ('ɐ', 'ㅏ'),
    ('ə', 'ㅓ'), ('ɵ', 'ㅓ'), ('ʌ', 'ㅓ'),
    ('ɨ', 'ㅡ'), ('ʉ', 'ㅡ'), ('ɯ', 'ㅡ'),
    ('u', 'ㅜ'), ('ʊ', 'ㅜ'),    # merger #10
    ('o', 'ㅗ'),
    ('ɔ', 'ㆎ'), ('ɑ', 'ㆍ'), ('ɒ', 'ㆍ'),
    # === §3.7 Front rounded ===
    ('y', 'ㅟ'), ('ʏ', 'ㅟ'),
    ('ø', 'ㅚ'), ('œ', 'ㅙ'),
]


# ============== §4 Intentional Mergers — verify same output ==============
INTENTIONAL_MERGERS = [
    # (a, b, expected_shared_value, comment)
    ('ʃ', 'ɕ', 'ᄾ', 'merger #5: alveolo-palatal ≡ post-alveolar'),
    ('ʃ', 'ʂ', 'ᄾ', 'merger #5: retroflex ≡ post-alveolar'),
    ('ç', 'ħ', 'ㆅ', 'merger #6: palatal ≡ pharyngeal "강한 ㅎ"'),
    ('x', 'χ', 'ㆅ', 'merger #6: velar ≡ uvular'),
    ('q', 'k', 'ㅋ', 'merger #1: uvular k ≡ velar k'),
    ('ɴ', 'ŋ', 'ㆁ', 'merger #3: uvular n ≡ velar n'),
    ('ɸ', 'f', 'ㆄ', 'merger #4: bilabial ≡ labiodental f'),
    ('β', 'v', 'ㅸ', 'merger #4: bilabial ≡ labiodental v'),
    ('i', 'ɪ', 'ㅣ', 'merger #10: tense ≡ lax i'),
    ('u', 'ʊ', 'ㅜ', 'merger #10: tense ≡ lax u'),
]


# ============== §3.4 Affricates (digraph) ==============
AFFRICATE_TABLE = [
    ('tʃ', 'ㅊ'), ('dʒ', 'ㅈ'),
    ('t͡ʃ', 'ㅊ'), ('d͡ʒ', 'ㅈ'),
    ('tɕ', 'ㅊ'), ('dʑ', 'ㅈ'),
    ('t͡ɕ', 'ㅊ'), ('d͡ʑ', 'ㅈ'),
    ('tʂ', 'ㅊ'), ('dʐ', 'ㅈ'),
    ('ʈʂ', 'ㅊ'), ('ɖʐ', 'ㅈ'),
    ('ʈ͡ʂ', 'ㅊ'), ('ɖ͡ʐ', 'ㅈ'),
    ('ts', 'ㅊ'), ('dz', 'ㅈ'),
    ('t͡s', 'ㅊ'), ('d͡z', 'ㅈ'),
]


# ============== Helpers ==============
def get_first_phoneme_value(ipa, level=3):
    """Return the value of first non-SUPRA token."""
    toks = transcribe(ipa, 'ipa', level=level, return_tokens=True)
    for t in toks:
        if t[0] not in ('SUPRA', 'SPACE', 'PUNCT', 'SV_MARKER'):
            return t[1]
    return None


# ============== TESTS ==============
@pytest.mark.parametrize("ipa,expected", PHONEME_TABLE)
def test_phoneme_mapping(ipa, expected):
    """§3: each IPA single phoneme → expected UHPS jamo."""
    out = get_first_phoneme_value(ipa)
    assert out == expected, f"{ipa!r} → {out!r}, expected {expected!r}"


@pytest.mark.parametrize("ipa,expected", AFFRICATE_TABLE)
def test_affricate(ipa, expected):
    """§3.4: affricates (with/without tie bar)."""
    out = get_first_phoneme_value(ipa)
    assert out == expected, f"{ipa!r} → {out!r}, expected {expected!r}"


@pytest.mark.parametrize("a,b,expected,note", INTENTIONAL_MERGERS)
def test_intentional_merger(a, b, expected, note):
    """§4: intentional mergers — both IPA must produce same UHPS jamo."""
    out_a = get_first_phoneme_value(a)
    out_b = get_first_phoneme_value(b)
    assert out_a == out_b == expected, \
        f"{note}: {a!r}→{out_a!r}, {b!r}→{out_b!r}, expected {expected!r}"


def test_determinism():
    """Same input → same output (100 calls)."""
    inputs = ['həˈloʊ', 'bɔ̃ʒuʁ', 'ʈʂʊŋ˥', 'sin t͡ɕaːw', 'ˈfɑːðɚ']
    for ipa in inputs:
        first = transcribe(ipa, 'ipa', level=5, return_tokens=True)
        for _ in range(99):
            out = transcribe(ipa, 'ipa', level=5, return_tokens=True)
            assert out == first, f"Non-deterministic on {ipa!r}"


def test_level5_includes_supra():
    """level=5 must include SUPRA tokens for stress/tone/length."""
    toks = transcribe('həˈloʊ', 'ipa', level=5, return_tokens=True)
    kinds = [t[0] for t in toks]
    assert 'SUPRA' in kinds, "Level 5 missing SUPRA (stress)"


def test_level3_no_supra():
    """level=3 must NOT include SUPRA tokens (UHPS-core, no suprasegmental)."""
    toks = transcribe('həˈloʊ', 'ipa', level=3, return_tokens=True)
    kinds = [t[0] for t in toks]
    assert 'SUPRA' not in kinds, "Level 3 should not have SUPRA"


def test_tone_distinct_4_mandarin():
    """§5: Mandarin 4성 must be distinguishable in UHPS-full."""
    ma1 = transcribe('ma˥', 'ipa', level=5)
    ma2 = transcribe('ma˧˥', 'ipa', level=5)
    ma3 = transcribe('ma˨˩˦', 'ipa', level=5)
    ma4 = transcribe('ma˥˩', 'ipa', level=5)
    # In `arrow` style (most distinct), all 4 should differ
    from hunmin.core.universal import transcribe_universal
    out = [transcribe_universal(f'ma{bar}', 'ipa', uhps='full', tone_style='arrow')
           for bar in ('˥', '˧˥', '˨˩˦', '˥˩')]
    assert len(set(out)) == 4, f"Mandarin 4 tones must differ (arrow style): {out}"


def test_vietnamese_tones():
    """Vietnamese: NFD-decomposed combining marks → 4 distinct tones."""
    from hunmin.core.universal import transcribe_universal
    out = {label: transcribe_universal(ipa, 'ipa', uhps='full', tone_style='arrow')
           for label, ipa in [('sắc','á'), ('huyền','à'), ('hỏi','ả'), ('nặng','ạ')]}
    # All 4 should produce different outputs
    assert len(set(out.values())) == 4, f"VN 4 tones must differ: {out}"


def test_old_jamo_preserved_in_level3():
    """level=3 must preserve old jamo tokens (OLD kind)."""
    toks = transcribe('θɪŋk', 'ipa', level=3, return_tokens=True)
    # θ → OLD ㅼ should be present
    found = [t for t in toks if t == ('OLD', 'ㅼ')]
    assert found, f"θ should produce ('OLD', 'ㅼ') token, got {toks}"
