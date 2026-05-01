"""Hunmin Precise — Dutch (nl) letter-by-letter → Hangul.

전략: Germanic, 독일어와 비슷하지만 단순.

주요 규칙:
  ij → 아이 (Hollander 'long ij')
  ei → 아이
  oe → 우
  ie → 이
  eu → 외
  ou/au → 아우
  uu → 위
  ee → 에 (long e)
  aa → 아 (long a)
  oo → 오 (long o)
  sch → ㅅ + ㅋ ('school' → 스콜) — 다른 언어와 차이
  ch → ㅎ (post-vocalic /x/)
  g → ㅎ (Dutch g is /x/, soft)
  v → ㅸ/ㅂ
  w → ㅸ/ㅂ
  j → 야/예/이/요/유 (semi-vowel)
  ng → ㅇ받침
  intervocalic l 이중화
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


VOWEL_LETTERS = set('aeiouyáéíóúäëïöü')


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

        # === 어말 -en → -언 (schwa). 단, monosyllabic word는 제외 ===
        if c == 'e' and nxt == 'n' and i+2 >= n:
            other_vowels = sum(1 for ch in word.lower()[:i] if ch in VOWEL_LETTERS)
            if other_vowels >= 1:
                out.append(('V', 'ㅓ'))
                out.append(('GEM', 'ㄴ'))
                i += 2
                continue

        # === Vowel digraphs ===
        di = c + nxt
        if di == 'ij':
            out.append(('V', 'ㅔ')); out.append(('V', 'ㅣ'))
            i += 2; continue
        if di == 'ei':
            out.append(('V', 'ㅔ')); out.append(('V', 'ㅣ'))
            i += 2; continue
        if di == 'oe':
            out.append(('V', 'ㅜ'))
            i += 2; continue
        if di == 'ie':
            out.append(('V', 'ㅣ'))
            i += 2; continue
        if di == 'eu':
            out.append(('V', 'ㅚ'))
            i += 2; continue
        if di in ('ou', 'au'):
            out.append(('V', 'ㅏ')); out.append(('V', 'ㅜ'))
            i += 2; continue
        # NIKL Dutch: long vowels (aa/ee/oo/uu) → 두 음절로 분리
        # maan 마안, zee 제, kooi 코위, muur 뮈르
        # (단, 'ee'/'oo' before single consonant final → single Korean vowel)
        if di == 'aa':
            out.append(('V', 'ㅏ')); out.append(('V', 'ㅏ')); i += 2; continue
        if di == 'ee':
            out.append(('V', 'ㅔ')); i += 2; continue
        if di == 'oo':
            out.append(('V', 'ㅗ')); i += 2; continue
        if di == 'uu':
            out.append(('V', 'ㅟ')); i += 2; continue
        if di == 'iu':
            out.append(('V', 'ㅣ')); out.append(('V', 'ㅜ')); i += 2; continue
        if di == 'ui':
            # ui → 아위 (Dutch /œy/ → 아위)
            out.append(('V', 'ㅏ')); out.append(('V', 'ㅟ')); i += 2; continue
        if di == 'aai':
            pass  # rare

        # === 단일 모음 ===
        single_v = {
            'a':'ㅏ','á':'ㅏ','ä':'ㅏ',
            'e':'ㅔ','é':'ㅔ','ë':'ㅔ',
            'i':'ㅣ','í':'ㅣ','ï':'ㅣ',
            'o':'ㅗ','ó':'ㅗ','ö':'ㅗ',
            'u':'ㅟ','ú':'ㅟ','ü':'ㅟ',
            'y':'ㅣ',
        }
        if c in single_v:
            out.append(('V', single_v[c]))
            i += 1; continue

        # === Trigraphs / Digraphs ===
        # sch → ㅅ + ㅋ ('school' → 스콜)
        if c == 's' and nxt == 'c' and nxt2 == 'h':
            out.append(('C', 'ㅅ', 's'))
            out.append(('V', 'ㅡ'))
            out.append(('C', 'ㅋ', 'k'))
            i += 3; continue
        # ch → ㅎ (post-vocalic /x/)
        if c == 'c' and nxt == 'h':
            out.append(('C', 'ㅎ', 'ch'))
            i += 2; continue
        # ng (어말 또는 자음 앞) → ㅇ받침
        if c == 'n' and nxt == 'g' and (i+2 >= n or s[i+2] not in VOWEL_LETTERS):
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㄱ', 'g'))
            i += 2; continue
        # nk → ㅇ받침 + ㅋ
        if c == 'n' and nxt == 'k':
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㅋ', 'k'))
            i += 2; continue

        # === Doubled consonants → drop ===
        if c == nxt and c in 'bcdfgklmnprstvz':
            i += 1; continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b')); i += 1; continue
        if c == 'c':
            if nxt in ('e','i','y'):
                out.append(('C', 'ㅅ', 'c'))
            else:
                out.append(('C', 'ㅋ', 'c'))
            i += 1; continue
        if c == 'd':
            # 자음 앞 d → ㅌ (devoicing, Eindhoven → 아인트호번)
            if nxt and nxt not in VOWEL_LETTERS and nxt not in 'rl':
                out.append(('C', 'ㅌ', 'd_devoiced'))
                i += 1; continue
            out.append(('C', 'ㄷ', 'd')); i += 1; continue
        if c == 'f':
            if precise: out.append(('OLD', F))
            else: out.append(('C', F, 'f'))
            i += 1; continue
        if c == 'g':
            # Dutch g = /x/ → ㅎ (Hollandic) or /ɣ/. Korean: ㅎ.
            out.append(('C', 'ㅎ', 'g')); i += 1; continue
        if c == 'h':
            if nxt in single_v or nxt in VOWEL_LETTERS:
                out.append(('C', 'ㅎ', 'h')); i += 1; continue
            i += 1; continue
        if c == 'j':
            ymap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ'}
            if nxt in ymap:
                out.append(('C', 'ㅇ', 'j'))
                out.append(('SV', ymap[nxt]))
                i += 2; continue
            out.append(('C', 'ㅇ', 'j'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
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
            # Dutch v = /v/ but often /f/. precise → ㅸ; basic → ㅂ
            if precise: out.append(('OLD', 'ㅸ'))
            else: out.append(('C', 'ㅂ', 'v'))
            i += 1; continue
        if c == 'w':
            # Dutch w = /ʋ/ ≈ /v/. precise → ㅸ; basic → ㅂ
            if precise: out.append(('OLD', 'ㅸ'))
            else: out.append(('C', 'ㅂ', 'w'))
            i += 1; continue
        if c == 'x':
            out.append(('X', None)); i += 1; continue
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


ALLOW_AS_FINAL = {'ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ'}


def _next_is_vowel(phs, i):
    return i+1 < len(phs) and phs[i+1][0] in ('V', 'SV', 'NV')


def _assemble(phonemes, precise):
    syllables = []
    i = 0
    n = len(phonemes)
    while i < n:
        ph = phonemes[i]; kind = ph[0]
        if kind == 'FUSED':
            syllables.append(ph[1]); i += 1; continue
        if kind == 'GEM':
            _add_jong_to_last(syllables, ph[1]); i += 1; continue
        if kind == 'V':
            syllables.append(_compose('ㅇ', ph[1])); i += 1; continue
        if kind == 'SV':
            syllables.append(_compose('ㅇ', ph[1])); i += 1; continue
        if kind == 'NV':
            syllables.append(_compose('ㅇ', ph[1], 'ㅇ')); i += 1; continue
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
            if not syllables:
                if _next_is_vowel(phonemes, i):
                    syllables.append(_compose('ㅅ', phonemes[i+1][1])); i += 2
                else:
                    syllables.append(_compose('ㅅ', 'ㅡ')); i += 1
            else:
                _add_jong_to_last(syllables, 'ㄱ')
                if _next_is_vowel(phonemes, i):
                    syllables.append(_compose('ㅅ', phonemes[i+1][1])); i += 2
                else:
                    syllables.append(_compose('ㅅ', 'ㅡ')); i += 1
            continue
        if kind == 'OLD':
            old = ph[1]
            if _next_is_vowel(phonemes, i):
                syllables.append(old)
                syllables.append(_compose('ㅇ', phonemes[i+1][1]))
                i += 2
            elif (i+2 < n and phonemes[i+1][0] == 'C' and phonemes[i+2][0] in ('V','SV','NV')):
                syllables.append(old)
                syllables.append(_compose(phonemes[i+1][1], phonemes[i+2][1]))
                i += 3
            else:
                syllables.append(old); syllables.append(_compose('ㅇ', 'ㅡ'))
                i += 1
            continue
        if kind == 'C':
            cho = ph[1]; src = ph[2] if len(ph) > 2 else ''
            if _next_is_vowel(phonemes, i):
                syllables.append(_compose(cho, phonemes[i+1][1]))
                i += 2; continue
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ')); i += 1; continue
            if src in ('l','m','n'):
                if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                    if _add_jong_to_last(syllables, cho):
                        i += 1; continue
                syllables.append(_compose(cho, 'ㅡ')); i += 1; continue
            # NIKL Dutch: 어말 무성 폐쇄음은 받침 흡수 X, 별도 음절 (kerk 케르크, dorp 도르프, park 파르크)
            if src in ('c','k','q') and cho == 'ㅋ':
                syllables.append(_compose('ㅋ', 'ㅡ')); i += 1; continue
            if src == 'p' and cho == 'ㅍ':
                syllables.append(_compose('ㅍ', 'ㅡ')); i += 1; continue
            # NIKL Dutch: 어말 'd' devoicing → ㅌ (wind 빈트, stad 스타트)
            if src == 'd' and i + 1 == len(phonemes):
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


def transcribe_nl(text, precise=True, mode='hangul', phonetic=False):
    """nl → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-záéíóúäëïöü]+$', part):
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
        if not re.match(r'^[A-Za-záéíóúäëïöü]+$', part):
            out.append(part); continue
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


if __name__ == '__main__':
    tests = [
        ('Amsterdam', '암스테르담', '암스테르담'),
        ('Holland', '홀란드', '홀란드'),
        ('school', '스콜', '스콜'),
        ('goedemorgen', '후데모르헌', '후데모르헌'),  # g=ㅎ
        ('Vincent', 'ㅸ인센트', '빈센트'),
        ('rijst', '레이스트', '레이스트'),
        ('koe', '쿠', '쿠'),
        ('huis', '하위스', '하위스'),
        ('vader', 'ㅸ아데르', '바데르'),
        ('moeder', '무데르', '무데르'),
        ('water', 'ㅸ아테르', '바테르'),
        ('Den Haag', '덴 하흐', '덴 하흐'),
        ('zee', '제', '제'),
        ('Nijmegen', '네이메헌', '네이메헌'),
        ('Eindhoven', '에인트호ㅸ언', '에인트호번'),
    ]
    print("=== DUTCH PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_nl(inp, True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")
    print("\n=== DUTCH BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_nl(inp, False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
