"""Hunmin Precise — Hungarian (hu) letter-by-letter → Hangul.

NIKL 외래어 표기법 헝가리어 핵심 규칙:
  - 모음: a → ㅓ (Hungarian a is /ɒ/), á → ㅏ
          e → ㅔ, é → ㅔ (장음, NIKL은 동일하게 ㅔ)
          i/í → ㅣ, o/ó → ㅗ, ö/ő → ㅚ, u/ú → ㅜ, ü/ű → ㅟ
  - 자음:
      c → ㅊ (ts 발음)
      cs → ㅊ (CH 발음)
      gy → 지 (palatal d, 다음 모음과 결합)
      ny → 니 (palatal n)
      ly → 이 (j 발음, 일반적으로 이전 vowel과 결합)
      ty → 티 (palatal t)
      sz → ㅅ (s)
      s → 슈/시 (sh)
      zs → 주 (zh)
      dz → ㅈ
      dzs → 주 (j 발음)
      ch → 흐 (외래어)
  - 받침: 단어 끝 자음 — k → 크/ㄱ, t → 트/ㅌ, etc (NIKL: 자음+ㅡ)
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


# Two layers of vowel mapping — see UHPS_SPEC §1.0 for layer separation
# Phonetic (음운적): IPA-faithful, language-learning oriented
# NIKL: 외래어 표기법 컨벤션 (Korean reader-friendly, may diverge from phonetic)
VOWEL_J_PHONETIC = {
    'a': 'ㅏ',  # IPA /ɒ/ — closer to ㅏ phonetically
    'á': 'ㅏ',
    'e': 'ㅔ', 'é': 'ㅔ',
    'i': 'ㅣ', 'í': 'ㅣ',
    'o': 'ㅗ', 'ó': 'ㅗ',
    'ö': 'ㅚ', 'ő': 'ㅚ',
    'u': 'ㅜ', 'ú': 'ㅜ',
    'ü': 'ㅟ', 'ű': 'ㅟ',
}

VOWEL_J_NIKL = {
    'a': 'ㅓ',  # NIKL: Hungarian a /ɒ/ → ㅓ (외래어 표기법 컨벤션)
    'á': 'ㅏ',
    'e': 'ㅔ', 'é': 'ㅔ',
    'i': 'ㅣ', 'í': 'ㅣ',
    'o': 'ㅗ', 'ó': 'ㅗ',
    'ö': 'ㅚ', 'ő': 'ㅚ',
    'u': 'ㅜ', 'ú': 'ㅜ',
    'ü': 'ㅟ', 'ű': 'ㅟ',
}

# Default = NIKL (HUNMIN-readable layer 기본값)
VOWEL_J = VOWEL_J_NIKL

VOWEL_LETTERS = set(VOWEL_J.keys())


def _is_vowel(c):
    return c in VOWEL_LETTERS


def _phonemize(word, precise=False, phonetic=False):
    """Hungarian word → list of jamo tokens.
    phonetic=True : 음운 정확도 우선 (a → ㅏ /ɒ/)
    phonetic=False (default) : NIKL 컨벤션 (a → ㅓ)
    """
    global VOWEL_J
    VOWEL_J = VOWEL_J_PHONETIC if phonetic else VOWEL_J_NIKL
    s = word.lower()

    # Normalize geminates: tt/nn/ll/kk/pp/bb/dd/gg/mm/rr/ss → 받침+자음
    # NIKL: 강조된 geminate는 앞 음절에 받침으로 흡수
    geminate = re.compile(r'([bdfgklmnprstv])\1')
    # Don't normalize digraph parts (cs, sz, gy, ny, ly, ty, zs, dz)
    # Simple geminate pattern: handles bb, dd, gg, kk, ll, mm, nn, pp, rr, ss, tt
    # But NOT cs+s, etc. cs is treated separately first.

    # Normalize digraphs (longer first) — placeholder chars
    s = s.replace('dzs', '\x01')   # dzs → 주 (zh-like /dʒ/)
    s = s.replace('cs', '\x02')    # cs → ㅊ (CH)
    s = s.replace('dz', '\x03')    # dz → ㅈ
    s = s.replace('gy', '\x04')    # gy → palatal d
    s = s.replace('ny', '\x05')    # ny → palatal n
    s = s.replace('ly', '\x06')    # ly → j
    s = s.replace('sz', '\x07')    # sz → s
    s = s.replace('ty', '\x08')    # ty → palatal t
    s = s.replace('zs', '\x0B')    # zs → zh

    # Now handle simple geminates AFTER digraph extraction
    s = re.sub(r'([bdfgklmnprstv])\1', r'\1', s)  # collapse double cons

    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # Handle digraph placeholders
        # \x01 = dzs (jzh), \x02 = cs (ch), \x03 = dz (j), \x04 = gy (palatal d),
        # \x05 = ny, \x06 = ly, \x07 = sz, \x08 = ty, \x0B = zs
        if c == '\x02':  # cs → ㅊ
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2
                continue
            out.append('치'); i += 1; continue
        if c == '\x07':  # sz → ㅅ
            if _is_vowel(nxt):
                out.append(_compose('ㅅ', VOWEL_J[nxt]))
                i += 2
                continue
            out.append('스'); i += 1; continue
        if c == '\x04':  # gy → palatalized 지/져/죠 etc.
            if _is_vowel(nxt):
                v = VOWEL_J[nxt]
                Y_V = {'ㅓ':'ㅕ','ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅚ':'ㅛ',
                        'ㅜ':'ㅠ','ㅟ':'ㅠ','ㅣ':'ㅣ'}
                out.append(_compose('ㅈ', Y_V.get(v, v)))
                i += 2
                continue
            out.append('지'); i += 1; continue
        if c == '\x05':  # ny → 니(palatal). NIKL: nya→녀, nyo→뇨, nyu→뉴 etc.
            if _is_vowel(nxt):
                # Palatalize the vowel (use Y_VOWEL mapping)
                v = VOWEL_J[nxt]
                Y_V = {'ㅓ':'ㅕ','ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅚ':'ㅛ',
                        'ㅜ':'ㅠ','ㅟ':'ㅠ','ㅣ':'ㅣ'}
                out.append(_compose('ㄴ', Y_V.get(v, v)))
                i += 2; continue
            out.append('니'); i += 1; continue
        if c == '\x08':  # ty → 티(palatal). NIKL: tya→탸, tyo→툐
            if _is_vowel(nxt):
                v = VOWEL_J[nxt]
                Y_V = {'ㅓ':'ㅕ','ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅚ':'ㅛ',
                        'ㅜ':'ㅠ','ㅟ':'ㅠ','ㅣ':'ㅣ'}
                out.append(_compose('ㅌ', Y_V.get(v, v)))
                i += 2; continue
            out.append('티'); i += 1; continue
        if c == '\x06':  # ly → 이/[lj]
            # NIKL: ly is silent or merged with vowel
            if _is_vowel(nxt):
                # ly + vowel: just vowel with i-glide
                v = VOWEL_J[nxt]
                # Try Y_VOWEL mapping
                Y_V = {'ㅓ':'ㅕ','ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
                out.append(_compose('ㅇ', Y_V.get(v, v)))
                i += 2; continue
            out.append('이'); i += 1; continue
        if c == '\x03':  # dz → ㅈ
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('즈'); i += 1; continue
        if c == '\x01':  # dzs → 주
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('주'); i += 1; continue
        if c == '\x0B':  # zs → 주
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('주'); i += 1; continue

        # Single consonants
        if c == 'c':  # ts
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('츠'); i += 1; continue
        if c == 's':  # sh-like
            if _is_vowel(nxt):
                # NIKL: s + a/e/i/o/u → 사/세/시/소/수 (actually 샤 etc for sh)
                # Use simpler: s + V → 슈+/시 patterns
                v_map = {'ㅓ':'ㅓ','ㅏ':'ㅑ','ㅔ':'ㅖ','ㅣ':'ㅣ',
                          'ㅗ':'ㅛ','ㅚ':'ㅚ','ㅜ':'ㅠ','ㅟ':'ㅟ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㅅ', v_map.get(v, v)))
                i += 2; continue
            out.append('슈'); i += 1; continue

        # Generic consonants
        if c in 'bdfgjklmnprtvz':
            cons_map = {'b':'ㅂ','d':'ㄷ','f':'ㆄ' if precise else 'ㅍ',
                         'g':'ㄱ','j':'ㅇ','k':'ㅋ','l':'ㄹ','m':'ㅁ',
                         'n':'ㄴ','p':'ㅍ','r':'ㄹ','t':'ㅌ',
                         'v':'ㅸ' if precise else 'ㅂ','z':'ㅈ'}
            cho = cons_map[c]
            if _is_vowel(nxt):
                # j + vowel → y-initial (예: ja → 야)
                if c == 'j':
                    Y_V = {'ㅓ':'ㅕ','ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅚ':'ㅛ','ㅜ':'ㅠ','ㅟ':'ㅠ','ㅣ':'ㅣ'}
                    v = VOWEL_J[nxt]
                    out.append(_compose('ㅇ', Y_V.get(v, v)))
                else:
                    out.append(_compose(cho, VOWEL_J[nxt]))
                i += 2; continue
            # consonant + consonant or word-end
            mute_map = {'b':'브','d':'드','f':'프','g':'그','j':'이','k':'크',
                         'l':'ㄹ','m':'ㅁ','n':'ㄴ','p':'프','r':'르','t':'트',
                         'v':'브','z':'즈'}
            out.append(mute_map[c]); i += 1; continue

        # Vowel alone
        if c in VOWEL_J:
            out.append(_compose('ㅇ', VOWEL_J[c]))
            i += 1; continue

        # h
        if c == 'h':
            if _is_vowel(nxt):
                out.append(_compose('ㅎ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('흐'); i += 1; continue

        # Unhandled — keep as-is
        out.append(c)
        i += 1

    # Try to absorb 받침 — combine adjacent CV + 마지막자음으로
    return _absorb_finals(out)


def _absorb_finals(syls):
    """Combine '바' + 'ㄴ' patterns into '반'. Heuristic."""
    result = []
    i = 0
    while i < len(syls):
        s = syls[i]
        nxt = syls[i+1] if i+1 < len(syls) else ''
        # Try to absorb single jamo as 받침
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
    """Hungarian text → Hangul.

    Args:
      text: input text
      mode: 'hangul' (default) — produces Korean surface
      precise: bool — if True, use 옛한글 ㆄ/ㅸ for f/v
      phonetic: bool — True면 음운 정확도 (a → ㅏ), False면 NIKL (a → ㅓ)
    """
    # Word-level processing (split by space, preserve punctuation)
    parts = re.split(r'(\s+|[,.!?;:])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:]', part):
            out.append(part)
            continue
        syls = _phonemize(part, precise=precise, phonetic=phonetic)
        out.append(''.join(syls))
    return ''.join(out)
