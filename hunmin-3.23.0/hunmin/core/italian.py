"""Hunmin Precise — Italian (it) letter-by-letter → Hangul.

전략: IPA 없음. spelling 기반 직접 매핑.
이탈리아어는 phonetic spelling 95%+ → letter rule + 음절 분석.

주요 규칙:
  ce/ci → 체/치 (/tʃ/)
  cia/cio/ciu → 차/초/추 (i silent palatalization)
  ge/gi → 제/지 (/dʒ/)
  gia/gio/giu → 자/조/주
  ch + V → 카/케/키/코/쿠 (/k/)
  gh + V → 가/게/기/고/구 (/g/)
  gn → 냐/뇨 (palatal n)
  gli → 리 (palatal l)
  sc + e/i → 셰/시 (/ʃ/)
  z, zz → ㅊ
  v → ㅸ (precise) / ㅂ (basic)
  doubled consonants → 받침 + 새 syllable (mamma → 맘마, pizza → 핏차)
  intervocalic l → V받침ㄹ + ㄹV (gelato → 젤라토)
  n + (hard g/k/q) → ㅇ받침 (n+e/i면 ㄴ받침 유지: angelo → 안젤로)
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
OLD_JAMO = {'ㆄ', 'ㅸ', 'ㅿ', 'ㆁ', 'ㆆ'}


def _compose(cho, jung, jong=''):
    if cho in INITIALS and jung in VOWELS_J:
        c = INITIALS.index(cho)
        j = VOWELS_J.index(jung)
        f = FINALS.index(jong) if jong in FINALS else 0
        return chr(HANGUL_BASE + c*588 + j*28 + f)
    return cho + jung + jong


def _add_jong_to_last(syllables, jong_jamo):
    if not syllables:
        return False
    last = syllables[-1]
    if len(last) == 1:
        c = ord(last)
        if 0xAC00 <= c <= 0xD7A3:
            base = c - HANGUL_BASE
            cho = base // 588
            jung = (base % 588) // 28
            jong = base % 28
            if jong == 0 and jong_jamo in FINALS:
                syllables[-1] = chr(HANGUL_BASE + cho*588 + jung*28 + FINALS.index(jong_jamo))
                return True
    syllables[-1] = last + jong_jamo
    return True


VOWEL_J = {
    'a':'ㅏ', 'e':'ㅔ', 'i':'ㅣ', 'o':'ㅗ', 'u':'ㅜ',
    'à':'ㅏ', 'è':'ㅔ', 'é':'ㅔ', 'ì':'ㅣ', 'í':'ㅣ',
    'ò':'ㅗ', 'ó':'ㅗ', 'ù':'ㅜ', 'ú':'ㅜ',
}
Y_VOWEL_J = {
    'a':'ㅑ', 'e':'ㅖ', 'i':'ㅣ', 'o':'ㅛ', 'u':'ㅠ',
    'à':'ㅑ', 'è':'ㅖ', 'é':'ㅖ', 'ì':'ㅣ', 'ò':'ㅛ', 'ù':'ㅠ',
}


def _phonemize(word, precise):
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    s = word
    n = len(s)
    out = []
    i = 0
    while i < n:
        c = s[i].lower()
        nxt = s[i+1].lower() if i+1 < n else ''
        nxt2 = s[i+2].lower() if i+2 < n else ''
        nxt3 = s[i+3].lower() if i+3 < n else ''

        if c in VOWEL_J:
            out.append(('V', VOWEL_J[c]))
            i += 1
            continue

        # === gli + V → 리 + V (palatal l), gli alone → 리이 ===
        if c == 'g' and nxt == 'l' and nxt2 == 'i':
            if nxt3 in VOWEL_J:
                # gli + a/e/o/u → 리 + V (skip i)
                out.append(('C', 'ㄹ', 'gli'))
                out.append(('V', 'ㅣ'))  # V to allow intervocalic l previous
                # Actually for famiglia: fa-mi-gli-a → 파-미-리-아 → with intervocalic L doubling on 'gli's ㄹ
                # We need: previous V (from mi) and current 리 with V_a coming after
                # Simpler: emit C ㄹ gli + V_a, skipping the i since gli's 'i' is silent
                # But user expected 파밀리아 has 리 (with i). So actually gli + a = 리 + 아 (separate, with i).
                # Wait 파밀리아: 파-밀-리-아 = pa-mil-li-a. So 'gli' acts as 'l + li'.
                # Let me emit: ('C', 'ㄹ', 'gli') + ('V', 'ㅣ') + ('V', V_jamo) — that's what I had.
                out.append(('V', VOWEL_J[nxt3]))
                i += 4
                continue
            else:
                out.append(('C', 'ㄹ', 'gli'))
                out.append(('V', 'ㅣ'))
                i += 3
                continue

        # === gn + V → 냐/녜/니/뇨/뉴 ===
        if c == 'g' and nxt == 'n':
            if nxt2 in Y_VOWEL_J:
                out.append(('C', 'ㄴ', 'gn'))
                out.append(('SV', Y_VOWEL_J[nxt2]))
                i += 3
                continue
            else:
                out.append(('C', 'ㄴ', 'gn'))
                out.append(('V', 'ㅣ'))
                i += 2
                continue

        # === sch + V → 스ㅋ + V ===
        if c == 's' and nxt == 'c' and nxt2 == 'h' and nxt3 in VOWEL_J:
            out.append(('C', 'ㅅ', 's'))
            out.append(('V', 'ㅡ'))
            out.append(('C', 'ㅋ', 'k'))
            out.append(('V', VOWEL_J[nxt3]))
            i += 4
            continue

        # === sci + V → 시 + V (palatal /ʃ/) ===
        if c == 's' and nxt == 'c' and nxt2 == 'i' and nxt3 in VOWEL_J:
            out.append(('C', 'ㅅ', 'sc'))
            out.append(('V', VOWEL_J[nxt3]))
            i += 4
            continue
        if c == 's' and nxt == 'c' and nxt2 in ('e','é','è'):
            out.append(('C', 'ㅅ', 'sc'))
            out.append(('SV', 'ㅖ'))
            i += 3
            continue
        if c == 's' and nxt == 'c' and nxt2 in ('i','í','ì'):
            out.append(('C', 'ㅅ', 'sc'))
            out.append(('V', 'ㅣ'))
            i += 3
            continue

        # === ch + V → 카/케/키/코/쿠 ===
        if c == 'c' and nxt == 'h':
            if nxt2 in VOWEL_J:
                out.append(('C', 'ㅋ', 'c'))
                out.append(('V', VOWEL_J[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㅋ', 'c'))
            i += 2
            continue
        # === gh + V → 가/게/기/고/구 ===
        if c == 'g' and nxt == 'h':
            if nxt2 in VOWEL_J:
                out.append(('C', 'ㄱ', 'g'))
                out.append(('V', VOWEL_J[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㄱ', 'g'))
            i += 2
            continue

        # === ci/gi + a/o/u (silent i palatalization) ===
        if c == 'c' and nxt == 'i' and nxt2 in ('a','o','u','à','ò','ù'):
            out.append(('C', 'ㅊ', 'c'))
            out.append(('V', VOWEL_J[nxt2]))
            i += 3
            continue
        if c == 'g' and nxt == 'i' and nxt2 in ('a','o','u','à','ò','ù'):
            out.append(('C', 'ㅈ', 'g'))
            out.append(('V', VOWEL_J[nxt2]))
            i += 3
            continue

        # === qu + V ===
        if c == 'q' and nxt == 'u':
            if nxt2 in VOWEL_J:
                out.append(('C', 'ㅋ', 'q'))
                out.append(('V', 'ㅜ'))
                out.append(('V', VOWEL_J[nxt2]))
                i += 3
                continue

        # === DOUBLED CONSONANTS (gemination) ===
        # cc + e/i (soft, /ttʃ/) → ㅅ받침. cc + 그외 → ㄱ받침.
        # gg + e/i (soft, /ddʒ/) → ㅅ받침. gg + 그외 → ㄱ받침.
        if c == 'c' and nxt == 'c':
            if nxt2 in ('e','é','è','i','í','ì'):
                out.append(('GEM', 'ㅅ'))
            else:
                out.append(('GEM', 'ㄱ'))
            i += 1
            continue
        if c == 'g' and nxt == 'g':
            if nxt2 in ('e','é','è','i','í','ì'):
                out.append(('GEM', 'ㅅ'))
            else:
                out.append(('GEM', 'ㄱ'))
            i += 1
            continue
        if c == nxt and c in 'bdklmnprstz':  # f/v 제외, c/g 별도 처리됨
            jong_map = {
                'b':'ㅂ', 'd':'ㅅ',
                'k':'ㄱ', 'l':'ㄹ', 'm':'ㅁ', 'n':'ㄴ', 'p':'ㅂ',
                'r':'ㄹ', 's':'ㅅ', 't':'ㅅ', 'z':'ㅅ',
            }
            jong = jong_map[c]
            out.append(('GEM', jong))
            i += 1
            continue
        # ff: precise mode → 단일 ㆄ로 (gemination 무시); basic → 단일 ㅍ
        if c == 'f' and nxt == 'f':
            i += 1
            continue
        # vv: 단일 v로
        if c == 'v' and nxt == 'v':
            i += 1
            continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b'))
            i += 1; continue
        if c == 'c':
            if nxt in ('e','é','è','i','í','ì'):
                out.append(('C', 'ㅊ', 'c'))
            else:
                out.append(('C', 'ㅋ', 'c'))
            i += 1; continue
        if c == 'd':
            out.append(('C', 'ㄷ', 'd'))
            i += 1; continue
        if c == 'f':
            if precise:
                out.append(('OLD', 'ㆄ'))
            else:
                out.append(('C', 'ㅍ', 'f'))
            i += 1; continue
        if c == 'g':
            if nxt in ('e','é','è','i','í','ì'):
                out.append(('C', 'ㅈ', 'g'))
            else:
                out.append(('C', 'ㄱ', 'g'))
            i += 1; continue
        if c == 'h':
            i += 1; continue
        if c == 'j':
            if nxt in Y_VOWEL_J:
                out.append(('C', 'ㅇ', 'j'))
                out.append(('SV', Y_VOWEL_J[nxt]))
                i += 2
                continue
            out.append(('C', 'ㅇ', 'j'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 'k':
            out.append(('C', 'ㅋ', 'k'))
            i += 1; continue
        if c == 'l':
            out.append(('C', 'ㄹ', 'l'))
            i += 1; continue
        if c == 'm':
            out.append(('C', 'ㅁ', 'm'))
            i += 1; continue
        if c == 'n':
            # n + hard g/k/q (g+a/o/u, k, q) → ㅇ받침
            # n + soft g (g+e/i) → ㄴ받침 유지
            if nxt == 'g' and nxt2 in ('e','é','è','i','í','ì','l','n'):
                # soft g 또는 gli/gn — n 그대로 유지
                out.append(('C', 'ㄴ', 'n'))
                i += 1
                continue
            if nxt in ('g', 'k', 'q'):
                out.append(('NG_ASSIM',))
                i += 1
                continue
            out.append(('C', 'ㄴ', 'n'))
            i += 1; continue
        if c == 'p':
            out.append(('C', 'ㅍ', 'p'))
            i += 1; continue
        if c == 'q':
            out.append(('C', 'ㅋ', 'q'))
            i += 1; continue
        if c == 'r':
            out.append(('C', 'ㄹ', 'r'))
            i += 1; continue
        if c == 's':
            out.append(('C', 'ㅅ', 's'))
            i += 1; continue
        if c == 't':
            out.append(('C', 'ㅌ', 't'))
            i += 1; continue
        if c == 'v':
            if precise:
                out.append(('OLD', V_OLD))
            else:
                out.append(('C', V_OLD, 'v'))
            i += 1; continue
        if c == 'w':
            wmap = {'a':'ㅘ','e':'ㅞ','i':'ㅟ','o':'ㅝ','u':'ㅜ'}
            if nxt in wmap:
                out.append(('C', 'ㅇ', 'w'))
                out.append(('SV', wmap[nxt]))
                i += 2
                continue
            out.append(('C', 'ㅇ', 'w'))
            out.append(('V', 'ㅜ'))
            i += 1; continue
        if c == 'x':
            out.append(('X', None))
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
            out.append(('C', 'ㅊ', 'z'))
            i += 1; continue

        out.append(('LIT', s[i]))
        i += 1

    return out


def _intervocalic_l_post(phonemes):
    """Hangul mode only: intervocalic L doubling (Italian convention same as Spanish)."""
    out2 = []
    for k, ph in enumerate(phonemes):
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] in ('l', 'gli')
                and k > 0 and phonemes[k-1][0] in ('V', 'SV')
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_double'))
        else:
            out2.append(ph)
    return out2


# === 음소 → 한글 ===
ALLOW_AS_FINAL = {'ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ'}


def _next_is_vowel(phonemes, i):
    return i+1 < len(phonemes) and phonemes[i+1][0] in ('V', 'SV')


def _assemble(phonemes, precise):
    syllables = []
    i = 0
    n = len(phonemes)

    while i < n:
        ph = phonemes[i]
        kind = ph[0]

        if kind == 'V':
            syllables.append(_compose('ㅇ', ph[1]))
            i += 1
            continue

        if kind == 'SV':
            syllables.append(_compose('ㅇ', ph[1]))
            i += 1
            continue

        if kind == 'LIT':
            syllables.append(ph[1])
            i += 1
            continue

        if kind == 'NG_ASSIM':
            _add_jong_to_last(syllables, 'ㅇ')
            i += 1
            continue

        if kind == 'GEM':
            _add_jong_to_last(syllables, ph[1])
            i += 1
            continue

        if kind == 'RR':
            _add_jong_to_last(syllables, 'ㄹ')
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                syllables.append(_compose('ㄹ', v))
                i += 2
            else:
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
            continue

        if kind == 'X':
            if not syllables:
                if _next_is_vowel(phonemes, i):
                    v = phonemes[i+1][1]
                    syllables.append(_compose('ㅅ', v))
                    i += 2
                else:
                    syllables.append(_compose('ㅅ', 'ㅡ'))
                    i += 1
            else:
                _add_jong_to_last(syllables, 'ㄱ')
                if _next_is_vowel(phonemes, i):
                    v = phonemes[i+1][1]
                    syllables.append(_compose('ㅅ', v))
                    i += 2
                else:
                    syllables.append(_compose('ㅅ', 'ㅡ'))
                    i += 1
            continue

        if kind == 'OLD':
            old = ph[1]
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                syllables.append(old)
                syllables.append(_compose('ㅇ', v))
                i += 2
            else:
                syllables.append(old)
                syllables.append(_compose('ㅇ', 'ㅡ'))
                i += 1
            continue

        if kind == 'C':
            cho = ph[1]
            src = ph[2] if len(ph) > 2 else ''
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                syllables.append(_compose(cho, v))
                i += 2
                continue
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
                continue
            if src in ('l', 'm', 'n', 'gn', 'gli'):
                if cho in ALLOW_AS_FINAL:
                    if _add_jong_to_last(syllables, cho):
                        i += 1
                        continue
                syllables.append(_compose(cho, 'ㅡ'))
                i += 1
                continue
            if src in ('c', 'k', 'q') and cho == 'ㅋ':
                if _add_jong_to_last(syllables, 'ㄱ'):
                    i += 1
                    continue
                syllables.append(_compose('ㅋ', 'ㅡ'))
                i += 1
                continue
            if src == 'p' and cho == 'ㅍ':
                if _add_jong_to_last(syllables, 'ㅂ'):
                    i += 1
                    continue
                syllables.append(_compose('ㅍ', 'ㅡ'))
                i += 1
                continue
            syllables.append(_compose(cho, 'ㅡ'))
            i += 1
            continue

        i += 1

    return ''.join(syllables)


# === jamo sequence (UHPS) ===
def _to_jamo_seq(phonemes):
    out = []
    for ph in phonemes:
        kind = ph[0]
        if kind in ('V', 'SV'):
            out.append(ph[1])
        elif kind == 'NV':
            out.append(ph[1]); out.append('ㆁ')
        elif kind == 'C':
            if ph[1] == 'ㅇ' and len(ph) > 2 and ph[2] in ('y','w','j','ll','ł'):
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
        elif kind == 'LIT':
            out.append(ph[1])
    return ''.join(out)


# === Public ===
def transcribe_it(text, precise=True, mode='hangul', phonetic=False):
    """Italian → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part:
            continue
        if not re.match(r'^[A-Za-zàèéìíòóùúüöä]+$', part):
            out.append(part)
            continue
        phs_raw = _phonemize(part, precise)
        if mode == 'hangul':
            phs = _intervocalic_l_post(phs_raw)
            han = _assemble(phs, precise)
            out.append(han)
        elif mode == 'jamo':
            out.append(_to_jamo_seq(phs_raw))
        elif mode == 'spaced':
            out.append(' '.join(_to_jamo_seq(phs_raw)))
        else:
            raise ValueError(f"Unknown mode: {mode}")
    return ''.join(out)


# === Test ===
if __name__ == '__main__':
    tests = [
        # (input, expected_precise, expected_basic)
        ('ciao', '차오', '차오'),
        ('grazie', '그라치에', '그라치에'),
        ('amore', '아모레', '아모레'),
        ('bambino', '밤비노', '밤비노'),
        ('gelato', '젤라토', '젤라토'),
        ('spaghetti', '스파겟티', '스파겟티'),
        ('mamma', '맘마', '맘마'),
        ('nonna', '논나', '논나'),
        ('formaggio', 'ㆄ오르맛조', '포르맛조'),
        ('gnocchi', '뇩키', '뇩키'),
        ('Roma', '로마', '로마'),
        ('Italia', '이탈리아', '이탈리아'),
        ('Milano', '밀라노', '밀라노'),
        ('Venezia', 'ㅸ에네치아', '베네치아'),
        ('Firenze', 'ㆄ이렌체', '피렌체'),
        ('Napoli', '나폴리', '나폴리'),
        ('Sicilia', '시칠리아', '시칠리아'),
        ('arrivederci', '알리ㅸ에데르치', '알리베데르치'),
        ('prego', '프레고', '프레고'),
        ('pizza', '핏차', '핏차'),
        ('caffè', '카ㆄ에', '카페'),
        ('bello', '벨로', '벨로'),
        ('famiglia', 'ㆄ아밀리아', '파밀리아'),
        ('bruschetta', '브루스켓타', '브루스켓타'),
        ('ciao bella', '차오 벨라', '차오 벨라'),
        ('Buongiorno', '부온조르노', '부온조르노'),
        ('angelo', '안젤로', '안젤로'),
        ('mangiare', '만자레', '만자레'),
        ('arancia', '아란차', '아란차'),
    ]

    print("=== ITALIAN PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_it(inp, precise=True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")

    print("\n=== ITALIAN BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_it(inp, precise=False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
