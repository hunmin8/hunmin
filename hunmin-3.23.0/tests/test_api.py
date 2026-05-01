"""API surface tests — Hunmin class, transcribe(), edge cases."""
import pytest
from hunmin import transcribe, Hunmin, supported_languages, __version__


def test_version():
    assert isinstance(__version__, str)
    assert __version__.count('.') >= 2  # major.minor.patch


def test_class_singleton():
    h = Hunmin()
    assert h.transcribe('student', 'en') == '스튜던트'


def test_invalid_lang_raises():
    with pytest.raises(ValueError):
        transcribe('test', 'xx')


def test_empty_string():
    # Should not crash
    out = transcribe('', 'en')
    assert isinstance(out, str)


def test_punctuation_preserved():
    # Punctuation should pass through
    out = transcribe('hello, world!', 'en')
    assert ',' in out and '!' in out


def test_multiword_sentence():
    out = transcribe('I love LSTM', 'en')
    assert '엘에스티엠' in out  # acronym in sentence


def test_levels_dispatched():
    # Each level should produce different output for words with /f/
    l1 = transcribe('father', 'en', level=1)
    l3 = transcribe('father', 'en', level=3)
    l4 = transcribe('father', 'en', level=4)
    assert l1 != l3  # L3 uses Old Hangul
    assert l3 != l4  # L4 is jamo seq
