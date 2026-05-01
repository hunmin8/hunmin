"""Hunmin Precise — Romanian (ro) letter-by-letter → Hangul.

NIKL 외래어 표기법 루마니아어 핵심:
  - 모음: a → ㅏ, ă → ㅓ (schwa /ə/), â/î → ㅡ (close central /ɨ/)
          e → ㅔ, i → ㅣ, o → ㅗ, u → ㅜ
  - 자음 특수:
      ș → ㅅ (s with comma below)
      ț → ㅊ (t with comma below — sound /ts/)
      c + e/i → ㅊ, c + 그 외 → ㅋ
      g + e/i → ㅈ, g + 그 외 → ㄱ
      ch + e/i → 케/키 (silent h, k sound)
      gh + e/i → 게/기 (silent h, g sound)
      x → 크스
      h → 흐 (단어 어두) / 약화
  - 받침: 어말 자음 → 자음+ㅡ 또는 받침 흡수
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
        c = INITIALS.index(cho); j = VOWELS_J.index(jung)
        f = FINALS.index(jong) if jong in FINALS else 0
        return chr(HANGUL_BASE + c*588 + j*28 + f)
    return cho + jung + jong


VOWEL_J = {
    'a':'ㅏ',
    'ă':'ㅓ',          # NIKL: schwa → ㅓ
    'â':'ㅡ', 'î':'ㅡ', # NIKL: central close → ㅡ
    'e':'ㅔ',
    'i':'ㅣ',
    'o':'ㅗ',
    'u':'ㅜ',
}
VOWEL_LETTERS = set(VOWEL_J.keys())
FRONT_VOWELS = {'e','i'}  # c/g 앞에서 palatal 발음 트리거


def _is_vowel(c):
    return c in VOWEL_LETTERS


def _phonemize(word, precise=False):
    """Romanian word → list of jamo tokens."""
    s = word.lower()

    # Geminate collapse
    s = re.sub(r'([bcdfgklmnprstv])\1', r'\1', s)

    # Digraph placeholders
    s = s.replace('ch', '\x01')   # ch → /k/ + 다음 모음 결합
    s = s.replace('gh', '\x02')   # gh → /g/ + 다음 모음

    out = []
    i = 0
    n = len(s)
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # Digraphs
        if c == '\x01':  # ch — silent h, k sound
            if _is_vowel(nxt):
                out.append(_compose('ㅋ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('크'); i += 1; continue
        if c == '\x02':  # gh — silent h, g sound
            if _is_vowel(nxt):
                out.append(_compose('ㄱ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('그'); i += 1; continue

        # c + e/i → ㅊ; c + 그 외 → ㅋ
        if c == 'c':
            if nxt in FRONT_VOWELS:
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            if _is_vowel(nxt):
                out.append(_compose('ㅋ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('크'); i += 1; continue
        # g + e/i → ㅈ; g + 그 외 → ㄱ
        if c == 'g':
            if nxt in FRONT_VOWELS:
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            if _is_vowel(nxt):
                out.append(_compose('ㄱ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('그'); i += 1; continue

        # Special cedilla letters
        if c == 'ș':
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ',
                        'ㅓ':'ㅕ','ㅡ':'ㅡ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㅅ', Y_V.get(v, v)))
                i += 2; continue
            out.append('슈'); i += 1; continue
        if c == 'ț':  # /ts/
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('츠'); i += 1; continue

        # x → 크스 (or ㅋㅅ before vowel as kis-)
        if c == 'x':
            if _is_vowel(nxt):
                out.append('크')
                out.append(_compose('ㅅ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('크스'); i += 1; continue

        # h: 단어 어두면 ㅎ, 그 외에는 약화
        if c == 'h':
            if _is_vowel(nxt):
                out.append(_compose('ㅎ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('흐'); i += 1; continue

        # Generic consonants
        if c in 'bdfjklmnprstvwz':
            cons_map = {'b':'ㅂ','d':'ㄷ','f':F,'j':'ㅈ','k':'ㅋ','l':'ㄹ',
                         'm':'ㅁ','n':'ㄴ','p':'ㅍ','r':'ㄹ','s':'ㅅ',
                         't':'ㅌ','v':V_OLD,'w':'ㅇ','z':'ㅈ'}
            cho = cons_map[c]
            if _is_vowel(nxt):
                out.append(_compose(cho, VOWEL_J[nxt]))
                i += 2; continue
            mute_map = {'b':'브','d':'드','f':'프','j':'주','k':'크',
                         'l':'ㄹ','m':'ㅁ','n':'ㄴ','p':'프','r':'르',
                         's':'스','t':'트','v':'브','w':'우','z':'즈'}
            out.append(mute_map[c]); i += 1; continue

        # Vowel alone
        if c in VOWEL_J:
            out.append(_compose('ㅇ', VOWEL_J[c]))
            i += 1; continue

        # Unhandled
        out.append(c); i += 1

    return _absorb_finals(out)


def _absorb_finals(syls):
    result = []
    i = 0
    while i < len(syls):
        s = syls[i]
        nxt = syls[i+1] if i+1 < len(syls) else ''
        if (len(s) == 1 and 0xAC00 <= ord(s) <= 0xD7A3 and
            nxt in ('ㄹ','ㅁ','ㄴ','ㅇ','ㅂ','ㄱ','ㅅ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ')):
            base = ord(s) - HANGUL_BASE
            cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
            if jong_idx == 0 and nxt in FINALS:
                new = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index(nxt))
                result.append(new); i += 2; continue
        result.append(s); i += 1
    return result


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Romanian text → Hangul."""
    parts = re.split(r'(\s+|[,.!?;:])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:]', part):
            out.append(part); continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)
