"""Hunmin — Universal phonetic Hangul transcription system.

Convert any language's pronunciation into readable Korean Hangul.

Quick start:
    >>> from hunmin import transcribe
    >>> transcribe("student", lang="en")
    '스튜던트'
    >>> transcribe("中国", lang="zh", level=4)
    'ㅈㅜㅇㄱㅜㅓ'
    >>> transcribe("familia", lang="es", level=3)
    'ㆄ아밀리아'

Levels:
  1 (default): Children-friendly Hangul
  2: Natural pronunciation (currently same as 1)
  3: Precise with old Hangul (ㆄ for /f/, ㅸ for /v/, ㅿ for /z/)
  4: UHPS jamo sequence (for ML / research)

Supported languages (14):
  Latin/Cyrillic (rule-based):
    en, es, it, de, ru, fr, pt, nl, pl, tr, id
  CJK (dictionary-based via v1):
    ja, zh, ko
"""

__version__ = '3.44.1'
__author__ = 'Hunmin Project'

from .api import (
    Hunmin, transcribe, transcribe_batch, atranscribe, atranscribe_batch,
    views, supported_languages,
    transcribe_cache_info, transcribe_cache_clear,
    HUNMIN_NIKL, HUNMIN_PHONETIC, UHPS_CORE, UHPS_JAMO, UHPS_FULL,
)
from .auto import transcribe_auto
from .reverse import to_romanization, hangul_to_ipa, hangul_to_rr
from .entity import PhoneticEntityIndex, Entity, EntityMatch

__all__ = [
    'Hunmin', 'transcribe', 'transcribe_batch',
    'atranscribe', 'atranscribe_batch',
    'transcribe_auto', 'views',
    'supported_languages', '__version__',
    'transcribe_cache_info', 'transcribe_cache_clear',
    'to_romanization', 'hangul_to_ipa', 'hangul_to_rr',
    'PhoneticEntityIndex', 'Entity', 'EntityMatch',
    'HUNMIN_NIKL', 'HUNMIN_PHONETIC', 'UHPS_CORE', 'UHPS_JAMO', 'UHPS_FULL',
]
