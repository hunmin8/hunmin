"""Hunmin Precise — Spanish (es) letter-by-letter → Hangul.

전략: IPA 없음. spelling 기반 직접 매핑.
스페인어는 phonetic spelling 95%+ → letter rule + 음절 분석으로 충분.

Old Hangul (precise mode):
  f → ㆄ + (ㅇ+V 음절)
  v → ㅸ + (ㅇ+V 음절)
  z → ㅿ + (ㅇ+V 음절)
basic mode: f→ㅍ, v→ㅂ, z→ㅅ (음절 결합 가능)

Conventions:
- 'l' between vowels → 이중화: V받침ㄹ + ㄹV (familia → 파밀리아)
- 'r' final/pre-cons → 르 syllable (separate, NOT 받침) (señor → 세뇨르)
- 'l' final/pre-cons → 받침 ㄹ (papel → 파펠)
- 'n' before g/k/q → ㅇ받침 (nasal assim) (pingüino → 핑구...)
- 어말 b/d/g/p/t/k → 으-syllable (Madrid → 마드리드)
- 어말 m/n/l → 받침
- 어말 s/r → 으-syllable (스/르)
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
    """마지막 syllable에 받침 추가 (가능시).

    한글 syllable이고 받침이 비어있으면: 받침 추가
    한글 syllable인데 받침 있으면: 새 jamo로 추가
    한글 syllable 아니면 (jamo 등): jamo 그대로 append
    """
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
    # syllable이 한글이 아니거나 이미 받침 있음 → 새로 jamo 추가
    syllables[-1] = last + jong_jamo
    return True


# === 모음 매핑 ===
VOWEL_J = {
    'a':'ㅏ', 'e':'ㅔ', 'i':'ㅣ', 'o':'ㅗ', 'u':'ㅜ',
    'á':'ㅏ', 'é':'ㅔ', 'í':'ㅣ', 'ó':'ㅗ', 'ú':'ㅜ', 'ü':'ㅜ',
}
Y_VOWEL_J = {
    'a':'ㅑ', 'e':'ㅖ', 'i':'ㅣ', 'o':'ㅛ', 'u':'ㅠ',
    'á':'ㅑ', 'é':'ㅖ', 'í':'ㅣ', 'ó':'ㅛ', 'ú':'ㅠ',
}


# === Phonemize: Spanish word → list of phoneme tuples ===
# Phoneme tuple format: (kind, value, [src])
#   ('V', vowel_jamo)              일반 모음
#   ('SV', semi_vowel_jamo)        반모음 (ll/y/ñ + V)
#   ('C', cho_jamo, src_letter)    자음 (src='l' for L, 'r' for R, etc.)
#   ('OLD', old_jamo)              옛한글 (f/v/z)
#   ('NG_ASSIM',)                  n before g/k/q (ㅇ 받침)
#   ('RR', 'ㄹ')                   double-r (강제 받침 + 새 ㄹ syllable)
#   ('X', None)                    x (k+s)
#   ('LIT', char)                  literal

def _phonemize(word, precise):
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'
    Z_OLD = 'ㅿ' if precise else 'ㅅ'

    s = word
    n = len(s)
    out = []
    i = 0
    while i < n:
        c = s[i].lower()
        nxt = s[i+1].lower() if i+1 < n else ''
        nxt2 = s[i+2].lower() if i+2 < n else ''

        # 모음
        if c in VOWEL_J:
            out.append(('V', VOWEL_J[c]))
            i += 1
            continue

        # === DIGRAPHS ===
        if c == 'c' and nxt == 'h':
            out.append(('C', 'ㅊ', 'ch'))
            i += 2
            continue
        if c == 'l' and nxt == 'l':
            # ll → semi-vowel y
            if nxt2 in Y_VOWEL_J:
                out.append(('C', 'ㅇ', 'll'))
                out.append(('SV', Y_VOWEL_J[nxt2]))
                i += 3
                continue
            else:
                out.append(('C', 'ㅇ', 'll'))
                out.append(('V', 'ㅣ'))
                i += 2
                continue
        if c == 'r' and nxt == 'r':
            # rr → trill: 받침ㄹ + 새 ㄹV
            out.append(('RR', 'ㄹ'))
            i += 2
            continue
        if c == 'q' and nxt == 'u' and nxt2 in ('e','i','é','í'):
            out.append(('C', 'ㅋ', 'q'))
            i += 2  # leave nxt2 vowel
            continue
        if c == 'q' and nxt == 'u' and nxt2 in VOWEL_J:
            # qua/quo: ㅋ + 우 + V (분리)
            out.append(('C', 'ㅋ', 'q'))
            out.append(('V', 'ㅜ'))
            out.append(('V', VOWEL_J[nxt2]))
            i += 3
            continue
        if c == 'g' and nxt == 'u' and nxt2 in ('e','i','é','í'):
            out.append(('C', 'ㄱ', 'g'))
            i += 2
            continue
        if c == 'g' and nxt == 'ü':
            # gü+V: ㄱ + 우 + V (분리, 우 발음)
            out.append(('C', 'ㄱ', 'g'))
            out.append(('V', 'ㅜ'))
            if nxt2 in VOWEL_J:
                out.append(('V', VOWEL_J[nxt2]))
                i += 3
            else:
                i += 2
            continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b'))
            i += 1; continue
        if c == 'c':
            if nxt in ('e','i','é','í'):
                out.append(('C', 'ㅅ', 'c'))
            else:
                out.append(('C', 'ㅋ', 'c'))
            i += 1; continue
        if c == 'd':
            out.append(('C', 'ㄷ', 'd'))
            i += 1; continue
        if c == 'f':
            if precise:
                out.append(('OLD', F))
            else:
                out.append(('C', F, 'f'))
            i += 1; continue
        if c == 'g':
            if nxt in ('e','i','é','í'):
                out.append(('C', 'ㅎ', 'g'))
            else:
                out.append(('C', 'ㄱ', 'g'))
            i += 1; continue
        if c == 'h':
            i += 1; continue  # silent
        if c == 'j':
            out.append(('C', 'ㅎ', 'j'))
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
            # n before g/k/q → nasal assim (ㅇ받침)
            if nxt in ('g', 'k', 'q'):
                out.append(('NG_ASSIM',))
                i += 1
                continue
            out.append(('C', 'ㄴ', 'n'))
            i += 1; continue
        if c == 'ñ':
            if nxt in Y_VOWEL_J:
                out.append(('C', 'ㄴ', 'ñ'))
                out.append(('SV', Y_VOWEL_J[nxt]))
                i += 2
                continue
            else:
                out.append(('C', 'ㄴ', 'ñ'))
                out.append(('V', 'ㅣ'))
                i += 1
                continue
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
            # w + V (rare)
            wmap = {'a':'ㅘ','e':'ㅞ','i':'ㅟ','o':'ㅝ','u':'ㅜ',
                    'á':'ㅘ','é':'ㅞ','í':'ㅟ','ó':'ㅝ','ú':'ㅜ'}
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
            if precise:
                out.append(('OLD', Z_OLD))
            else:
                out.append(('C', Z_OLD, 'z'))
            i += 1; continue

        out.append(('LIT', s[i]))
        i += 1

    return out


def _intervocalic_l_post(phonemes):
    """Post-pass for hangul mode only: intervocalic L doubling.

    'C ㄹ l' between V/SV and V/SV → convert to RR (Korean orthographic convention).
    NOT applied in jamo mode (phonologically inaccurate).
    """
    out2 = []
    for k, ph in enumerate(phonemes):
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('V', 'SV')
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_double'))  # marker: artificial doubling
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
            v = ph[1]
            syllables.append(_compose('ㅇ', v))
            i += 1
            continue

        if kind == 'SV':
            # SV 단독이 오면 (이전이 자음이 아니었음): ㅇ + SV
            syllables.append(_compose('ㅇ', ph[1]))
            i += 1
            continue

        if kind == 'LIT':
            syllables.append(ph[1])
            i += 1
            continue

        if kind == 'NG_ASSIM':
            # 이전 syllable에 ㅇ받침
            _add_jong_to_last(syllables, 'ㅇ')
            i += 1
            continue

        if kind == 'RR':
            # 받침ㄹ + 다음 phoneme이 V면 ㄹV syllable
            _add_jong_to_last(syllables, 'ㄹ')
            if _next_is_vowel(phonemes, i):
                vph = phonemes[i+1]
                v = vph[1]
                syllables.append(_compose('ㄹ', v))
                i += 2
            else:
                # rr 뒤 자음 (드뭄)
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
            continue

        if kind == 'X':
            # ks: 어두 → ㅅ+V; 어중/어말 → 받침ㄱ + ㅅ+V or 으-syll
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
            # OLD + V/SV → "ㆄ" + 한글syll(ㅇ+V)
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                syllables.append(old)
                syllables.append(_compose('ㅇ', v))
                i += 2
            else:
                # OLD + 자음 또는 어말 → "ㆄ" + 으 syllable
                syllables.append(old)
                syllables.append(_compose('ㅇ', 'ㅡ'))
                i += 1
            continue

        if kind == 'C':
            cho = ph[1]
            src = ph[2] if len(ph) > 2 else ''
            # 다음이 V/SV → CV syllable
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                syllables.append(_compose(cho, v))
                i += 2
                continue
            # 어말 또는 자음 앞: 받침 vs 으-syllable
            # r → 항상 르 syllable (Korean Spanish 표기법)
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
                continue
            # l, m, n → 받침 (가능 시)
            if src in ('l', 'm', 'n', 'ñ', 'll'):
                if cho in ALLOW_AS_FINAL:
                    if _add_jong_to_last(syllables, cho):
                        i += 1
                        continue
                # fallback
                syllables.append(_compose(cho, 'ㅡ'))
                i += 1
                continue
            # c/k/q (/k/ stop) before consonant → ㄱ받침
            if src in ('c', 'k', 'q') and cho == 'ㅋ':
                if _add_jong_to_last(syllables, 'ㄱ'):
                    i += 1
                    continue
                syllables.append(_compose('ㅋ', 'ㅡ'))
                i += 1
                continue
            # p (/p/ stop) before consonant → ㅂ받침
            if src == 'p' and cho == 'ㅍ':
                if _add_jong_to_last(syllables, 'ㅂ'):
                    i += 1
                    continue
                syllables.append(_compose('ㅍ', 'ㅡ'))
                i += 1
                continue
            # 그 외 자음: 으-syllable
            syllables.append(_compose(cho, 'ㅡ'))
            i += 1
            continue

        # fallback
        i += 1

    return ''.join(syllables)


# === jamo sequence output ===

def _to_jamo_seq(phonemes):
    """phoneme list → jamo string (UHPS).

    음절 합성 무시. phoneme 1개 = jamo 1개 (또는 GEM/NG_ASSIM 처리).
    """
    out = []
    for ph in phonemes:
        kind = ph[0]
        if kind == 'V':
            out.append(ph[1])
        elif kind == 'SV':
            out.append(ph[1])
        elif kind == 'NV':
            # Nasal vowel: V + ㆁ (UHPS: ㆁ는 nasal 마커)
            out.append(ph[1])
            out.append('ㆁ')
        elif kind == 'C':
            # ㅇ는 placeholder (모음 단독 음절 표시) → jamo 모드에선 skip
            if ph[1] == 'ㅇ' and len(ph) > 2 and ph[2] in ('y', 'w', 'j', 'll', 'ł'):
                # semi-vowel placeholder: skip (다음 SV가 palatal 정보 가짐)
                pass
            else:
                out.append(ph[1])
        elif kind == 'OLD':
            out.append(ph[1])
        elif kind == 'RR':
            # Real geminate (rr) → ㄹㄹ
            # Artificial doubling (l_double from post-pass) → ㄹ
            src = ph[2] if len(ph) > 2 else 'rr'
            if src == 'l_double':
                out.append('ㄹ')
            else:
                out.append('ㄹ')
                out.append('ㄹ')
        elif kind == 'GEM':
            # Real geminate: emit jong jamo (다음 C가 같은 자모를 emit하므로 합쳐서 doubled)
            out.append(ph[1])
        elif kind == 'NG_ASSIM':
            out.append('ㆁ')
        elif kind == 'X':
            # ks → ㄱㅅ
            out.append('ㄱ')
            out.append('ㅅ')
        elif kind == 'LIT':
            out.append(ph[1])
    return ''.join(out)


# === Public ===
def transcribe_es(text, precise=True, mode='hangul', phonetic=False):
    """Spanish → Hangul.

    mode:
      'hangul'  → 음절 합성 (사람 읽기): 올라
      'jamo'    → jamo seq (ML 입력): ㅗㄹㅏ
      'spaced'  → spaced jamo: ㅗ ㄹ ㅏ
    """
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part:
            continue
        if not re.match(r'^[A-Za-zñÑáéíóúüÁÉÍÓÚÜ]+$', part):
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
            jamo = _to_jamo_seq(phs_raw)
            out.append(' '.join(jamo))
        else:
            raise ValueError(f"Unknown mode: {mode}")
    return ''.join(out)


# === Test ===
if __name__ == '__main__':
    tests = [
        # (input, expected_precise, expected_basic)
        ('hola', '올라', '올라'),
        ('gracias', '그라시아스', '그라시아스'),
        ('España', '에스파냐', '에스파냐'),
        ('México', '멕시코', '멕시코'),
        ('cinco', '신코', '신코'),
        ('queso', '케소', '케소'),
        ('guerra', '겔라', '겔라'),
        ('llamo', '야모', '야모'),
        ('me llamo Juan', '메 야모 후안', '메 야모 후안'),
        ('Buenos días', '부에노스 디아스', '부에노스 디아스'),
        ('señor', '세뇨르', '세뇨르'),
        ('chico', '치코', '치코'),
        ('Madrid', '마드리드', '마드리드'),
        ('Barcelona', '바르셀로나', '바르셀로나'),
        ('amigo', '아미고', '아미고'),
        ('familia', 'ㆄ아밀리아', '파밀리아'),
        ('zapato', 'ㅿ아파토', '사파토'),
        ('vino', 'ㅸ이노', '비노'),
        ('feliz', 'ㆄ엘리ㅿ으', '펠리스'),
        ('Cervantes', '세르ㅸ안테스', '세르반테스'),
        ('Juan', '후안', '후안'),
        ('papel', '파펠', '파펠'),
        ('niño', '니뇨', '니뇨'),
        ('agua', '아구아', '아구아'),
        ('pingüino', '핑구이노', '핑구이노'),
        ('Argentina', '아르헨티나', '아르헨티나'),
        ('rojo', '로호', '로호'),
        ('rosa', '로사', '로사'),
        ('perro', '펠로', '펠로'),  # rr 받침ㄹ+ㄹ로 = 펠로
    ]

    print("=== PRECISE (옛한글) ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_es(inp, precise=True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<20} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")

    print("\n=== BASIC (표준 한글만) ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_es(inp, precise=False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<20} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
