"""Property-based tests using hypothesis.

전형적 unit test가 놓치는 edge case를 random input으로 발견.

Run:
    pip install hypothesis
    pytest tests/test_properties.py -v
"""
import pytest

try:
    from hypothesis import given, strategies as st, settings, HealthCheck
except ImportError:
    pytest.skip("hypothesis not installed", allow_module_level=True)

from hunmin import (
    transcribe, views, supported_languages,
    transcribe_cache_clear, hangul_to_rr, hangul_to_ipa,
)


# === 전제: 입력 strategies ===
SUPPORTED_LANGS = ['en', 'es', 'it', 'de', 'fr', 'pt', 'nl', 'pl',
                   'tr', 'id', 'hu', 'cs', 'sk', 'ro', 'hr', 'sr',
                   'vi', 'fa', 'ru', 'ja', 'zh']

# 안전한 ASCII letter inputs
ascii_word = st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu')),
                     min_size=1, max_size=20)


# === Properties ===

@given(text=ascii_word, lang=st.sampled_from(SUPPORTED_LANGS))
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_transcribe_returns_str(text, lang):
    """transcribe()는 항상 str을 반환."""
    result = transcribe(text, lang)
    assert isinstance(result, str)


@given(text=ascii_word, lang=st.sampled_from(SUPPORTED_LANGS))
@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
def test_transcribe_idempotent(text, lang):
    """같은 입력은 항상 같은 출력 (deterministic)."""
    r1 = transcribe(text, lang)
    r2 = transcribe(text, lang)
    assert r1 == r2


@given(text=ascii_word, lang=st.sampled_from(SUPPORTED_LANGS))
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_no_crash(text, lang):
    """모든 ASCII letter 입력에서 crash 없음."""
    try:
        transcribe(text, lang)
    except (ImportError, ValueError):
        pass  # known errors OK


@given(text=ascii_word.filter(lambda s: len(s) > 0))
@settings(max_examples=50)
def test_cache_consistency(text):
    """cache=True와 cache=False 결과 동일."""
    transcribe_cache_clear()
    r_cached = transcribe(text, 'en', cache=True)
    r_uncached = transcribe(text, 'en', cache=False)
    assert r_cached == r_uncached


@given(text=st.text(min_size=0, max_size=100))
@settings(max_examples=50)
def test_no_crash_arbitrary_text(text):
    """임의의 Unicode text도 crash 없이 처리."""
    try:
        transcribe(text, 'en')
    except (ImportError, ValueError, TypeError):
        pass


# === Type validation ===
@given(text=st.one_of(st.none(), st.integers(), st.booleans(),
                       st.lists(st.integers()), st.dictionaries(st.text(), st.text())))
def test_invalid_text_type(text):
    """non-str text → TypeError."""
    with pytest.raises(TypeError):
        transcribe(text, 'en')


# === Reverse properties ===
hangul_text = st.text(
    alphabet=st.characters(min_codepoint=0xAC00, max_codepoint=0xD7A3),
    min_size=1, max_size=10,
)


@given(text=hangul_text)
@settings(max_examples=100)
def test_reverse_returns_str(text):
    """to_romanization → str."""
    assert isinstance(hangul_to_rr(text), str)
    assert isinstance(hangul_to_ipa(text), str)


@given(text=hangul_text)
@settings(max_examples=100)
def test_reverse_no_korean_chars(text):
    """RR 출력은 ASCII만 (Korean 문자 없어야)."""
    rr = hangul_to_rr(text)
    for c in rr:
        # RR uses only ASCII letters
        assert ord(c) < 256, f'Non-ASCII char in RR output: {c!r}'


# === Supported languages는 항상 존재 ===
def test_supported_langs_nonempty():
    s = supported_languages('hardcoded')
    assert len(s) >= 20


# === Idempotency on repeated calls ===
@given(text=ascii_word, n=st.integers(min_value=1, max_value=10))
@settings(max_examples=20)
def test_repeated_calls_same(text, n):
    """N번 반복 호출 결과 모두 동일."""
    results = [transcribe(text, 'en') for _ in range(n)]
    assert all(r == results[0] for r in results)


# === views() 항상 dict ===
@given(text=ascii_word, lang=st.sampled_from(['en', 'fr', 'de', 'es']))
@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
def test_views_returns_dict(text, lang):
    """views()는 dict 반환."""
    v = views(text, lang)
    assert isinstance(v, dict)
    assert 'text' in v


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
