"""Hunmin Precise — Vietnamese (vi) letter-by-letter → Hangul.

NIKL 외래어 표기법 베트남어 핵심:
  - 모음 (NIKL은 톤 무시, 단모음/단음만 매핑):
      a → ㅏ, ă → ㅏ, â → ㅓ
      e → ㅔ, ê → ㅔ
      i/y → ㅣ
      o → ㅗ, ô → ㅗ, ơ → ㅓ
      u → ㅜ, ư → ㅡ
  - 자음 특수:
      ph → ㅍ (또는 ㆄ in precise)
      đ → ㄷ
      d → ㅈ (북부 표준)
      r → ㅈ (북부) / 르
      ch → 짜 (palatal)
      tr → ㅉ (NIKL: 짜 계열)
      gi → ㅈ (북부)
      th → ㅌ
      kh → 크
      nh → 니 (palatal)
      ngh/ng → 응 (전설), ㄴ응 (어말 ng → 받침 응)
      x → 시 (sh-like)
      qu → 꾸
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


# Tone-stripped vowel mapping (NIKL: 톤 무시)
# 모든 톤마크 (̀, ́, ̉, ̃, ̣) 제거 후 base 모음으로
VOWEL_J = {
    'a':'ㅏ', 'ă':'ㅏ',
    'â':'ㅓ',
    'e':'ㅔ', 'ê':'ㅔ',
    'i':'ㅣ', 'y':'ㅣ',
    'o':'ㅗ', 'ô':'ㅗ',
    'ơ':'ㅓ',
    'u':'ㅜ',
    'ư':'ㅡ',
}
VOWEL_LETTERS = set(VOWEL_J.keys())


def _strip_tone(text):
    """Vietnamese 톤 마크 제거 — NIKL 컨벤션."""
    import unicodedata
    s = unicodedata.normalize('NFD', text)
    # combining tone marks 제거
    out = ''.join(c for c in s if c not in '̣́̀̉̃')
    return unicodedata.normalize('NFC', out)


def _is_vowel(c):
    return c in VOWEL_LETTERS


def _phonemize(word, precise=False):
    s = _strip_tone(word).lower()

    # Multi-char digraphs (longest first)
    s = s.replace('ngh', '\x01')   # ngh → 응 (palatal)
    s = s.replace('ng',  '\x02')   # ng  → 응
    s = s.replace('nh',  '\x03')   # nh  → 니 (palatal)
    s = s.replace('ph',  '\x04')   # ph  → ㅍ (/f/)
    s = s.replace('th',  '\x05')   # th  → ㅌ
    s = s.replace('tr',  '\x06')   # tr  → ㅉ
    s = s.replace('ch',  '\x07')   # ch  → 짜 (palatal)
    s = s.replace('kh',  '\x08')   # kh  → 크
    s = s.replace('gh',  '\x09')   # gh  → ㄱ
    s = s.replace('gi',  '\x0B')   # gi  → ㅈ (북부)
    s = s.replace('qu',  '\x0C')   # qu  → 꾸

    # v3.38: NIKL Vietnamese vowel diphthongs (a/ô → ơ when after u/ư)
    s = s.replace('ưa', 'ươ')   # ưa → ㅡ+ㅓ (lửa 르어)
    s = s.replace('uô', 'uơ')   # uô → ㅜ+ㅓ (cuốn 꾸언)
    s = s.replace('ua', 'uơ')   # ua → ㅜ+ㅓ (chùa 쭈어)

    out = []
    i = 0
    n = len(s)
    F = 'ㆄ' if precise else 'ㅍ'

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # Digraph placeholders
        if c in ('\x01', '\x02'):  # ng/ngh
            # 어말이면 받침 응, 어두면 응 + 모음
            if _is_vowel(nxt):
                # 어두 ng + 모음 → 응 + 모음 (NIKL: 응)
                # 따로 분리: 응 syllable + V syllable
                out.append('응')
                out.append(_compose('ㅇ', VOWEL_J[nxt]))
                i += 2; continue
            # 어말 ng — 직전 syllable에 받침 ㅇ
            out.append('응'); i += 1; continue
        if c == '\x03':  # nh — palatal n
            if _is_vowel(nxt):
                Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅣ':'ㅣ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅓ':'ㅕ','ㅡ':'ㅡ'}
                v = VOWEL_J[nxt]
                out.append(_compose('ㄴ', Y_V.get(v, v)))
                i += 2; continue
            # 어말 nh → 받침 ㄴ NIKL (đình 딘, bánh 반, thành 탄)
            out.append('ㄴ'); i += 1; continue
        if c == '\x04':  # ph
            if _is_vowel(nxt):
                out.append(_compose(F if precise else 'ㅍ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('프'); i += 1; continue
        if c == '\x05':  # th
            if _is_vowel(nxt):
                out.append(_compose('ㅌ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('트'); i += 1; continue
        if c == '\x06':  # tr (NIKL: ㅉ)
            if _is_vowel(nxt):
                out.append(_compose('ㅉ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('쯔'); i += 1; continue
        if c == '\x07':  # ch (NIKL: 짜 = ㅉ + V)
            if _is_vowel(nxt):
                out.append(_compose('ㅉ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('찌'); i += 1; continue
        if c == '\x08':  # kh
            if _is_vowel(nxt):
                out.append(_compose('ㅋ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('크'); i += 1; continue
        if c == '\x09':  # gh
            if _is_vowel(nxt):
                out.append(_compose('ㄱ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('그'); i += 1; continue
        if c == '\x0B':  # gi (북부 z-like → ㅈ)
            if _is_vowel(nxt):
                out.append(_compose('ㅈ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('지'); i += 1; continue
        if c == '\x0C':  # qu
            if _is_vowel(nxt):
                out.append(_compose('ㄲ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('꾸'); i += 1; continue

        # đ → ㄷ
        if c == 'đ':
            if _is_vowel(nxt):
                out.append(_compose('ㄷ', VOWEL_J[nxt]))
                i += 2; continue
            out.append('드'); i += 1; continue

        # 어말 c/t/p → 받침 ㄱ/ㅅ/ㅂ (Vietnamese final stops, NIKL)
        # đất 덧, mặt 맛, nước 느억 (c→ㄱ받침)
        if c in 'ctp' and not _is_vowel(nxt) and i + 1 == n:
            jong_map = {'c':'ㄱ', 't':'ㅅ', 'p':'ㅂ'}
            out.append(jong_map[c]); i += 1; continue

        # Generic consonants
        # NIKL: c/k → ㄲ (Vietnamese 일반)
        # Actually NIKL: c → ㄲ (북부) — 보수적으로 ㅋ 사용
        if c in 'bcdfghjklmnprstvwxz':
            cons_map = {
                'b':'ㅂ','c':'ㄲ','d':'ㅈ','f':F if precise else 'ㅍ',
                'g':'ㄱ','h':'ㅎ','j':'ㅈ','k':'ㄲ','l':'ㄹ',
                'm':'ㅁ','n':'ㄴ','p':'ㅂ','r':'ㅈ','s':'ㅅ',
                't':'ㄸ','v':'ㅂ','w':'ㅇ','x':'ㅅ','z':'ㅈ',
            }
            cho = cons_map[c]
            if _is_vowel(nxt):
                if c == 'x':
                    Y_V = {'ㅏ':'ㅑ','ㅔ':'ㅖ','ㅣ':'ㅣ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅓ':'ㅕ'}
                    v = VOWEL_J[nxt]
                    out.append(_compose('ㅅ', Y_V.get(v, v)))
                else:
                    out.append(_compose(cho, VOWEL_J[nxt]))
                i += 2; continue
            mute_map = {'b':'브','c':'크','d':'즈','f':'프','g':'그','h':'흐',
                         'j':'즈','k':'크','l':'ㄹ','m':'ㅁ','n':'ㄴ',
                         'p':'프','r':'르','s':'스','t':'트','v':'브',
                         'w':'으','x':'스','z':'즈'}
            out.append(mute_map[c]); i += 1; continue

        # v3.38: y + ê → 예 (palatal y; tình yêu 띤예우)
        if c == 'y' and nxt == 'ê':
            out.append(_compose('ㅇ', 'ㅖ'))
            i += 2; continue

        # Vowel alone
        if c in VOWEL_J:
            out.append(_compose('ㅇ', VOWEL_J[c]))
            i += 1; continue

        out.append(c); i += 1

    return _absorb_finals(out)


def _absorb_finals(syls):
    """Combine 응 with previous syllable as 받침 ㅇ, similar for ㄴ/ㅁ/ㄹ.

    v3.38: ㄱ/ㅅ/ㅂ도 흡수 (Vietnamese 어말 stops): nước 느억, đất 덧, mặt 맛, học 혹.
    v3.38: 응 흡수 예외 — 직전 으-syllable이면 keep separate (rừng 즈응).
    """
    EU_INDEX = VOWELS_J.index('ㅡ')
    result = []
    i = 0
    while i < len(syls):
        s = syls[i]
        nxt = syls[i+1] if i+1 < len(syls) else ''
        # 응 → 직전 syllable에 ㅇ받침 흡수 (단, 으-syllable 제외)
        if (len(s) == 1 and 0xAC00 <= ord(s) <= 0xD7A3 and
                nxt == '응'):
            base = ord(s) - HANGUL_BASE
            cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
            if jong_idx == 0 and jung_idx != EU_INDEX:
                new = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index('ㅇ'))
                result.append(new); i += 2; continue
        # 단일 자음 받침 흡수 (v3.38: ㄱ/ㅅ/ㅂ added for Vietnamese final stops)
        if (len(s) == 1 and 0xAC00 <= ord(s) <= 0xD7A3 and
            nxt in ('ㄴ','ㅁ','ㄹ','ㅇ','ㄱ','ㅅ','ㅂ')):
            base = ord(s) - HANGUL_BASE
            cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
            if jong_idx == 0 and nxt in FINALS:
                new = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index(nxt))
                result.append(new); i += 2; continue
        result.append(s); i += 1
    return result


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Vietnamese text → Hangul (NIKL convention, 톤 무시).

    NIKL 베트남어: 음절 사이 공백 제거 (gia đình → 자딘, Hà Nội → 하노이).
    문장부호는 유지.
    """
    parts = re.split(r'(\s+|[,.!?;:])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace():
            continue  # NIKL: drop inter-syllable spaces
        if re.match(r'[,.!?;:]', part):
            out.append(part); continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)
