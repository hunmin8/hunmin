"""Hunmin Precise — Indonesian (id) letter-by-letter → Hangul.

전략: 인도네시아어는 거의 완벽한 phonetic spelling. 1-to-1 매핑.

매핑:
  a/e/i/o/u → ㅏ/ㅔ/ㅣ/ㅗ/ㅜ
  ai → 아이, au → 아우, oi → 오이
  c → ㅊ (cinta → 친타)
  ng → ㅇ (앙)
  ny → 냐/녜/뉴/뇨 (palatal)
  sy → 샤/셰/시... (palatal)
  kh → ㅎ (loanwords)
  j → ㅈ
  y → 야/예/이/요/유 (semi-vowel)
  v → ㅸ/ㅂ
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


def _add_jong_to_last(syllables, jong_jamo):
    if not syllables: return False
    last = syllables[-1]
    if len(last) == 1:
        c = ord(last)
        if 0xAC00 <= c <= 0xD7A3:
            base = c - HANGUL_BASE
            cho = base // 588; jung = (base % 588) // 28; jong = base % 28
            if jong == 0 and jong_jamo in FINALS:
                syllables[-1] = chr(HANGUL_BASE + cho*588 + jung*28 + FINALS.index(jong_jamo))
                return True
    return False


def _has_jong(syllable):
    if len(syllable) != 1: return True
    c = ord(syllable)
    if not (0xAC00 <= c <= 0xD7A3): return False
    return (c - HANGUL_BASE) % 28 != 0


def _is_eu_syll(syllable):
    if len(syllable) != 1: return False
    c = ord(syllable)
    if not (0xAC00 <= c <= 0xD7A3): return False
    return ((ord(syllable) - HANGUL_BASE) % 588) // 28 == VOWELS_J.index('ㅡ')


VOWEL_LETTERS = set('aeiou')

VOWEL_J = {'a':'ㅏ','e':'ㅔ','i':'ㅣ','o':'ㅗ','u':'ㅜ'}
Y_VOWEL_J = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ'}


def _phonemize(word, precise):
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    s = word.lower()
    n = len(s)
    out = []
    i = 0

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''
        nxt2 = s[i+2] if i+2 < n else ''

        # 모음
        if c in VOWEL_J:
            out.append(('V', VOWEL_J[c]))
            i += 1
            continue

        # === Digraphs ===
        # ng (어말 또는 자음 앞) → ㅇ받침
        if c == 'n' and nxt == 'g' and (i+2 >= n or s[i+2] not in VOWEL_LETTERS):
            out.append(('NG_ASSIM',))
            i += 2
            continue
        # ng + V → ㅇ받침 + ㄱ + V (Singapura → 싱가푸라)
        if c == 'n' and nxt == 'g' and nxt2 in VOWEL_LETTERS:
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㄱ', 'g'))
            i += 2
            continue
        # ny + V → 냐/녜/...
        if c == 'n' and nxt == 'y':
            if nxt2 in Y_VOWEL_J:
                out.append(('C', 'ㄴ', 'ny'))
                out.append(('SV', Y_VOWEL_J[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㄴ', 'ny'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue
        # sy + V → 샤/셰/...
        if c == 's' and nxt == 'y':
            if nxt2 in Y_VOWEL_J:
                out.append(('C', 'ㅅ', 'sy'))
                out.append(('SV', Y_VOWEL_J[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㅅ', 'sy'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue
        # kh → ㅎ (loanwords from Arabic)
        if c == 'k' and nxt == 'h':
            out.append(('C', 'ㅎ', 'kh'))
            i += 2
            continue

        # === Doubled consonants → drop ===
        if c == nxt and c in 'bcdfghjklmnpqrstvwyz':
            i += 1
            continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b')); i += 1; continue
        if c == 'c':
            out.append(('C', 'ㅊ', 'c')); i += 1; continue
        if c == 'd':
            out.append(('C', 'ㄷ', 'd')); i += 1; continue
        if c == 'f':
            if precise: out.append(('OLD', F))
            else: out.append(('C', F, 'f'))
            i += 1; continue
        if c == 'g':
            out.append(('C', 'ㄱ', 'g')); i += 1; continue
        if c == 'h':
            # 어말 h → silent (kasih → 카시)
            if i+1 >= n:
                i += 1; continue
            out.append(('C', 'ㅎ', 'h')); i += 1; continue
        if c == 'j':
            out.append(('C', 'ㅈ', 'j')); i += 1; continue
        if c == 'k':
            out.append(('C', 'ㅋ', 'k')); i += 1; continue
        if c == 'l':
            out.append(('C', 'ㄹ', 'l')); i += 1; continue
        if c == 'm':
            out.append(('C', 'ㅁ', 'm')); i += 1; continue
        if c == 'n':
            out.append(('C', 'ㄴ', 'n')); i += 1; continue
        if c == 'p':
            out.append(('C', 'ㅍ', 'p')); i += 1; continue
        if c == 'q':
            out.append(('C', 'ㅋ', 'q')); i += 1; continue
        if c == 'r':
            out.append(('C', 'ㄹ', 'r')); i += 1; continue
        if c == 's':
            out.append(('C', 'ㅅ', 's')); i += 1; continue
        if c == 't':
            out.append(('C', 'ㅌ', 't')); i += 1; continue
        if c == 'v':
            if precise: out.append(('OLD', V_OLD))
            else: out.append(('C', V_OLD, 'v'))
            i += 1; continue
        if c == 'w':
            wmap = {'a':'ㅘ','e':'ㅞ','i':'ㅟ','o':'ㅝ','u':'ㅜ'}
            if nxt in wmap:
                out.append(('C', 'ㅇ', 'w'))
                out.append(('SV', wmap[nxt]))
                i += 2; continue
            out.append(('C', 'ㅇ', 'w'))
            out.append(('V', 'ㅜ'))
            i += 1; continue
        if c == 'x':
            out.append(('X', None)); i += 1; continue
        if c == 'y':
            if nxt in Y_VOWEL_J:
                out.append(('C', 'ㅇ', 'y'))
                out.append(('SV', Y_VOWEL_J[nxt]))
                i += 2; continue
            out.append(('C', 'ㅇ', 'y'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 'z':
            out.append(('C', 'ㅈ', 'z')); i += 1; continue

        out.append(('LIT', s[i])); i += 1

    return out


def _intervocalic_l_post(phonemes):
    """Hangul mode only: intervocalic L doubling."""
    out2 = []
    for k, ph in enumerate(phonemes):
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('V', 'SV')
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_double'))
        else:
            out2.append(ph)
    return out2


ALLOW_AS_FINAL = {'ㄴ','ㅁ','ㄹ','ㅇ','ㅂ','ㄱ','ㅅ'}


def _next_is_vowel(phs, i):
    return i+1 < len(phs) and phs[i+1][0] in ('V','SV','NV')


def _assemble(phonemes, precise):
    syllables = []; i = 0; n = len(phonemes)
    while i < n:
        ph = phonemes[i]; kind = ph[0]
        if kind == 'V':
            syllables.append(_compose('ㅇ', ph[1])); i += 1; continue
        if kind == 'SV':
            syllables.append(_compose('ㅇ', ph[1])); i += 1; continue
        if kind == 'LIT':
            syllables.append(ph[1]); i += 1; continue
        if kind == 'NG_ASSIM':
            _add_jong_to_last(syllables, 'ㅇ'); i += 1; continue
        if kind == 'RR':
            _add_jong_to_last(syllables, 'ㄹ')
            if _next_is_vowel(phonemes, i):
                syllables.append(_compose('ㄹ', phonemes[i+1][1])); i += 2
            else:
                syllables.append(_compose('ㄹ', 'ㅡ')); i += 1
            continue
        if kind == 'X':
            if syllables and not _has_jong(syllables[-1]):
                _add_jong_to_last(syllables, 'ㄱ')
            if _next_is_vowel(phonemes, i):
                syllables.append(_compose('ㅅ', phonemes[i+1][1])); i += 2
            else:
                syllables.append(_compose('ㅅ', 'ㅡ')); i += 1
            continue
        if kind == 'OLD':
            old = ph[1]
            if _next_is_vowel(phonemes, i):
                syllables.append(old); syllables.append(_compose('ㅇ', phonemes[i+1][1]))
                i += 2
            elif (i+2 < n and phonemes[i+1][0] == 'C' and phonemes[i+2][0] in ('V','SV')):
                syllables.append(old); syllables.append(_compose(phonemes[i+1][1], phonemes[i+2][1]))
                i += 3
            elif i+1 >= n:
                syllables.append(old); i += 1
            else:
                syllables.append(old); syllables.append(_compose('ㅇ', 'ㅡ')); i += 1
            continue
        if kind == 'C':
            cho = ph[1]; src = ph[2] if len(ph) > 2 else ''
            if _next_is_vowel(phonemes, i):
                syllables.append(_compose(cho, phonemes[i+1][1])); i += 2; continue
            # 다음이 유음 (ㄹ initial) cluster면 → 으-syll (k/t/p/g 받침 안 함)
            next_is_liquid = (i+1 < n and phonemes[i+1][0] == 'C' and phonemes[i+1][1] == 'ㄹ')
            if next_is_liquid and src in ('t','k','p','g','c','q'):
                syllables.append(_compose(cho, 'ㅡ')); i += 1; continue
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ')); i += 1; continue
            if src in ('l','m','n','ny'):
                if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                    if _add_jong_to_last(syllables, cho):
                        i += 1; continue
                syllables.append(_compose(cho, 'ㅡ')); i += 1; continue
            if src in ('c','k','q','kh') and cho in ('ㅋ','ㅎ'):
                if cho == 'ㅋ' and syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㄱ'):
                        i += 1; continue
                syllables.append(_compose(cho, 'ㅡ')); i += 1; continue
            if src == 'p' and cho == 'ㅍ':
                if syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㅂ'):
                        i += 1; continue
                syllables.append(_compose('ㅍ', 'ㅡ')); i += 1; continue
            # g 자음 앞/어말 → ㄱ받침
            if src == 'g' and cho == 'ㄱ':
                if syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㄱ'):
                        i += 1; continue
                syllables.append(_compose('ㄱ', 'ㅡ')); i += 1; continue
            # t 자음 앞/어말 → ㅅ받침
            if src == 't' and cho == 'ㅌ':
                if syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㅅ'):
                        i += 1; continue
                syllables.append(_compose('ㅌ', 'ㅡ')); i += 1; continue
            syllables.append(_compose(cho, 'ㅡ')); i += 1; continue
        i += 1
    return ''.join(syllables)



# === jamo sequence (UHPS) ===
def _to_jamo_seq(phonemes):
    """phoneme list → jamo string. UHPS 1:1."""
    out = []
    for ph in phonemes:
        kind = ph[0]
        if kind in ('V', 'SV'):
            out.append(ph[1])
        elif kind == 'NV':
            out.append(ph[1]); out.append('ㆁ')
        elif kind == 'C':
            if ph[1] == 'ㅇ' and len(ph) > 2 and ph[2] in ('y','w','j','ll','ł','й','ñ','gn','nh','ny','sy'):
                pass
            else:
                out.append(ph[1])
        elif kind == 'OLD':
            out.append(ph[1])
        elif kind == 'RR':
            src = ph[2] if len(ph) > 2 else 'rr'
            if src == 'l_double':
                out.append('ㄹ')
            else:
                out.append('ㄹ'); out.append('ㄹ')
        elif kind == 'GEM':
            out.append(ph[1])
        elif kind == 'NG_ASSIM':
            out.append('ㆁ')
        elif kind == 'X':
            out.append('ㄱ'); out.append('ㅅ')
        elif kind == 'FUSED':
            ch = ph[1]
            if len(ch) == 1 and 0xAC00 <= ord(ch) <= 0xD7A3:
                base = ord(ch) - 0xAC00
                INI = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
                JNG = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
                JG = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
                cho = INI[base // 588]; jung = JNG[(base % 588) // 28]; jong = JG[base % 28]
                if cho != 'ㅇ': out.append(cho)
                out.append(jung)
                if jong: out.append(jong)
            else:
                out.append(ch)
        elif kind == 'LIT':
            out.append(ph[1])
        elif kind == 'LINK_R':
            out.append('ㄹ'); out.append(ph[1])
    return ''.join(out)


def transcribe_id(text, precise=True, mode='hangul', phonetic=False):
    """id → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-z]+$', part):
            out.append(part); continue
        phs_raw = _phonemize(part, precise)
        if mode == 'hangul':
            phs = _intervocalic_l_post(phs_raw)
            out.append(_assemble(phs, precise))
        elif mode == 'jamo':
            out.append(_to_jamo_seq(phs_raw))
        elif mode == 'spaced':
            out.append(' '.join(_to_jamo_seq(phs_raw)))
        else:
            raise ValueError(f"Unknown mode: {mode}")
    return ''.join(out)



    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-z]+$', part):
            out.append(part); continue
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


if __name__ == '__main__':
    tests = [
        ('Indonesia', '인도네시아', '인도네시아'),
        ('Jakarta', '자카르타', '자카르타'),
        ('Bali', '발리', '발리'),
        ('selamat', '셀라맛', '셀라맛'),
        ('terima kasih', '테리마 카시', '테리마 카시'),
        ('nasi', '나시', '나시'),
        ('goreng', '고렝', '고렝'),
        ('Singapura', '싱가푸라', '싱가푸라'),
        ('Surabaya', '수라바야', '수라바야'),
        ('Yogyakarta', '욕야카르타', '욕야카르타'),
        ('Sumatra', '수마트라', '수마트라'),
        ('rambutan', '람부탄', '람부탄'),
        ('orang', '오랑', '오랑'),
        ('cinta', '친타', '친타'),
        ('hujan', '후잔', '후잔'),
        ('Bandung', '반둥', '반둥'),
    ]
    print("=== INDONESIAN PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_id(inp, True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")
    print("\n=== INDONESIAN BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_id(inp, False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
