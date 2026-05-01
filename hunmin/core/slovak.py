"""Hunmin Precise — Slovak (sk) letter-by-letter → Hangul.

NIKL 외래어 표기법 슬로바키아어 핵심:
  - 모음: a → ㅏ, á → ㅏ, e → ㅔ, é → ㅔ, i/y → ㅣ, í/ý → ㅣ
          o → ㅗ, ó → ㅗ, u → ㅜ, ú → ㅜ
          ä → ㅔ, ô → 우오, ŕ → ㄹ, ĺ → ㄹ
  - 자음 digraphs:
      ch → 흐 (German-style x)
      dz → ㅈ, dž → ㅈ
      š → ㅅ, ž → 주, č → ㅊ
      ť → 티 (palatal t), ď → 디 (palatal d)
      ň → ㄴ (palatal n)
      ľ → ㄹ (palatal l)
      v → ㅸ/ㅂ (옛한글 모드 vs 기본)
      f → ㆄ/ㅍ
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
    'a':'ㅏ', 'á':'ㅏ',
    'e':'ㅔ', 'é':'ㅔ', 'ä':'ㅔ',
    'i':'ㅣ', 'í':'ㅣ', 'y':'ㅣ', 'ý':'ㅣ',
    'o':'ㅗ', 'ó':'ㅗ',
    'u':'ㅜ', 'ú':'ㅜ',
    'ô':'ㅗ',  # diphthong ô [u̯o] approximated
}
VOWEL_LETTERS = set(VOWEL_J.keys())


def _is_vowel(c):
    return c in VOWEL_LETTERS


def _phonemize(word, precise=False):
    """Slovak word → list of jamo tokens."""
    s = word.lower()

    # Geminate collapse (kk/ll/nn 등 NIKL 일반적으로 단일화)
    s = re.sub(r'([bcdfgklmnprstv])\1', r'\1', s)

    # Digraph placeholders (longer first)
    s = s.replace('dž', '\x01')   # dž → 주 (zh)
    s = s.replace('ch', '\x02')   # ch → 흐
    s = s.replace('dz', '\x03')   # dz → ㅈ

    out = []
    i = 0
    n = len(s)
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # Digraph placeholders
        if c == '\x02':  # ch → 흐
            if _is_vowel(nxt):
                out.append(_compose('ㅎ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('흐'); i += 1; continue
        if c == '\x01':  # dž → 주
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('주'); i += 1; continue
        if c == '\x03':  # dz → ㅈ
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('즈'); i += 1; continue

        # Special consonants
        if c == 'š':  # š → ㅅ + palatalize?
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅐ':'ㅒ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㅅ', Y_V.get(v, v)))
                i += 2; continue
            out.append('슈'); i += 1; continue
        if c == 'ž':  # ž → 주
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('주'); i += 1; continue
        if c == 'č':  # č → ㅊ
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('치'); i += 1; continue
        if c == 'ť':  # ť → 티 (palatal)
            if _is_vowel(nxt):
                out.append(_compose('ㅌ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('티'); i += 1; continue
        if c == 'ď':  # ď → 디 (palatal)
            if _is_vowel(nxt):
                out.append(_compose('ㄷ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('디'); i += 1; continue
        if c == 'ň':  # ň → 니 (palatal)
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㄴ', Y_V.get(v, v)))
                i += 2; continue
            out.append('니'); i += 1; continue
        if c == 'ľ':  # ľ → 리
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㄹ', Y_V.get(v, v)))
                i += 2; continue
            out.append('리'); i += 1; continue
        if c in ('ŕ','ĺ'):  # syllabic r/l
            out.append('르' if c == 'ŕ' else '리'); i += 1; continue

        # 'c' = /ts/ — affricate
        if c == 'c':
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('츠'); i += 1; continue

        # Generic consonants
        if c in 'bdfgjhklmnprstvz':
            cons_map = {'b':'ㅂ','d':'ㄷ','f':F,'g':'ㄱ','j':'ㅇ','h':'ㅎ',
                         'k':'ㅋ','l':'ㄹ','m':'ㅁ','n':'ㄴ','p':'ㅍ',
                         'r':'ㄹ','s':'ㅅ','t':'ㅌ','v':V_OLD,'z':'ㅈ'}
            cho = cons_map[c]
            if _is_vowel(nxt):
                if c == 'j':
                    Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
                    out.append(_compose('ㅇ', Y_V.get(VOWEL_J[nxt], VOWEL_J[nxt])))
                else:
                    out.append(_compose(cho, VOWEL_J[nxt]))
                i += 2; continue
            mute_map = {'b':'브','d':'드','f':'프','g':'그','j':'이','h':'흐',
                         'k':'크','l':'ㄹ','m':'ㅁ','n':'ㄴ','p':'프',
                         'r':'르','s':'스','t':'트','v':'브','z':'즈'}
            out.append(mute_map[c]); i += 1; continue

        # Vowel alone
        if c in VOWEL_J:
            out.append(_compose('ㅇ', VOWEL_J[c]))
            i += 1; continue

        # Unhandled
        out.append(c); i += 1

    return _absorb_finals(out)


def _absorb_finals(syls):
    """combine '바' + 'ㄴ' → '반'."""
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
    """Slovak text → Hangul."""
    parts = re.split(r'(\s+|[,.!?;:])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:]', part):
            out.append(part); continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)
