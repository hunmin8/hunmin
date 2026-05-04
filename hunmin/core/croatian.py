"""Hunmin Precise — Croatian/Bosnian (hr/bs) letter-by-letter → Hangul.

NIKL 외래어 표기법 (구) 유고슬라비아 핵심:
  - 모음: a → ㅏ, e → ㅔ, i → ㅣ, o → ㅗ, u → ㅜ
  - 자음 특수:
      š → ㅅ, ž → 주, č → ㅊ, ć → ㅊ, đ/dj → ㅈ
      lj → 리야 (palatal l), nj → 니야 (palatal n)
      h → 흐 (NIKL: 약화 — 단어 끝/자음 앞 받침 흡수 안 함)
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
    'a':'ㅏ','e':'ㅔ','i':'ㅣ','o':'ㅗ','u':'ㅜ',
}
VOWEL_LETTERS = set(VOWEL_J.keys())


def _is_vowel(c):
    return c in VOWEL_LETTERS


def _phonemize(word, precise=False):
    s = word.lower()
    s = re.sub(r'([bcdfgklmnprstv])\1', r'\1', s)

    # Digraph placeholders
    s = s.replace('lj', '\x01')   # lj → 리/리야
    s = s.replace('nj', '\x02')   # nj → 니/니야
    s = s.replace('dž', '\x03')   # dž → 주
    s = s.replace('dj', '\x04')   # dj → 지 (NIKL alternative for đ)

    out = []
    i = 0
    n = len(s)
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        if c == '\x01':  # lj → palatal l
            # v3.38: 어말/자음앞 lj → ㄹ jamo (absorb_finals이 받침으로); obitelj 오비텔
            if not _is_vowel(nxt):
                out.append('ㄹ')
                i += 1; continue
            # v3.38: Intervocalic V+lj+V → V받침ㄹ + ㄹ+ㅣ + ㅇ+V (zemlja 제믈리아)
            if i > 0 and s[i-1] in VOWEL_LETTERS and out:
                last = out[-1]
                if len(last) == 1 and 0xAC00 <= ord(last) <= 0xD7A3:
                    base = ord(last) - HANGUL_BASE
                    cho_idx = base // 588
                    jung_idx = (base % 588) // 28
                    jong_idx = base % 28
                    if jong_idx == 0:
                        out[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index('ㄹ'))
                        out.append(_compose('ㄹ', 'ㅣ'))
                        out.append(_compose('ㅇ', VOWEL_J[nxt]))
                        i += 2
                        continue
            # 어두/자음 뒤 + V — palatal
            Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
            v = VOWEL_J[nxt]
            out.append(_compose('ㄹ', Y_V.get(v, v)))
            i += 2; continue
        if c == '\x02':  # nj → palatal n
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㄴ', Y_V.get(v, v)))
                i += 2; continue
            out.append('니'); i += 1; continue
        if c == '\x03':  # dž
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('주'); i += 1; continue
        if c == '\x04':  # dj
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('지'); i += 1; continue

        if c == 'š':
            # v3.38: 'š+lj+V' → 실 + 리 (+ ㅇ+V if V≠i): šljivovica 실리보비차
            nxt2 = s[i+2] if i+2 < n else ''
            if nxt == '\x01' and nxt2 in VOWEL_LETTERS:
                syll = chr(HANGUL_BASE + INITIALS.index('ㅅ')*588 + VOWELS_J.index('ㅣ')*28 + FINALS.index('ㄹ'))
                out.append(syll)
                out.append(_compose('ㄹ', 'ㅣ'))
                if nxt2 != 'i':
                    out.append(_compose('ㅇ', VOWEL_J[nxt2]))
                i += 3
                continue
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㅅ', Y_V.get(v, v)))
                i += 2; continue
            out.append('시'); i += 1; continue  # v3.38: NIKL š 어말/자음앞 → 시
        if c == 'ž':
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('지'); i += 1; continue  # v3.38: NIKL ž 어말/자음앞 → 지
        if c == 'č':
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('치'); i += 1; continue
        if c == 'ć':  # softer ch
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('치'); i += 1; continue
        if c == 'đ':
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('지'); i += 1; continue

        # 'c' = /ts/ in Slavic — affricate
        if c == 'c':
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('츠'); i += 1; continue

        # v3.38: 'C + lj + V' cluster (zemlja 제믈리아) — C+ㅡ+ㄹ받침 + ㄹ+ㅣ + ㅇ+V (V≠i)
        nxt2 = s[i+2] if i+2 < n else ''
        _CLJ_CHO = {'b':'ㅂ','d':'ㄷ','g':'ㄱ','k':'ㅋ','m':'ㅁ','n':'ㄴ',
                    'p':'ㅍ','s':'ㅅ','t':'ㅌ','z':'ㅈ'}
        if (c in _CLJ_CHO and nxt == '\x01' and nxt2 in VOWEL_LETTERS):
            cho_jamo = _CLJ_CHO[c]
            syll = chr(HANGUL_BASE
                       + INITIALS.index(cho_jamo)*588
                       + VOWELS_J.index('ㅡ')*28
                       + FINALS.index('ㄹ'))
            out.append(syll)
            out.append(_compose('ㄹ', 'ㅣ'))
            if nxt2 != 'i':
                out.append(_compose('ㅇ', VOWEL_J[nxt2]))
            i += 3
            continue

        # v3.38: Cl-cluster — C + l + V → Cㅡㄹ + ㄹV (Split 스플리트, planina 플라니나)
        _CL_CHO = {'b':'ㅂ','p':'ㅍ','k':'ㅋ','g':'ㄱ','t':'ㅌ','d':'ㄷ','s':'ㅅ','f':F}
        if (c in _CL_CHO and nxt == 'l' and nxt2 in VOWEL_LETTERS):
            cho_jamo = _CL_CHO[c]
            if cho_jamo in INITIALS:
                syll = chr(HANGUL_BASE
                           + INITIALS.index(cho_jamo)*588
                           + VOWELS_J.index('ㅡ')*28
                           + FINALS.index('ㄹ'))
                out.append(syll)
                out.append(_compose('ㄹ', VOWEL_J[nxt2]))
                i += 3
                continue

        # v3.38: Intervocalic l (V+l+V) → V받침ㄹ + ㄹV (selo 셀로, Pula 풀라, ulica 울리차)
        # 단, prev='i'면 단순 ㄹ+V 유지 (sveučilište 스베우치리시테)
        if (c == 'l' and _is_vowel(nxt)
                and i > 0 and s[i-1] in VOWEL_LETTERS and s[i-1] != 'i'
                and out):
            last = out[-1]
            if len(last) == 1 and 0xAC00 <= ord(last) <= 0xD7A3:
                base = ord(last) - HANGUL_BASE
                cho_idx = base // 588
                jung_idx = (base % 588) // 28
                jong_idx = base % 28
                if jong_idx == 0:
                    out[-1] = chr(HANGUL_BASE + cho_idx*588
                                  + jung_idx*28
                                  + FINALS.index('ㄹ'))
                    out.append(_compose('ㄹ', VOWEL_J[nxt]))
                    i += 2
                    continue

        # v3.38: 어두 C+j+V (m/v/b/p 등) → C+ㅣ + ㅇ+yV (mjesec 미예세츠, vjetar 비예타르)
        if (c in 'mbvpgkdtsz' and nxt == 'j' and i+2 < n
                and s[i+2] in VOWEL_LETTERS and i == 0):
            cons_map_cy = {'b':'ㅂ','d':'ㄷ','g':'ㄱ','k':'ㅋ','m':'ㅁ','p':'ㅍ',
                           's':'ㅅ','t':'ㅌ','v':V_OLD,'z':'ㅈ'}
            cho = cons_map_cy[c]
            out.append(_compose(cho, 'ㅣ'))
            Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ'}
            v = VOWEL_J[s[i+2]]
            out.append(_compose('ㅇ', Y_V.get(v, v)))
            i += 3
            continue

        # Generic consonants
        if c in 'bdfgjhklmnprstvxz':
            cons_map = {'b':'ㅂ','d':'ㄷ','f':F,'g':'ㄱ','j':'ㅇ','h':'ㅎ',
                         'k':'ㅋ','l':'ㄹ','m':'ㅁ','n':'ㄴ','p':'ㅍ',
                         'r':'ㄹ','s':'ㅅ','t':'ㅌ','v':V_OLD,'x':'ㅋ','z':'ㅈ'}
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
                         'r':'르','s':'스','t':'트','v':'브','x':'크스','z':'즈'}
            out.append(mute_map[c]); i += 1; continue

        if c in VOWEL_J:
            out.append(_compose('ㅇ', VOWEL_J[c]))
            i += 1; continue

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
    """Croatian/Bosnian/Serbian-Latin text → Hangul."""
    parts = re.split(r'(\s+|[,.!?;:])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:]', part):
            out.append(part); continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)
