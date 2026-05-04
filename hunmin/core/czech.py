"""Hunmin Precise — Czech (cs) letter-by-letter → Hangul.

NIKL 외래어 표기법 체코어 핵심:
  - 모음: a/á → ㅏ, e/é → ㅔ, i/í/y/ý → ㅣ, o/ó → ㅗ, u/ú/ů → ㅜ
          ě → 예/예 (palatalize 이전 자음)
  - 자음 digraphs:
      ch → 흐 (German-style x)
      š → ㅅ, ž → 주, č → ㅊ
      ř → 즈 (NIKL: 단독 → 르ᄌ; 단순화 → 즈)
      ť → 티, ď → 디, ň → 니 (palatal)
  - 받침: 어말 자음 → 받침 흡수 또는 단모음
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
    'e':'ㅔ', 'é':'ㅔ',
    'i':'ㅣ', 'í':'ㅣ', 'y':'ㅣ', 'ý':'ㅣ',
    'o':'ㅗ', 'ó':'ㅗ',
    'u':'ㅜ', 'ú':'ㅜ', 'ů':'ㅜ',
    'ě':'ㅔ',  # NIKL Czech: ě → ㅔ (palatalization absorbed by preceding cons orthography)
}

# v3.38: Cl-cluster cho mapping (C + l + V → Cㅡㄹ + ㄹV)
# '\x02' = digraph placeholder for 'ch'
_CL_CHO = {
    'b':'ㅂ', 'p':'ㅍ', 'k':'ㅋ', 'g':'ㄱ',
    't':'ㅌ', 'd':'ㄷ', 's':'ㅅ', '\x02':'ㅎ',
}
VOWEL_LETTERS = set(VOWEL_J.keys())


def _is_vowel(c):
    return c in VOWEL_LETTERS


def _phonemize(word, precise=False):
    """Czech word → list of jamo tokens."""
    s = word.lower()

    # Geminate collapse
    s = re.sub(r'([bcdfgklmnprstv])\1', r'\1', s)

    # Digraph placeholders
    s = s.replace('ch', '\x02')   # ch → 흐 (single sound)

    out = []
    i = 0
    n = len(s)
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # Digraphs
        if c == '\x02':  # ch → 흐
            # v3.38: Cl-cluster ch + l + V → 흘 + ㄹV (chleba → 흘레바)
            nxt2 = s[i+2] if i+2 < n else ''
            if nxt == 'l' and nxt2 in VOWEL_LETTERS:
                syll = chr(HANGUL_BASE
                           + INITIALS.index('ㅎ')*588
                           + VOWELS_J.index('ㅡ')*28
                           + FINALS.index('ㄹ'))
                out.append(syll)
                out.append(_compose('ㄹ', VOWEL_J[nxt2]))
                i += 3; continue
            if _is_vowel(nxt):
                out.append(_compose('ㅎ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('흐'); i += 1; continue

        # Special consonants
        if c == 'š':
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅣ':'ㅣ','ㅗ':'ㅛ','ㅜ':'ㅠ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㅅ', Y_V.get(v, v)))
                i += 2; continue
            out.append('시'); i += 1; continue  # v3.38: NIKL š 어말/자음앞 → 시
        if c == 'ž':
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('주'); i += 1; continue
        if c == 'č':
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('치'); i += 1; continue
        if c == 'ř':  # uniquely Czech (raised alveolar trill, /r̝/)
            # NIKL: ř → 즈 (default), or 르 in some contexts
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('르주'); i += 1; continue
        if c == 'ť':
            if _is_vowel(nxt):
                out.append(_compose('ㅌ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('티'); i += 1; continue
        if c == 'ď':
            if _is_vowel(nxt):
                out.append(_compose('ㄷ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('디'); i += 1; continue
        if c == 'ň':
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅣ':'ㅣ','ㅗ':'ㅛ','ㅜ':'ㅠ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㄴ', Y_V.get(v, v)))
                i += 2; continue
            out.append('니'); i += 1; continue

        # ě — NIKL Czech: ě → 에 (단독 시작/모음 후), 자음+ě는 VOWEL_J 매핑이 처리
        if c == 'ě':
            out.append(_compose('ㅇ', 'ㅔ'))
            i += 1; continue

        # 'c' = /ts/ — affricate
        if c == 'c':
            if _is_vowel(nxt):
                out.append(_compose('ㅊ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('츠'); i += 1; continue

        # v3.38: Cl-cluster — C + l + V → Cㅡㄹ + ㄹV
        # (Klima → 클리마, slunce → 슬룬체, chleba → 흘레바, škola — handled via 시+kola path)
        nxt2 = s[i+2] if i+2 < n else ''
        if (c in _CL_CHO and nxt == 'l'
                and nxt2 in VOWEL_LETTERS):
            cho_jamo = _CL_CHO[c]
            # C+ㅡ+ㄹ받침 syllable (e.g., 클, 슬, 흘)
            syll = chr(HANGUL_BASE
                       + INITIALS.index(cho_jamo)*588
                       + VOWELS_J.index('ㅡ')*28
                       + FINALS.index('ㄹ'))
            out.append(syll)
            # ㄹ + V syllable
            out.append(_compose('ㄹ', VOWEL_J[nxt2]))
            i += 3
            continue

        # v3.38: Intervocalic l — V + l + V → V받침ㄹ + ㄹV
        # (ulice → 울리체, guláš → 굴라시)
        if (c == 'l' and _is_vowel(nxt)
                and i > 0 and s[i-1] in VOWEL_LETTERS
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
            # v3.38: Word-final devoicing — 어말 b/d/g/v → 프/트/크/프 (ostrov → 오스트로프)
            if i+1 >= n and c in 'bdgv':
                devoice = {'b':'프','d':'트','g':'크','v':'프'}
                out.append(devoice[c]); i += 1; continue
            mute_map = {'b':'브','d':'드','f':'프','g':'그','j':'이','h':'흐',
                         'k':'크','l':'ㄹ','m':'ㅁ','n':'ㄴ','p':'프',
                         'r':'르','s':'스','t':'트','v':'브','x':'크스','z':'즈'}
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
    """Czech text → Hangul."""
    parts = re.split(r'(\s+|[,.!?;:])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:]', part):
            out.append(part); continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)
