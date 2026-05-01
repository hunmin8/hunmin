"""Hunmin Precise — German (de) letter-by-letter → Hangul.

전략: IPA 없음. spelling 기반 직접 매핑.

주요 규칙:
  sch + V → 샤/셰/시/쇼/슈/etc. (palatal /ʃ/)
  ch (어말) after front V → 히, after back V → 흐
  ch + V → 헤/하/호 등
  tsch → ㅊ (어말 → 치)
  ck → ㄱ받침 + ㅋ
  ph/pf → ㆄ / ㅍ
  qu → 크ㅸ / 크ㅂ
  z → ㅊ
  w → ㅸ / ㅂ
  v → ㆄ / ㅍ (대부분 /f/)
  ß → ㅅ
  ä → 에, ö → 외, ü → 위
  ei/ai/ay/ey → 아이
  au → 아우
  eu/äu → 오이
  ie → 이 (long i)
  intervocalic l → V받침ㄹ + ㄹV (Schule → 슐레)
  doubled cons → drop second (German doesn't preserve gemination)
  word-final -er → 어 (Wagner → 바그너)
  word-final b/d/g → 으-syllable (브/드/크)
  OLD + C + V → OLD + CV (no 으 inserted)
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
    """마지막 syllable에 받침 추가. 이미 받침 있으면 False 반환 (호출자가 다른 처리 선택)."""
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
    return False


VOWEL_J = {
    'a':'ㅏ', 'e':'ㅔ', 'i':'ㅣ', 'o':'ㅗ', 'u':'ㅜ',
    'ä':'ㅔ', 'ö':'ㅚ', 'ü':'ㅟ', 'ÿ':'ㅟ',
    'á':'ㅏ', 'é':'ㅔ', 'í':'ㅣ', 'ó':'ㅗ', 'ú':'ㅜ',
}
FRONT_VS = set('eiäöüy')
BACK_VS = set('aou')

# sch + V → palatal Korean vowel
SCH_VOWEL = {
    'a':'ㅑ', 'e':'ㅖ', 'i':'ㅣ', 'o':'ㅛ', 'u':'ㅠ',
    'ä':'ㅖ', 'ö':'ㅚ', 'ü':'ㅟ',
}


def _phonemize(word, precise):
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    s = word
    n = len(s)
    out = []
    i = 0

    last_vowel_letter = None  # for ch context

    while i < n:
        c = s[i].lower()
        nxt = s[i+1].lower() if i+1 < n else ''
        nxt2 = s[i+2].lower() if i+2 < n else ''
        nxt3 = s[i+3].lower() if i+3 < n else ''

        # === Diphthongs ===
        di = c + nxt
        if di in ('ei','ai','ay','ey'):
            out.append(('V', 'ㅏ'))
            out.append(('V', 'ㅣ'))
            last_vowel_letter = 'i'
            i += 2
            continue
        if di == 'au':
            out.append(('V', 'ㅏ'))
            out.append(('V', 'ㅜ'))
            last_vowel_letter = 'u'
            i += 2
            continue
        if di in ('eu','äu'):
            out.append(('V', 'ㅗ'))
            out.append(('V', 'ㅣ'))
            last_vowel_letter = 'i'
            i += 2
            continue
        if di == 'ie':
            out.append(('V', 'ㅣ'))
            last_vowel_letter = 'i'
            i += 2
            continue

        # === Word-final '-er' → 어 (replaces V ㅔ + C ㄹ at end) ===
        if c == 'e' and nxt == 'r' and (i+2 >= n):
            out.append(('V', 'ㅓ'))
            last_vowel_letter = 'e'
            i += 2
            continue

        # 단일 모음
        if c in VOWEL_J:
            out.append(('V', VOWEL_J[c]))
            last_vowel_letter = c
            i += 1
            continue

        # === Trigraphs ===
        # tsch + V → ㅊ + V
        if c == 't' and nxt == 's' and nxt2 == 'c' and nxt3 == 'h':
            # tsch alone (어말) → 치
            if i+4 >= n:
                out.append(('C', 'ㅊ', 'tsch'))
                out.append(('V', 'ㅣ'))
                i += 4
                continue
            # tsch + V → ㅊ + V
            v4 = s[i+4].lower() if i+4 < n else ''
            if v4 in VOWEL_J:
                out.append(('C', 'ㅊ', 'tsch'))
                out.append(('V', VOWEL_J[v4]))
                i += 5
                last_vowel_letter = v4
                continue
            # tsch + 자음
            out.append(('C', 'ㅊ', 'tsch'))
            i += 4
            continue

        # sch + V → palatal Korean vowel
        if c == 's' and nxt == 'c' and nxt2 == 'h':
            if nxt3 in SCH_VOWEL:
                out.append(('C', 'ㅅ', 'sch'))
                out.append(('SV', SCH_VOWEL[nxt3]))
                last_vowel_letter = nxt3
                i += 4
                continue
            # sch + 자음 또는 어말 → 슈 (default)
            out.append(('C', 'ㅅ', 'sch'))
            out.append(('V', 'ㅠ'))
            i += 3
            continue

        # chs → ks
        if c == 'c' and nxt == 'h' and nxt2 == 's':
            out.append(('X', None))
            i += 3
            continue

        # === ch (context-dependent) ===
        if c == 'c' and nxt == 'h':
            # ch + V → ㅎ + V
            if nxt2 in VOWEL_J:
                out.append(('C', 'ㅎ', 'ch'))
                out.append(('V', VOWEL_J[nxt2]))
                last_vowel_letter = nxt2
                i += 3
                continue
            # ch alone (어말 또는 자음 앞)
            # after front vowel → 히 (ich → 이히)
            # after back vowel → 흐 (Bach → 바흐)
            if last_vowel_letter in BACK_VS:
                out.append(('C', 'ㅎ', 'ch'))
                out.append(('V', 'ㅡ'))
            else:
                out.append(('C', 'ㅎ', 'ch'))
                out.append(('V', 'ㅣ'))
            i += 2
            continue

        # ck → 받침ㄱ + ㅋ
        if c == 'c' and nxt == 'k':
            out.append(('GEM', 'ㄱ'))
            out.append(('C', 'ㅋ', 'k'))
            i += 2
            continue

        # ng (자음 앞 또는 어말) → ㅇ받침 + ㄱ syllable
        if c == 'n' and nxt == 'g' and (i+2 >= n or s[i+2].lower() not in VOWEL_J):
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㄱ', 'g'))
            i += 2
            continue
        # nk → ㅇ받침 + ㅋ syllable (Frankfurt → 프랑크)
        if c == 'n' and nxt == 'k':
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㅋ', 'k'))
            i += 2
            continue
        # nq → similar
        if c == 'n' and nxt == 'q':
            out.append(('NG_ASSIM',))
            out.append(('C', 'ㅋ', 'q'))
            i += 2
            continue

        # ph / pf → ㆄ / ㅍ
        if c == 'p' and nxt == 'h':
            if precise:
                out.append(('OLD', 'ㆄ'))
            else:
                out.append(('C', 'ㅍ', 'ph'))
            i += 2
            continue
        if c == 'p' and nxt == 'f':
            if precise:
                out.append(('OLD', 'ㆄ'))
            else:
                out.append(('C', 'ㅍ', 'pf'))
            i += 2
            continue

        # qu → ㅋ + ㅸ/ㅂ + V (Quelle → 크ㅸ엘레)
        if c == 'q' and nxt == 'u':
            out.append(('C', 'ㅋ', 'q'))
            out.append(('V', 'ㅡ'))
            if precise:
                out.append(('OLD', V_OLD))
            else:
                out.append(('C', V_OLD, 'v'))
            i += 2
            continue

        # th → ㅌ
        if c == 't' and nxt == 'h':
            out.append(('C', 'ㅌ', 't'))
            i += 2
            continue

        # === Doubled consonants → 단일 (German doesn't gemiate in pronunciation) ===
        if c == nxt and c in 'bdfgklmnprstvz':
            i += 1  # consume one
            continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b'))
            i += 1; continue
        if c == 'c':
            if nxt in FRONT_VS:
                out.append(('C', 'ㅊ', 'c'))
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
            out.append(('C', 'ㄱ', 'g'))
            i += 1; continue
        if c == 'h':
            if nxt in VOWEL_J:
                out.append(('C', 'ㅎ', 'h'))
                i += 1
                continue
            i += 1; continue  # silent h
        if c == 'j':
            ymap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ',
                    'ä':'ㅖ','ö':'ㅛ','ü':'ㅠ'}
            if nxt in ymap:
                out.append(('C', 'ㅇ', 'j'))
                out.append(('SV', ymap[nxt]))
                last_vowel_letter = nxt
                i += 2
                continue
            out.append(('C', 'ㅇ', 'j'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 'k':
            out.append(('C', 'ㅋ', 'k'))
            i += 1; continue
        if c == 'l':
            # 어말 'ln' or 'lm' → linking ㄹ rule (Köln → 쾰른)
            if nxt in ('n', 'm') and i+2 >= n:
                # l → ㄹ받침 to prev (via post-handling), then linking 른/름
                out.append(('C', 'ㄹ', 'l'))
                # GEM marker로 강제 받침: 그러면 l이 받침처럼 처리되고
                # 그 다음 n/m이 연결 'ㄹ'-onset 음절로 처리됨
                # 마커: ('LINK_RN' or 'LINK_RM') with the n/m 받침
                final_jong = 'ㄴ' if nxt == 'n' else 'ㅁ'
                out.append(('LINK_R', final_jong))
                i += 2
                continue
            out.append(('C', 'ㄹ', 'l'))
            i += 1; continue
        if c == 'm':
            out.append(('C', 'ㅁ', 'm'))
            i += 1; continue
        if c == 'n':
            out.append(('C', 'ㄴ', 'n'))
            i += 1; continue
        if c == 'p':
            out.append(('C', 'ㅍ', 'p'))
            i += 1; continue
        if c == 'q':
            out.append(('C', 'ㅋ', 'q'))
            i += 1; continue
        if c == 'r':
            # 어말 r (직전이 모음, 다음 없음) → 어 (모음, V ㅓ)
            if i+1 >= n and out and out[-1][0] in ('V', 'SV'):
                out.append(('V', 'ㅓ'))
                i += 1
                continue
            # r + l (cluster, e.g., Berlin): r → 르 + GEM ㄹ (받침)
            if nxt == 'l':
                out.append(('C', 'ㄹ', 'r'))
                out.append(('GEM', 'ㄹ'))
                i += 1
                continue
            out.append(('C', 'ㄹ', 'r'))
            i += 1; continue
        if c == 's':
            out.append(('C', 'ㅅ', 's'))
            i += 1; continue
        if c == 'ß':
            out.append(('C', 'ㅅ', 'ß'))
            i += 1; continue
        if c == 't':
            out.append(('C', 'ㅌ', 't'))
            i += 1; continue
        if c == 'v':
            if precise:
                out.append(('OLD', 'ㆄ'))
            else:
                out.append(('C', 'ㅍ', 'v'))
            i += 1; continue
        if c == 'w':
            if precise:
                out.append(('OLD', 'ㅸ'))
            else:
                out.append(('C', 'ㅂ', 'w'))
            i += 1; continue
        if c == 'x':
            out.append(('X', None))
            i += 1; continue
        if c == 'y':
            if nxt in VOWEL_J:
                ymap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ'}
                out.append(('C', 'ㅇ', 'y'))
                out.append(('SV', ymap.get(nxt, 'ㅣ')))
                i += 2
                continue
            out.append(('V', 'ㅟ'))
            i += 1; continue
        if c == 'z':
            out.append(('C', 'ㅊ', 'z'))
            i += 1; continue

        out.append(('LIT', s[i]))
        i += 1

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


# === 음소 → 한글 ===
ALLOW_AS_FINAL = {'ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ'}


def _next_is_vowel(phonemes, i):
    return i+1 < len(phonemes) and phonemes[i+1][0] in ('V', 'SV')


def _has_jong(syllable):
    """syllable이 받침을 가지고 있는지."""
    if len(syllable) != 1: return True  # 옛한글 등은 안전하게 'has_jong'으로 처리
    c = ord(syllable)
    if not (0xAC00 <= c <= 0xD7A3): return False
    return (c - HANGUL_BASE) % 28 != 0


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

        if kind == 'LINK_R':
            # 이전 ㄹ를 받침으로 추가 (이미 last syllable에 있음) + 새 ㄹ+ㅡ+jong 음절
            # actually: 마지막 syll에 ㄹ받침 추가 + ㄹㅡ+jong 추가
            jong = ph[1]
            # last syll에 ㄹ받침 추가
            _add_jong_to_last(syllables, 'ㄹ')
            # 새 ㄹ+ㅡ+jong 음절
            syllables.append(_compose('ㄹ', 'ㅡ', jong))
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
            # OLD + V → OLD + (ㅇ+V syllable)
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                syllables.append(old)
                syllables.append(_compose('ㅇ', v))
                i += 2
            # OLD + C + V → OLD + CV (no 으 inserted)
            elif (i+2 < n and phonemes[i+1][0] == 'C'
                  and phonemes[i+2][0] in ('V', 'SV')):
                next_c = phonemes[i+1]
                next_v = phonemes[i+2]
                cho = next_c[1]
                v = next_v[1]
                # Emit OLD then CV syllable
                syllables.append(old)
                syllables.append(_compose(cho, v))
                i += 3
            else:
                # OLD + 어말 → OLD + 으
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
            # 어말/자음 앞
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
                continue
            if src in ('l', 'm', 'n'):
                if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                    if _add_jong_to_last(syllables, cho):
                        i += 1
                        continue
                syllables.append(_compose(cho, 'ㅡ'))
                i += 1
                continue
            if src in ('c', 'k', 'q') and cho == 'ㅋ':
                if syllables and not _has_jong(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㄱ'):
                        i += 1
                        continue
                syllables.append(_compose('ㅋ', 'ㅡ'))
                i += 1
                continue
            if src in ('p', 'pf', 'ph') and cho == 'ㅍ':
                if syllables and not _has_jong(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㅂ'):
                        i += 1
                        continue
                syllables.append(_compose('ㅍ', 'ㅡ'))
                i += 1
                continue
            # 어말 b/d/g 탈자음화 (devoicing): b→프, d→트, g→크
            if i+1 >= n:
                if src == 'b' and cho == 'ㅂ':
                    syllables.append(_compose('ㅍ', 'ㅡ'))
                    i += 1
                    continue
                if src == 'd' and cho == 'ㄷ':
                    syllables.append(_compose('ㅌ', 'ㅡ'))
                    i += 1
                    continue
                if src == 'g' and cho == 'ㄱ':
                    syllables.append(_compose('ㅋ', 'ㅡ'))
                    i += 1
                    continue
            # 그 외: 으-syllable
            syllables.append(_compose(cho, 'ㅡ'))
            i += 1
            continue

        i += 1

    return ''.join(syllables)


# === Public ===

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


def transcribe_de(text, precise=True, mode='hangul', phonetic=False):
    """de → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-zäöüÄÖÜßéáíóú]+$', part):
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
        if not part:
            continue
        if not re.match(r'^[A-Za-zäöüÄÖÜßéáíóú]+$', part):
            out.append(part)
            continue
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


# === Test ===
if __name__ == '__main__':
    tests = [
        ('Schule', '슐레', '슐레'),
        ('Bach', '바흐', '바흐'),
        ('ich', '이히', '이히'),
        ('Deutsch', '도이치', '도이치'),
        ('Wagner', 'ㅸ아그너', '바그너'),
        ('Berlin', '베를린', '베를린'),
        ('München', '뮌헨', '뮌헨'),
        ('Frankfurt', 'ㆄ랑크ㆄ우르트', '프랑크푸르트'),
        ('Köln', '쾰른', '쾰른'),
        ('Hamburg', '함부르크', '함부르크'),
        ('Pfeffer', 'ㆄ에ㆄ어', '페퍼'),
        ('Quelle', '크ㅸ엘레', '크벨레'),
        ('Zeit', '차이트', '차이트'),
        ('Volk', 'ㆄ올크', '폴크'),
        ('vier', 'ㆄ이어', '피어'),  # ie + r ending
        ('Mädchen', '메드헨', '메드헨'),
        ('schön', '쇤', '쇤'),
        ('groß', '그로스', '그로스'),
        ('weiß', 'ㅸ아이스', '바이스'),
        ('Auto', '아우토', '아우토'),
        ('Eis', '아이스', '아이스'),
        ('Haus', '하우스', '하우스'),
        ('Wahrheit', 'ㅸ아르하이트', '바르하이트'),
        ('Kuchen', '쿠헨', '쿠헨'),
    ]

    print("=== GERMAN PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_de(inp, precise=True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")

    print("\n=== GERMAN BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_de(inp, precise=False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
