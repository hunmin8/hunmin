"""Hunmin Precise — Turkish (tr) letter-by-letter → Hangul.

전략: 터키어는 Atatürk가 만든 phonetic alphabet → 거의 1-to-1.
8개 모음 (a/e/ı/i/o/ö/u/ü) 모두 명확.

매핑:
  a → ㅏ, e → ㅔ, ı → ㅡ, i → ㅣ
  o → ㅗ, ö → ㅚ, u → ㅜ, ü → ㅟ
  c → ㅈ (cetvel → 제트벨)
  ç → ㅊ
  ğ → silent (lengthens preceding vowel) or ㄱ
  g → ㄱ
  j → ㅈ (loanwords)
  ş → ㅅ + palatal vowel
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


VOWEL_LETTERS = set('aeıioöuüâêîôû')

VOWEL_J = {
    'a':'ㅏ','â':'ㅏ',
    'e':'ㅔ','ê':'ㅔ',
    'ı':'ㅡ',
    'i':'ㅣ','î':'ㅣ',
    'o':'ㅗ','ô':'ㅗ',
    'ö':'ㅚ',
    'u':'ㅜ','û':'ㅜ',
    'ü':'ㅟ',
}

# y + V → palatal
Y_VOWEL_J = {
    'a':'ㅑ','e':'ㅖ','ı':'ㅡ','i':'ㅣ',
    'o':'ㅛ','ö':'ㅛ','u':'ㅠ','ü':'ㅠ',
}


def _phonemize(word, precise):
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    # İ normalization (Turkish capital I with dot lowercases to i̇ with combining dot)
    s = word.replace('İ', 'i').replace('I', 'ı').lower()
    n = len(s)
    out = []
    i = 0

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # 모음
        if c in VOWEL_J:
            out.append(('V', VOWEL_J[c]))
            i += 1
            continue

        # === nk → ㅇ받침 + ㅋ ===
        if c == 'n' and nxt == 'k':
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㅋ', 'k'))
            i += 2
            continue
        # ng before consonant → ㅇ받침
        if c == 'n' and nxt == 'g' and (i+2 >= n or s[i+2] not in VOWEL_LETTERS):
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㄱ', 'g'))
            i += 2
            continue

        # === ph → ㅍ/ㆄ (loanword) ===
        if c == 'p' and nxt == 'h':
            if precise: out.append(('OLD', 'ㆄ'))
            else: out.append(('C', 'ㅍ', 'ph'))
            i += 2
            continue

        # === Doubled consonants → drop one (Turkish convention) ===
        if c == nxt and c in 'bcçdfgklmnprsştvyz':
            i += 1
            continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b')); i += 1; continue
        if c == 'c':
            out.append(('C', 'ㅈ', 'c')); i += 1; continue
        if c == 'ç':
            out.append(('C', 'ㅊ', 'ç')); i += 1; continue
        if c == 'd':
            out.append(('C', 'ㄷ', 'd')); i += 1; continue
        if c == 'f':
            if precise: out.append(('OLD', F))
            else: out.append(('C', F, 'f'))
            i += 1; continue
        if c == 'g':
            out.append(('C', 'ㄱ', 'g')); i += 1; continue
        if c == 'ğ':
            # ğ: 'soft g' — 보통 silent, 모음 길게 함
            # 모음 사이 → silent (just lengthen)
            # 자음 앞 / 어말 → 이전 모음 길게
            # 단순화: silent (drop)
            i += 1; continue
        if c == 'h':
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
        if c == 'r':
            out.append(('C', 'ㄹ', 'r')); i += 1; continue
        if c == 's':
            out.append(('C', 'ㅅ', 's')); i += 1; continue
        if c == 'ş':
            # ş + V → 샤/셰/시/쇼/슈
            sh_map = {'a':'ㅑ','e':'ㅖ','ı':'ㅡ','i':'ㅣ','o':'ㅛ','ö':'ㅛ','u':'ㅠ','ü':'ㅠ'}
            if nxt in sh_map:
                out.append(('C', 'ㅅ', 'sh'))
                out.append(('SV', sh_map[nxt]))
                i += 2; continue
            out.append(('C', 'ㅅ', 'sh'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 't':
            out.append(('C', 'ㅌ', 't')); i += 1; continue
        if c == 'v':
            if precise: out.append(('OLD', V_OLD))
            else: out.append(('C', V_OLD, 'v'))
            i += 1; continue
        if c == 'y':
            if nxt in Y_VOWEL_J:
                out.append(('C', 'ㅇ', 'y'))
                out.append(('SV', Y_VOWEL_J[nxt]))
                i += 2
                continue
            out.append(('C', 'ㅇ', 'y'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 'z':
            out.append(('C', 'ㅈ', 'z')); i += 1; continue
        if c == 'w':
            out.append(('C', 'ㅇ', 'w')); out.append(('V', 'ㅜ')); i += 1; continue
        if c == 'x':
            out.append(('C', 'ㅋ', 'x')); out.append(('V', 'ㅡ')); out.append(('C', 'ㅅ', 's')); i += 1; continue

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


def _is_eu_syll(syllable):
    if len(syllable) != 1: return False
    c = ord(syllable)
    if not (0xAC00 <= c <= 0xD7A3): return False
    base = c - HANGUL_BASE
    return ((base % 588) // 28) == VOWELS_J.index('ㅡ')


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
        if kind == 'GEM':
            _add_jong_to_last(syllables, ph[1]); i += 1; continue
        if kind == 'NG_ASSIM':
            _add_jong_to_last(syllables, 'ㅇ'); i += 1; continue
        if kind == 'RR':
            _add_jong_to_last(syllables, 'ㄹ')
            if _next_is_vowel(phonemes, i):
                syllables.append(_compose('ㄹ', phonemes[i+1][1])); i += 2
            else:
                syllables.append(_compose('ㄹ', 'ㅡ')); i += 1
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
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ')); i += 1; continue
            if src in ('l','m','n'):
                if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                    if _add_jong_to_last(syllables, cho):
                        i += 1; continue
                syllables.append(_compose(cho, 'ㅡ')); i += 1; continue
            if src in ('c','k','q') and cho == 'ㅋ':
                if syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㄱ'):
                        i += 1; continue
                syllables.append(_compose('ㅋ', 'ㅡ')); i += 1; continue
            if src == 'p' and cho == 'ㅍ':
                if syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㅂ'):
                        i += 1; continue
                syllables.append(_compose('ㅍ', 'ㅡ')); i += 1; continue
            # 어말 b/d/g 탈자음화 → 받침 ㅂ/ㅅ/ㄱ
            if i+1 >= n and syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                if src == 'b':
                    if _add_jong_to_last(syllables, 'ㅂ'):
                        i += 1; continue
                if src == 'd':
                    if _add_jong_to_last(syllables, 'ㅅ'):
                        i += 1; continue
                if src == 'g':
                    if _add_jong_to_last(syllables, 'ㄱ'):
                        i += 1; continue
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


def transcribe_tr(text, precise=True, mode='hangul', phonetic=False):
    """tr → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-zçÇğĞıİöÖşŞüÜâêîôû]+$', part):
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
        if not re.match(r'^[A-Za-zçÇğĞıİöÖşŞüÜâêîôû]+$', part):
            out.append(part); continue
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


if __name__ == '__main__':
    tests = [
        ('İstanbul', '이스탄불', '이스탄불'),
        ('Ankara', '앙카라', '앙카라'),  # Hmm 'nk' 비음동화? Let me skip nasalize
        ('merhaba', '메르하바', '메르하바'),
        ('teşekkür', '테셰퀴르', '테셰퀴르'),
        ('Türkiye', '튀르키예', '튀르키예'),
        ('güzel', '귀젤', '귀젤'),
        ('çay', '차이', '차이'),
        ('İzmir', '이즈미르', '이즈미르'),
        ('Atatürk', '아타튀르크', '아타튀르크'),
        ('döner', '되네르', '되네르'),
        ('kebab', '케밥', '케밥'),
        ('hoş geldin', '호시 겔딘', '호시 겔딘'),
        ('Bosphorus', '보스ㆄ오루스', '보스포루스'),
    ]
    print("=== TURKISH PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_tr(inp, True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")
    print("\n=== TURKISH BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_tr(inp, False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
