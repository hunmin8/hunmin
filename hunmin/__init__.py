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

__version__ = '2.4.3'
__author__ = 'Hunmin Project'

from .api import Hunmin, transcribe, supported_languages

__all__ = ['Hunmin', 'transcribe', 'supported_languages', '__version__']
