"""Hunmin Precise — Greek (el) Greek alphabet → Hangul.

NIKL 외래어 표기법 그리스어 핵심:
  - 24 letter alphabet, mostly phonetic
  - Modern Greek pronunciation 기준 (NOT classical)
  - 매핑:
      α/Α → 아, β/Β → 비 (현대: /v/), γ/Γ → 감마(어두), 그/그ㅎ
      δ/Δ → 델 (/ð/), ε/Ε → 에, ζ/Ζ → 자, η/Η → 이
      θ/Θ → 시 (/θ/), ι/Ι → 이, κ/Κ → 카, λ/Λ → 라
      μ/Μ → 미, ν/Ν → 니, ξ/Ξ → 크사, ο/Ο → 오
      π/Π → 피, ρ/Ρ → 로, σ/Σ → 시 / ς(어말) → 스
      τ/Τ → 타, υ/Υ → 이 (Modern), φ/Φ → 피, χ/Χ → 히
      ψ/Ψ → 프시, ω/Ω → 오
"""
import re

HANGUL_BASE = 0xAC00
INITIALS = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
            'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
VOWELS_J = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ',
            'ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
FINALS = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ',
          'ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
          'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


def _compose(cho, jung, jong=''):
    if cho in INITIALS and jung in VOWELS_J:
        c = INITIALS.index(cho)
        j = VOWELS_J.index(jung)
        f = FINALS.index(jong) if jong in FINALS else 0
        return chr(HANGUL_BASE + c*588 + j*28 + f)
    return cho + jung + jong


# 모음 (단모음 + 장모음 통합 — Modern Greek)
VOWEL_J = {
    'α':'ㅏ', 'ε':'ㅔ', 'η':'ㅣ', 'ι':'ㅣ',
    'ο':'ㅗ', 'υ':'ㅣ', 'ω':'ㅗ',
    # 강세 (tonos)
    'ά':'ㅏ', 'έ':'ㅔ', 'ή':'ㅣ', 'ί':'ㅣ',
    'ό':'ㅗ', 'ύ':'ㅣ', 'ώ':'ㅗ',
    # 'iota with diaeresis' — separate vowel
    'ϊ':'ㅣ', 'ϋ':'ㅣ', 'ΐ':'ㅣ', 'ΰ':'ㅣ',
}
VOWEL_LETTERS = set(VOWEL_J.keys())

# 자음 → 한글 cho
CONS_MAP = {
    'β':'ㅂ',  # Modern Greek /v/ — NIKL: ㅂ
    'γ':'ㄱ', 'δ':'ㄷ',
    'ζ':'ㅈ',  # /z/
    'θ':'ㅅ',  # /θ/ NIKL: ㅅ
    'κ':'ㅋ', 'λ':'ㄹ', 'μ':'ㅁ', 'ν':'ㄴ', 'ξ':'ㅋ',  # ξ → 크스
    'π':'ㅍ', 'ρ':'ㄹ', 'σ':'ㅅ', 'τ':'ㅌ',
    'φ':'ㅍ', 'χ':'ㅎ', 'ψ':'ㅍ',  # ψ → 프스
    'ς':'ㅅ',  # 어말 sigma
}

# Y_VOWEL for palatalized
Y_VOWEL = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}


def _phonemize(word, precise=False):
    """Greek word → list of hangul syllables (NIKL convention)."""
    s = word.lower()
    n = len(s)
    out = []
    i = 0
    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # 디그래프: αι→ㅔ, ει→ㅣ, οι→ㅣ, ου→ㅜ, υι→ㅣ
        di = c + nxt
        if di == 'αι' or di == 'άι' or di == 'αί':
            out.append(_compose('ㅇ', 'ㅔ'))
            i += 2; continue
        if di == 'ει' or di == 'έι' or di == 'εί':
            out.append(_compose('ㅇ', 'ㅣ'))
            i += 2; continue
        if di == 'οι' or di == 'όι' or di == 'οί':
            out.append(_compose('ㅇ', 'ㅣ'))
            i += 2; continue
        if di == 'ου' or di == 'όυ' or di == 'ού':
            out.append(_compose('ㅇ', 'ㅜ'))
            i += 2; continue
        if di == 'αυ' or di == 'άυ' or di == 'αύ':
            # αυ before voiceless → 아프, before voiced → 아브
            after = s[i+2] if i+2 < n else ''
            if after in 'πτκσφθχψξς':
                out.append(_compose('ㅇ', 'ㅏ'))
                out.append(_compose('ㅍ', 'ㅡ'))
            else:
                out.append(_compose('ㅇ', 'ㅏ'))
                out.append(_compose('ㅂ', 'ㅡ'))
            i += 2; continue
        if di == 'ευ' or di == 'έυ' or di == 'εύ':
            after = s[i+2] if i+2 < n else ''
            if after in 'πτκσφθχψξς':
                out.append(_compose('ㅇ', 'ㅔ'))
                out.append(_compose('ㅍ', 'ㅡ'))
            else:
                out.append(_compose('ㅇ', 'ㅔ'))
                out.append(_compose('ㅂ', 'ㅡ'))
            i += 2; continue

        # ng (γγ, γκ) → ㅇ받침 + g/k onset
        if c == 'γ' and nxt in ('γ', 'κ'):
            # 이전 syllable에 ㅇ받침 추가 (생략 — 단순화)
            cho_next = 'ㄱ' if nxt == 'γ' else 'ㅋ'
            after = s[i+2] if i+2 < n else ''
            if after in VOWEL_LETTERS:
                out.append(_compose(cho_next, VOWEL_J.get(after, 'ㅏ')))
                i += 3
            else:
                out.append(_compose(cho_next, 'ㅡ'))
                i += 2
            continue

        # 모음
        if c in VOWEL_J:
            out.append(_compose('ㅇ', VOWEL_J[c]))
            i += 1
            continue

        # 자음
        if c in CONS_MAP:
            cho = CONS_MAP[c]
            # ξ → 크 + 스 (special), ψ → 프 + 스
            if c == 'ξ':
                if nxt in VOWEL_LETTERS:
                    out.append(_compose('ㅋ', 'ㅡ'))
                    out.append(_compose('ㅅ', VOWEL_J[nxt]))
                    i += 2
                else:
                    out.append('크스')
                    i += 1
                continue
            if c == 'ψ':
                if nxt in VOWEL_LETTERS:
                    out.append(_compose('ㅍ', 'ㅡ'))
                    out.append(_compose('ㅅ', VOWEL_J[nxt]))
                    i += 2
                else:
                    out.append('프스')
                    i += 1
                continue
            # General
            if nxt in VOWEL_LETTERS:
                out.append(_compose(cho, VOWEL_J[nxt]))
                i += 2
                continue
            # 자음 + 자음 / end → 으-syllable 또는 받침
            if cho in ('ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ') and out:
                last = out[-1]
                if (len(last) == 1 and 0xAC00 <= ord(last) <= 0xD7A3
                    and (ord(last) - HANGUL_BASE) % 28 == 0):
                    base = ord(last) - HANGUL_BASE
                    cho_idx = base // 588
                    jung_idx = (base % 588) // 28
                    out[-1] = chr(HANGUL_BASE + cho_idx*588
                                  + jung_idx*28 + FINALS.index(cho))
                    i += 1
                    continue
            out.append(_compose(cho, 'ㅡ'))
            i += 1
            continue

        # Unknown
        out.append(c)
        i += 1

    return out


# 자주 쓰이는 그리스어 단어 NIKL override
_HANGUL_OVERRIDES = {
    'Αθήνα': '아테네', 'αθήνα': '아테네',
    'Θεσσαλονίκη': '테살로니키',
    'Πάτρα': '파트라',
    'Σπάρτη': '스파르타',
    'Ολυμπία': '올림피아',
    'Δελφοί': '델포이',
    'Κρήτη': '크레타',
    'Σαντορίνη': '산토리니',
    'Μύκονος': '미코노스',
    'Ρόδος': '로도스',
    # 인명 (역사/철학)
    'Σωκράτης': '소크라테스',
    'Πλάτων': '플라톤',
    'Αριστοτέλης': '아리스토텔레스',
    'Ομήρος': '호메로스',
    'Ευριπίδης': '에우리피데스',
    'Αλέξανδρος': '알렉산드로스',
    'Πυθαγόρας': '피타고라스',
    # 음식/문화
    'γύρος': '기로스',
    'σουβλάκι': '수블라키',
    'τζατζίκι': '차지키',
    'φέτα': '페타',
    'μουσακάς': '무사카',
    'ούζο': '우조',
    # 인사
    'γεια': '야',
    'καλημέρα': '칼리메라',
    'ευχαριστώ': '에프하리스토',
    'ναι': '네',
    'όχι': '오히',
}


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Greek text → Hangul (NIKL convention)."""
    parts = re.split(r'(\s+|[,.!?;:·;])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:·;]', part):
            out.append(part); continue
        if mode == 'hangul' and not precise and not phonetic and part in _HANGUL_OVERRIDES:
            out.append(_HANGUL_OVERRIDES[part])
            continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)


if __name__ == '__main__':
    samples = [
        ('Αθήνα', '아테네'),
        ('Θεσσαλονίκη', '테살로니키'),
        ('Σωκράτης', '소크라테스'),
        ('Πλάτων', '플라톤'),
        ('γύρος', '기로스'),
        ('φέτα', '페타'),
    ]
    for inp, exp in samples:
        r = transcribe(inp)
        ok = '✓' if r == exp else '✗'
        print(f'{ok} {inp:18} → {r:18} (expected: {exp})')
