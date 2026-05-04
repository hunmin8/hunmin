"""Hunmin Precise — Portuguese (pt) letter-by-letter → Hangul.

전략: 유럽 포르투갈어 기준 (브라질도 거의 호환). 비음화 + Romance 룰.

주요 규칙:
  ã, õ → 비음 모음 (ㅏㅇ, ㅗㅇ)
  ão, ãe, õe → 디프통 비음 (앙, 앵, 옹/오잉)
  am/em/im/om/um (어말 또는 자음 앞) → 앙/엥/잉/옹/웅
  ç → ㅅ
  ch → 샤/셰/시/쇼/슈 (palatal)
  nh → 냐/뇨 (palatal n, like Spanish ñ)
  lh → 리아 (palatal l)
  rr → ㄹ (intervocalic doubling)
  ce/ci → 세/시 (/s/)
  ge/gi → 제/지 (/ʒ/)
  qu + e/i → 케/키 (silent u)
  gu + e/i → 게/기 (silent u)
  v → ㅸ/ㅂ
  f → ㆄ/ㅍ
  z → ㅈ
  intervocalic l 이중화 (Spanish style)
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
        c = INITIALS.index(cho)
        j = VOWELS_J.index(jung)
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


VOWEL_LETTERS = set('aeiouáéíóúâêôãõàèìòùyAEIOUÁÉÍÓÚÂÊÔÃÕÀÈÌÒÙY')


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

        # === 비음 디프통 ===
        # ão → 앙 (single nasalized syllable)
        if c == 'ã' and nxt == 'o':
            out.append(('NV', 'ㅏ'))
            i += 2
            continue
        # ãe → 앵
        if c == 'ã' and nxt == 'e':
            out.append(('NV', 'ㅐ'))
            i += 2
            continue
        # õe → 오잉 (외 + 이?) — 외래어 표기법: 오잉
        if c == 'õ' and nxt == 'e':
            out.append(('NV', 'ㅗ'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue
        # ã alone → ㅏㅇ
        if c == 'ã':
            out.append(('NV', 'ㅏ'))
            i += 1
            continue
        # õ alone → ㅗㅇ
        if c == 'õ':
            out.append(('NV', 'ㅗ'))
            i += 1
            continue

        # === 비음화 (am/em/im/om/um + 어말만). 단, 'nh' 디그래프면 NOT. ===
        # v3.38: NIKL pt — mid-word V+m/n+cons는 자음을 그대로 받침으로 흡수
        # (montanha 몬타냐, Coimbra 코임브라, samba 삼바). 어말 -m/-n만 비음 모음.
        def _is_nasal_context(after_idx):
            """V+m/n at word-end → nasal vowel (NV)."""
            return after_idx >= n

        if c in ('a','á','â','à') and nxt in ('m','n') and _is_nasal_context(i+2):
            out.append(('NV', 'ㅏ'))
            i += 2
            continue
        if c in ('e','é','ê','è') and nxt in ('m','n') and _is_nasal_context(i+2):
            out.append(('NV', 'ㅔ'))
            i += 2
            continue
        if c in ('i','í','ì') and nxt in ('m','n') and _is_nasal_context(i+2):
            out.append(('NV', 'ㅣ'))
            i += 2
            continue
        if c in ('o','ó','ô','ò') and nxt in ('m','n') and _is_nasal_context(i+2):
            out.append(('NV', 'ㅗ'))
            i += 2
            continue
        if c in ('u','ú','ù') and nxt in ('m','n') and _is_nasal_context(i+2):
            out.append(('NV', 'ㅜ'))
            i += 2
            continue

        # === 단일 모음 ===
        single_v = {
            'a':'ㅏ','á':'ㅏ','â':'ㅏ','à':'ㅏ',
            'e':'ㅔ','é':'ㅔ','ê':'ㅔ','è':'ㅔ',
            'i':'ㅣ','í':'ㅣ','ì':'ㅣ',
            'o':'ㅗ','ó':'ㅗ','ô':'ㅗ','ò':'ㅗ',
            'u':'ㅜ','ú':'ㅜ','ù':'ㅜ',
            'y':'ㅣ',
        }
        if c in single_v:
            # NIKL Brazilian: word-final unstressed 'o' → ㅜ (mercado 메르카두, queijo 케이주)
            if c == 'o' and i + 1 == n:
                out.append(('V', 'ㅜ'))
            else:
                out.append(('V', single_v[c]))
            i += 1
            continue

        # === Digraphs ===
        # ch + V → 샤/셰/시/쇼/슈 (palatal /ʃ/)
        if c == 'c' and nxt == 'h':
            sh_map = {'a':'ㅑ','e':'ㅖ','é':'ㅖ','ê':'ㅖ','i':'ㅣ','o':'ㅛ','ô':'ㅛ','u':'ㅠ'}
            if nxt2 in sh_map:
                out.append(('C', 'ㅅ', 'sh'))
                out.append(('SV', sh_map[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㅅ', 'sh'))
            i += 2
            continue
        # nh + V → 냐/녜/...
        if c == 'n' and nxt == 'h':
            ymap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ'}
            if nxt2 in ymap:
                out.append(('C', 'ㄴ', 'nh'))
                # Brazilian: nh + word-final 'o' → 뉴 (caminho 카미뉴, vinho 비뉴)
                if nxt2 == 'o' and i + 3 == n:
                    out.append(('SV', 'ㅠ'))
                else:
                    out.append(('SV', ymap[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㄴ', 'nh'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue
        # v3.38: lh + V → ㄹ받침 to prev + ㄹ + V (intervocalic l doubling pattern)
        # bacalhau 바칼라우, trabalho 트라발류 (어말 lho → ㄹ+ㅠ palatal)
        if c == 'l' and nxt == 'h':
            if nxt2 in single_v:
                out.append(('RR', 'ㄹ', 'lh'))
                if nxt2 == 'o' and i + 3 == n:
                    out.append(('SV', 'ㅠ'))  # 어말 -lho → 류
                else:
                    out.append(('V', single_v[nxt2]))
                i += 3
                continue
            out.append(('RR', 'ㄹ', 'lh'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue
        # qu + e/i → ㅋ + V (silent u)
        if c == 'q' and nxt == 'u' and nxt2 in ('e','é','ê','i','í'):
            out.append(('C', 'ㅋ', 'q'))
            out.append(('V', single_v[nxt2]))
            i += 3
            continue
        if c == 'q' and nxt == 'u':
            # qua → 쿠아 (separate)
            out.append(('C', 'ㅋ', 'q'))
            out.append(('V', 'ㅜ'))
            i += 2
            continue
        # gu + e/i → ㄱ + V (silent u)
        if c == 'g' and nxt == 'u' and nxt2 in ('e','é','ê','i','í'):
            out.append(('C', 'ㄱ', 'g'))
            out.append(('V', single_v[nxt2]))
            i += 3
            continue

        # v3.38: 어말 'de'/'ve' → d/v + ㅡ (reduced 'e'; cidade 시다드, Algarve 알가르브, saudade 사우다드)
        if c == 'd' and nxt == 'e' and i + 2 == n:
            out.append(('C', 'ㄷ', 'd'))
            out.append(('V', 'ㅡ'))
            i += 2; continue
        if c == 'v' and nxt == 'e' and i + 2 == n:
            if precise:
                out.append(('OLD', V_OLD))
            else:
                out.append(('C', V_OLD, 'v'))
            out.append(('V', 'ㅡ'))
            i += 2; continue

        # v3.38: ti → ㅊ + ㅣ (Brazilian palatal; Curitiba 쿠리치바)
        if c == 't' and nxt == 'i':
            out.append(('C', 'ㅊ', 'ti'))
            out.append(('V', 'ㅣ'))
            i += 2; continue

        # v3.38: 어말 z → 스 (devoicing; arroz 아호스)
        if c == 'z' and i + 1 == n:
            out.append(('C', 'ㅅ', 'z'))
            i += 1; continue

        # === Doubled consonants ===
        if c == nxt and c in 'bcdfgklmnprstvz':
            # rr → /h/ (Brazilian Portuguese, NIKL standard)
            if c == 'r':
                out.append(('RHO', 'ㅎ'))
                i += 2
                continue
            i += 1
            continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b'))
            i += 1; continue
        if c == 'c':
            if nxt in ('e','é','ê','i','í'):
                out.append(('C', 'ㅅ', 'c'))
            else:
                out.append(('C', 'ㅋ', 'c'))
            i += 1; continue
        if c == 'ç':
            out.append(('C', 'ㅅ', 'ç'))
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
            if nxt in ('e','é','ê','i','í'):
                out.append(('C', 'ㅈ', 'g'))
            else:
                out.append(('C', 'ㄱ', 'g'))
            i += 1; continue
        if c == 'h':
            i += 1; continue
        if c == 'j':
            out.append(('C', 'ㅈ', 'j'))
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
            out.append(('C', 'ㄴ', 'n'))
            i += 1; continue
        if c == 'p':
            out.append(('C', 'ㅍ', 'p'))
            i += 1; continue
        if c == 'r':
            out.append(('C', 'ㄹ', 'r'))
            i += 1; continue
        if c == 's':
            # 모음 사이 s → ㅈ (Brasil → 브라질)
            prev_is_v = out and out[-1][0] in ('V', 'SV', 'NV')
            if prev_is_v and nxt in VOWEL_LETTERS:
                out.append(('C', 'ㅈ', 's'))
                i += 1
                continue
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
            out.append(('C', 'ㅇ', 'w'))
            out.append(('V', 'ㅜ'))
            i += 1; continue
        if c == 'x':
            out.append(('X', None))
            i += 1; continue
        if c == 'z':
            out.append(('C', 'ㅈ', 'z'))
            i += 1; continue

        out.append(('LIT', s[i]))
        i += 1

    return out


def _intervocalic_l_post(phonemes):
    """Hangul mode: Portuguese intervocalic L (Romance)."""
    out2 = []
    for k, ph in enumerate(phonemes):
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('V', 'SV', 'NV')
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_double'))
        else:
            out2.append(ph)
    return out2


ALLOW_AS_FINAL = {'ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ'}


def _next_is_vowel(phonemes, i):
    return i+1 < len(phonemes) and phonemes[i+1][0] in ('V', 'SV', 'NV')


def _assemble(phonemes, precise):
    syllables = []
    i = 0
    n = len(phonemes)

    while i < n:
        ph = phonemes[i]
        kind = ph[0]

        if kind == 'V':
            syllables.append(_compose('ㅇ', ph[1]))
            i += 1; continue
        if kind == 'SV':
            syllables.append(_compose('ㅇ', ph[1]))
            i += 1; continue
        if kind == 'NV':
            syllables.append(_compose('ㅇ', ph[1], 'ㅇ'))
            i += 1; continue
        if kind == 'LIT':
            syllables.append(ph[1])
            i += 1; continue

        if kind == 'RR':
            _add_jong_to_last(syllables, 'ㄹ')
            if _next_is_vowel(phonemes, i):
                vph = phonemes[i+1]
                if vph[0] == 'NV':
                    syllables.append(_compose('ㄹ', vph[1], 'ㅇ'))
                else:
                    syllables.append(_compose('ㄹ', vph[1]))
                i += 2
            else:
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
            continue

        if kind == 'RHO':
            # NIKL Brazilian Portuguese: rr → /h/
            # forró 포호, arroz 아호스, churrasco 슈하스쿠
            if _next_is_vowel(phonemes, i):
                vph = phonemes[i+1]
                if vph[0] == 'NV':
                    syllables.append(_compose('ㅎ', vph[1], 'ㅇ'))
                else:
                    syllables.append(_compose('ㅎ', vph[1]))
                i += 2
            else:
                syllables.append(_compose('ㅎ', 'ㅡ'))
                i += 1
            continue

        if kind == 'X':
            if not syllables:
                if _next_is_vowel(phonemes, i):
                    syllables.append(_compose('ㅅ', phonemes[i+1][1]))
                    i += 2
                else:
                    syllables.append(_compose('ㅅ', 'ㅡ'))
                    i += 1
            else:
                _add_jong_to_last(syllables, 'ㄱ')
                if _next_is_vowel(phonemes, i):
                    syllables.append(_compose('ㅅ', phonemes[i+1][1]))
                    i += 2
                else:
                    syllables.append(_compose('ㅅ', 'ㅡ'))
                    i += 1
            continue

        if kind == 'OLD':
            old = ph[1]
            if _next_is_vowel(phonemes, i):
                vph = phonemes[i+1]
                if vph[0] == 'NV':
                    syllables.append(old)
                    syllables.append(_compose('ㅇ', vph[1], 'ㅇ'))
                else:
                    syllables.append(old)
                    syllables.append(_compose('ㅇ', vph[1]))
                i += 2
            elif (i+2 < n and phonemes[i+1][0] == 'C'
                  and phonemes[i+2][0] in ('V', 'SV', 'NV')):
                cph = phonemes[i+1]; vph = phonemes[i+2]
                if vph[0] == 'NV':
                    syllables.append(old)
                    syllables.append(_compose(cph[1], vph[1], 'ㅇ'))
                else:
                    syllables.append(old)
                    syllables.append(_compose(cph[1], vph[1]))
                i += 3
            else:
                syllables.append(old)
                syllables.append(_compose('ㅇ', 'ㅡ'))
                i += 1
            continue

        if kind == 'C':
            cho = ph[1]
            src = ph[2] if len(ph) > 2 else ''
            if _next_is_vowel(phonemes, i):
                vph = phonemes[i+1]
                if vph[0] == 'NV':
                    syllables.append(_compose(cho, vph[1], 'ㅇ'))
                else:
                    syllables.append(_compose(cho, vph[1]))
                i += 2
                continue
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
                continue
            if src in ('l', 'm', 'n', 'nh', 'lh'):
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
            if src == 'p' and cho == 'ㅍ':
                if syllables and not _has_jong(syllables[-1]):
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
        elif kind == 'RHO':
            out.append('ㅎ')
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


def transcribe_pt(text, precise=True, mode='hangul', phonetic=False):
    """pt → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-záéíóúâêôãõàèìòùçÁÉÍÓÚÂÊÔÃÕÀÈÌÒÙÇ]+$', part):
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
        if not re.match(r'^[A-Za-záéíóúâêôãõàèìòùçÁÉÍÓÚÂÊÔÃÕÀÈÌÒÙÇ]+$', part):
            out.append(part)
            continue
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


if __name__ == '__main__':
    tests = [
        ('obrigado', '오브리가도', '오브리가도'),
        ('Brasil', '브라질', '브라질'),
        ('Portugal', '포르투갈', '포르투갈'),
        ('Lisboa', '리스보아', '리스보아'),
        ('coração', '코라상', '코라상'),
        ('São', '상', '상'),
        ('Paulo', '파울로', '파울로'),
        ('Rio', '리오', '리오'),
        ('amigo', '아미고', '아미고'),
        ('mulher', '무리에르', '무리에르'),  # lh palatal
        ('senhor', '세뇨르', '세뇨르'),  # nh palatal
        ('chave', '샤ㅸ에', '샤베'),
        ('caçar', '카사르', '카사르'),
        ('queijo', '케이조', '케이조'),
        ('família', 'ㆄ아밀리아', '파밀리아'),
        ('nação', '나상', '나상'),
        ('bom', '봉', '봉'),
        ('sim', '싱', '싱'),
        ('um', '웅', '웅'),
        ('Madeira', '마데이라', '마데이라'),
    ]
    print("=== PORTUGUESE PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_pt(inp, True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")
    print("\n=== PORTUGUESE BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_pt(inp, False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
