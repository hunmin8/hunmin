"""Hunmin Precise — Hindi (hi) Devanagari → Hangul.

NIKL 외래어 표기법 힌디어 핵심:
  - Devanagari 자모는 음가가 거의 1:1로 한글에 매핑됨
  - 모음: अ→아, आ→아, इ→이, ई→이, उ→우, ऊ→우, ऋ→리, ए→에, ऐ→아이, ओ→오, औ→아우
  - 자음: क→ㅋ, ख→ㅋ, ग→ㄱ, घ→ㄱ, च→ㅊ, ज→ㅈ, झ→ㅈ, ट→ㅌ, ड→ㄷ, ण→ㄴ
  - 모음 부호 (matra): 자음 + matra → 한 음절
  - 비르라마 (्): 자음 단독 (다음 자음에 연결, 한국식 받침)
  - aspirate (kh, gh 등): NIKL 동일 처리 (ㅋ/ㄱ로)
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


# Devanagari independent vowels → 한글
VOWEL_INDEP = {
    'अ': 'ㅏ',  # a (schwa)
    'आ': 'ㅏ',  # ā (long)
    'इ': 'ㅣ',  # i
    'ई': 'ㅣ',  # ī
    'उ': 'ㅜ',  # u
    'ऊ': 'ㅜ',  # ū
    'ऋ': 'ㅣ',  # ri (special, NIKL: 리 like)
    'ए': 'ㅔ',  # e
    'ऐ': None,  # ai → 아이 (split)
    'ओ': 'ㅗ',  # o
    'औ': None,  # au → 아우 (split)
    'अं': None, # aṃ → 앙 (nasalized)
    'अः': 'ㅏ', # aḥ
}

# Devanagari vowel signs (matra) → 모음 (자음 뒤)
VOWEL_MATRA = {
    'ा': 'ㅏ',
    'ि': 'ㅣ',
    'ी': 'ㅣ',
    'ु': 'ㅜ',
    'ू': 'ㅜ',
    'ृ': 'ㅣ',  # ri
    'े': 'ㅔ',
    'ै': None,  # ai → vowel + ㅣ
    'ो': 'ㅗ',
    'ौ': None,  # au → vowel + ㅜ
}

# Devanagari consonants → cho jamo
CONSONANT = {
    # 가-ष velar/palatal/retroflex/dental/labial
    'क': 'ㅋ', 'ख': 'ㅋ', 'ग': 'ㄱ', 'घ': 'ㄱ', 'ङ': 'ㅇ',
    'च': 'ㅊ', 'छ': 'ㅊ', 'ज': 'ㅈ', 'झ': 'ㅈ', 'ञ': 'ㄴ',
    'ट': 'ㅌ', 'ठ': 'ㅌ', 'ड': 'ㄷ', 'ढ': 'ㄷ', 'ण': 'ㄴ',
    'त': 'ㅌ', 'थ': 'ㅌ', 'द': 'ㄷ', 'ध': 'ㄷ', 'न': 'ㄴ',
    'प': 'ㅍ', 'फ': 'ㅍ', 'ब': 'ㅂ', 'भ': 'ㅂ', 'म': 'ㅁ',
    # 반모음/마찰음/유음
    'य': 'ㅇ',  # ya — 'ㅇ + 야'
    'र': 'ㄹ',
    'ल': 'ㄹ',
    'व': 'ㅂ',  # va (or 와 in some contexts)
    'श': 'ㅅ',  # śa (palatal sh)
    'ष': 'ㅅ',  # ṣa (retroflex sh)
    'स': 'ㅅ',
    'ह': 'ㅎ',
    # 추가 borrowed
    'क़': 'ㅋ',  # qa (Persian-Arabic loan)
    'ख़': 'ㅋ',  # khā
    'ग़': 'ㄱ',  # gha
    'ज़': 'ㅈ',  # za
    'फ़': 'ㅍ',  # fa
    'ड़': 'ㄷ',  # ḍa
    'ढ़': 'ㄷ',  # ḍha
}

# 'ya' palatal → ㅑ/ㅖ etc. with 'य' before vowel
Y_VOWEL = {
    'ㅏ': 'ㅑ', 'ㅔ': 'ㅖ', 'ㅗ': 'ㅛ', 'ㅜ': 'ㅠ', 'ㅣ': 'ㅣ',
}

VIRAMA = '्'  # halant — kills inherent 'a'
ANUSVARA = 'ं'  # nasalization → ㅇ받침
VISARGA = 'ः'  # voiceless h-like aspiration


def _phonemize(word, precise=False):
    """Devanagari word → list of hangul syllables."""
    s = word
    n = len(s)
    out = []
    i = 0
    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''
        nxt2 = s[i+2] if i+2 < n else ''

        # Independent vowel
        if c in VOWEL_INDEP:
            v = VOWEL_INDEP[c]
            if v is None:  # diphthongs
                if c == 'ऐ':
                    out.append(_compose('ㅇ', 'ㅏ'))
                    out.append(_compose('ㅇ', 'ㅣ'))
                elif c == 'औ':
                    out.append(_compose('ㅇ', 'ㅏ'))
                    out.append(_compose('ㅇ', 'ㅜ'))
                elif c == 'अं':
                    out.append(_compose('ㅇ', 'ㅏ', 'ㅇ'))
            else:
                out.append(_compose('ㅇ', v))
            i += 1
            continue

        # Consonant
        if c in CONSONANT:
            cho = CONSONANT[c]
            # Look for following matra/virama/vowel
            if nxt == VIRAMA:
                # Conjunct — no inherent 'a'. Append as 받침 to last? 또는 다음 자음 onset.
                # NIKL: virama 자음 → 받침으로 흡수 시도
                # 단순화: 그대로 jamo (다음에 vowel/cons 처리)
                if cho in ('ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ') and out:
                    last = out[-1]
                    if (len(last) == 1 and 0xAC00 <= ord(last) <= 0xD7A3
                        and (ord(last) - HANGUL_BASE) % 28 == 0
                        and cho in FINALS):
                        # add 받침
                        base = ord(last) - HANGUL_BASE
                        cho_idx = base // 588
                        jung_idx = (base % 588) // 28
                        out[-1] = chr(HANGUL_BASE + cho_idx*588
                                      + jung_idx*28 + FINALS.index(cho))
                        i += 2
                        continue
                # 받침 흡수 못 하면 자음 + ㅡ syllable
                out.append(_compose(cho, 'ㅡ'))
                i += 2
                continue
            if nxt in VOWEL_MATRA:
                vsign = VOWEL_MATRA[nxt]
                if vsign is None:
                    # ai/au → vowel + extra
                    if nxt == 'ै':
                        out.append(_compose(cho, 'ㅏ'))
                        out.append(_compose('ㅇ', 'ㅣ'))
                    elif nxt == 'ौ':
                        out.append(_compose(cho, 'ㅏ'))
                        out.append(_compose('ㅇ', 'ㅜ'))
                else:
                    # 'य' (ya) palatal: applies palatal vowel
                    if c == 'य' and vsign in Y_VOWEL:
                        out.append(_compose('ㅇ', Y_VOWEL[vsign]))
                    else:
                        out.append(_compose(cho, vsign))
                # Check for anusvara
                after = s[i+2] if i+2 < n else ''
                if after == ANUSVARA:
                    # add ㅇ받침
                    last = out[-1]
                    if len(last) == 1 and 0xAC00 <= ord(last) <= 0xD7A3:
                        base = ord(last) - HANGUL_BASE
                        cho_idx = base // 588
                        jung_idx = (base % 588) // 28
                        if (base % 28) == 0:
                            out[-1] = chr(HANGUL_BASE + cho_idx*588
                                          + jung_idx*28 + FINALS.index('ㅇ'))
                    i += 3
                    continue
                i += 2
                continue
            # Inherent 'a' (default schwa for 자음 alone)
            if c == 'य':
                out.append(_compose('ㅇ', 'ㅑ'))  # 'ya' default
            else:
                out.append(_compose(cho, 'ㅏ'))  # default 자음+a
            i += 1
            continue

        # Anusvara on previous syllable
        if c == ANUSVARA and out:
            last = out[-1]
            if len(last) == 1 and 0xAC00 <= ord(last) <= 0xD7A3:
                base = ord(last) - HANGUL_BASE
                cho_idx = base // 588
                jung_idx = (base % 588) // 28
                if (base % 28) == 0:
                    out[-1] = chr(HANGUL_BASE + cho_idx*588
                                  + jung_idx*28 + FINALS.index('ㅇ'))
            i += 1
            continue

        # Visarga
        if c == VISARGA:
            out.append('ㅎ')  # NIKL: 'ḥ' → 흐
            i += 1
            continue

        # Whitespace, punctuation, unknown
        out.append(c)
        i += 1

    return out


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Hindi (Devanagari) text → Hangul (NIKL convention)."""
    parts = re.split(r'(\s+|[,.!?;:।॥])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:।॥]', part):
            out.append(part); continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)


# 자주 쓰는 hindi 단어 NIKL override (table-driven for accuracy)
_HANGUL_OVERRIDES = {
    'नमस्ते': '나마스테',
    'नमस्कार': '나마스카르',
    'धन्यवाद': '단야바드',
    'भारत': '바라트',
    'हिन्दी': '힌디',
    'दिल्ली': '델리',
    'मुंबई': '뭄바이',
    'गांधी': '간디',
    'योग': '요가',
    'चाय': '차이',
    'करी': '카레',
    'मसाला': '마살라',
    'नाम': '남',
    'बच्चा': '바차',
    'राम': '람',
    'कृष्ण': '크리슈나',
    'आगरा': '아그라',
    'जयपुर': '자이푸르',
    'गंगा': '강가',
    'हिमालय': '히말라야',
}


def transcribe_with_overrides(text, **kwargs):
    """Override 우선 적용."""
    if text.strip() in _HANGUL_OVERRIDES:
        return _HANGUL_OVERRIDES[text.strip()]
    return transcribe(text, **kwargs)


if __name__ == '__main__':
    samples = [
        ('नमस्ते', '나마스테'),
        ('धन्यवाद', '단야바드'),
        ('भारत', '바라트'),
        ('दिल्ली', '델리'),
        ('मुंबई', '뭄바이'),
    ]
    for inp, exp in samples:
        r = transcribe(inp)
        ok = '✓' if r == exp else '✗'
        print(f'{ok} {inp:20} → {r:20} (expected: {exp})')
