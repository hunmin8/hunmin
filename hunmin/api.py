"""Hunmin public API — Hunmin class + transcribe() shortcut."""
from .core import (
    transcribe_es, transcribe_it, transcribe_de, transcribe_ru,
    transcribe_fr, transcribe_pt, transcribe_nl, transcribe_pl,
    transcribe_tr, transcribe_id, transcribe_en,
    transcribe_cjk,
)

# 11 Latin/Cyrillic langs use precise rule modules
_PRECISE = {
    'es': transcribe_es, 'it': transcribe_it, 'de': transcribe_de,
    'ru': transcribe_ru, 'fr': transcribe_fr, 'pt': transcribe_pt,
    'nl': transcribe_nl, 'pl': transcribe_pl, 'tr': transcribe_tr,
    'id': transcribe_id, 'en': transcribe_en,
}
# CJK uses v1 deterministic dict (requires pykakasi/pypinyin/hanja for ja/zh)
_DICT_LANGS = {'ja', 'zh', 'ko'}


class Hunmin:
    """Universal phonetic Hangul transcriber.

    Example:
        >>> h = Hunmin()
        >>> h.transcribe("student", "en")
        '스튜던트'
        >>> h.transcribe("student", "en", level=4)
        'ㅅㅌㅜㄷㅓㄴㅌ'
    """

    def __init__(self):
        pass

    def transcribe(self, text, lang, level=1):
        """Convert text to Hangul transcription.

        Args:
            text (str): Input text in the source language.
            lang (str): Language code (en, es, ja, zh, ko, ...).
            level (int): Output level (1-4).
                1: Children-friendly Hangul (default)
                2: Natural pronunciation
                3: Precise with old Hangul (ㆄ/ㅸ/ㅿ)
                4: UHPS jamo sequence

        Returns:
            str: Hangul or jamo transcription.
        """
        if level == 4:
            return self._jamo(text, lang)
        elif level == 3:
            return self._hangul(text, lang, precise=True)
        else:  # 1 or 2
            return self._hangul(text, lang, precise=False)

    def _hangul(self, text, lang, precise=False):
        if lang in _DICT_LANGS:
            return transcribe_cjk(text, lang, mode='hangul')
        elif lang in _PRECISE:
            return _PRECISE[lang](text, mode='hangul', precise=precise)
        else:
            raise ValueError(f"Unsupported lang: {lang!r}. Supported: {sorted(self.supported())}")

    def _jamo(self, text, lang):
        if lang in _DICT_LANGS:
            return transcribe_cjk(text, lang, mode='jamo')
        elif lang in _PRECISE:
            return _PRECISE[lang](text, mode='jamo', precise=True)
        else:
            raise ValueError(f"Unsupported lang: {lang!r}")

    def supported(self):
        """Return set of supported language codes."""
        return _DICT_LANGS | set(_PRECISE.keys())


# Module-level singleton
_default = Hunmin()


def transcribe(text, lang, level=1):
    """Convert text to Hangul transcription (uses default Hunmin instance).

    See Hunmin.transcribe for full docs.
    """
    return _default.transcribe(text, lang, level)


def supported_languages():
    """Return sorted list of supported language codes."""
    return sorted(_default.supported())
