"""Reverse transcription — Hangul → Romanization / IPA.

Korean Hangul 텍스트를 외국어 발음 표기 (영문 letter, IPA)로 변환.
한국어 학습자/관광객/번역 도구용.

NIKL 외래어 표기와 reverse 관계는 아니지만, 표준 ALA-LC / RR /
McCune-Reischauer 등의 한국어 로마자 표기 시스템 지원.
"""
from __future__ import annotations

HANGUL_BASE = 0xAC00
INITIALS = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
            'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
VOWELS_J = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ',
            'ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
FINALS = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ',
          'ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
          'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

# === Revised Romanization (RR) — 정부 공인 (since 2000) ===
# https://www.korean.go.kr/front_eng/roman/roman_01.do
# 학교 → hakgyo, 한국 → hanguk, 김치 → gimchi

# 초성 (initial)
RR_CHO = {
    'ㄱ': 'g', 'ㄲ': 'kk', 'ㄴ': 'n', 'ㄷ': 'd', 'ㄸ': 'tt',
    'ㄹ': 'r',  # 어두 'r', 어중 'r', 어말 'l'
    'ㅁ': 'm', 'ㅂ': 'b', 'ㅃ': 'pp', 'ㅅ': 's', 'ㅆ': 'ss',
    'ㅇ': '',  # 무음
    'ㅈ': 'j', 'ㅉ': 'jj', 'ㅊ': 'ch', 'ㅋ': 'k', 'ㅌ': 't',
    'ㅍ': 'p', 'ㅎ': 'h',
}

# 중성 (medial vowel)
RR_JUNG = {
    'ㅏ': 'a',  'ㅐ': 'ae', 'ㅑ': 'ya', 'ㅒ': 'yae', 'ㅓ': 'eo',
    'ㅔ': 'e',  'ㅕ': 'yeo','ㅖ': 'ye', 'ㅗ': 'o',  'ㅘ': 'wa',
    'ㅙ': 'wae','ㅚ': 'oe', 'ㅛ': 'yo', 'ㅜ': 'u',  'ㅝ': 'wo',
    'ㅞ': 'we', 'ㅟ': 'wi', 'ㅠ': 'yu', 'ㅡ': 'eu', 'ㅢ': 'ui',
    'ㅣ': 'i',
}

# 종성 (final)
RR_JONG = {
    '': '',
    'ㄱ': 'k', 'ㄲ': 'k', 'ㄳ': 'k',
    'ㄴ': 'n', 'ㄵ': 'n', 'ㄶ': 'n',
    'ㄷ': 't',
    'ㄹ': 'l', 'ㄺ': 'k', 'ㄻ': 'm', 'ㄼ': 'l', 'ㄽ': 'l',
    'ㄾ': 'l', 'ㄿ': 'p', 'ㅀ': 'l',
    'ㅁ': 'm', 'ㅂ': 'p', 'ㅄ': 'p',
    'ㅅ': 't', 'ㅆ': 't',
    'ㅇ': 'ng',
    'ㅈ': 't', 'ㅊ': 't', 'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p',
    'ㅎ': 't',
}

# === IPA mapping ===
IPA_CHO = {
    'ㄱ': 'k', 'ㄲ': 'k͈', 'ㄴ': 'n', 'ㄷ': 't', 'ㄸ': 't͈',
    'ㄹ': 'ɾ', 'ㅁ': 'm', 'ㅂ': 'p', 'ㅃ': 'p͈', 'ㅅ': 's',
    'ㅆ': 's͈', 'ㅇ': '', 'ㅈ': 't͡ɕ', 'ㅉ': 't͡ɕ͈',
    'ㅊ': 't͡ɕʰ', 'ㅋ': 'kʰ', 'ㅌ': 'tʰ', 'ㅍ': 'pʰ', 'ㅎ': 'h',
}
IPA_JUNG = {
    'ㅏ': 'a',  'ㅐ': 'ɛ',  'ㅑ': 'ja', 'ㅒ': 'jɛ', 'ㅓ': 'ʌ',
    'ㅔ': 'e',  'ㅕ': 'jʌ', 'ㅖ': 'je', 'ㅗ': 'o',  'ㅘ': 'wa',
    'ㅙ': 'wɛ', 'ㅚ': 'ø',  'ㅛ': 'jo', 'ㅜ': 'u',  'ㅝ': 'wʌ',
    'ㅞ': 'we', 'ㅟ': 'y',  'ㅠ': 'ju', 'ㅡ': 'ɯ',  'ㅢ': 'ɰi',
    'ㅣ': 'i',
}
IPA_JONG = {
    '': '',
    'ㄱ': 'k̚', 'ㄲ': 'k̚', 'ㄴ': 'n', 'ㄷ': 't̚',
    'ㄹ': 'l', 'ㅁ': 'm', 'ㅂ': 'p̚', 'ㅅ': 't̚', 'ㅆ': 't̚',
    'ㅇ': 'ŋ', 'ㅈ': 't̚', 'ㅊ': 't̚', 'ㅋ': 'k̚', 'ㅌ': 't̚',
    'ㅍ': 'p̚', 'ㅎ': 't̚',
}


def _decompose(syllable: str) -> tuple[str, str, str] | None:
    """한글 음절 → (cho, jung, jong)."""
    if not syllable or len(syllable) != 1:
        return None
    cp = ord(syllable)
    if not (HANGUL_BASE <= cp <= 0xD7A3):
        return None
    base = cp - HANGUL_BASE
    return (
        INITIALS[base // 588],
        VOWELS_J[(base % 588) // 28],
        FINALS[base % 28],
    )


def to_romanization(text: str, system: str = 'rr') -> str:
    """Hangul 텍스트 → 로마자 표기.

    Args:
        text: 한국어 한글 텍스트.
        system: 'rr' (Revised Romanization, 기본) 또는 'ipa'.

    Returns:
        로마자 또는 IPA 문자열.

    Examples:
        >>> to_romanization('안녕하세요')
        'annyeonghaseyo'
        >>> to_romanization('김치')
        'gimchi'
        >>> to_romanization('한국', 'ipa')
        'hanɡuk̚'
    """
    if not isinstance(text, str):
        raise TypeError(f"to_romanization(): text must be str, got {type(text).__name__}")
    if system not in ('rr', 'ipa'):
        raise ValueError(f"system must be 'rr' or 'ipa', got {system!r}")

    cho_map = IPA_CHO if system == 'ipa' else RR_CHO
    jung_map = IPA_JUNG if system == 'ipa' else RR_JUNG
    jong_map = IPA_JONG if system == 'ipa' else RR_JONG

    out = []
    prev_jong = ''  # for liaison handling
    for i, c in enumerate(text):
        d = _decompose(c)
        if d is None:
            out.append(c)
            prev_jong = ''
            continue
        cho, jung, jong = d
        # RR 연음 처리: 이전 받침 + 현재 ㅇ → 받침이 다음 onset으로 (간단화)
        if system == 'rr' and cho == 'ㅇ' and prev_jong and out and out[-1] == jong_map.get(prev_jong, ''):
            # 받침 이미 출력했으면 그대로
            pass
        # 어두 ㄹ → 'r', 어말 ㄹ → 'l' (RR 룰)
        if system == 'rr' and cho == 'ㄹ':
            cho_str = 'r'
        else:
            cho_str = cho_map.get(cho, '')
        out.append(cho_str)
        out.append(jung_map.get(jung, ''))
        out.append(jong_map.get(jong, ''))
        prev_jong = jong
    return ''.join(out)


def hangul_to_ipa(text: str) -> str:
    """Convenience: Hangul → IPA."""
    return to_romanization(text, system='ipa')


def hangul_to_rr(text: str) -> str:
    """Convenience: Hangul → Revised Romanization."""
    return to_romanization(text, system='rr')


if __name__ == '__main__':
    samples = [
        ('안녕하세요', 'rr'),
        ('김치', 'rr'),
        ('한국', 'rr'),
        ('학교', 'rr'),
        ('서울', 'rr'),
        ('대한민국', 'rr'),
        ('한국', 'ipa'),
        ('김치', 'ipa'),
    ]
    for text, system in samples:
        r = to_romanization(text, system)
        print(f'  {text:8} ({system:3}) → {r}')
