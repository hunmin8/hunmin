"""Hunmin Precise — Polish (pl) letter-by-letter → Hangul.

전략: 폴란드어는 디그래프가 많지만 phonetic. Slavic 언어.

주요 규칙:
  cz → ㅊ
  sz → ㅅ + palatal vowel (Warsaw → 바르샤바)
  rz → ㅈ
  dz → ㅈ
  dż → ㅈ (drze → 제 etc)
  szcz → 슈치
  ch → ㅎ
  ch alone → 흐
  ł → ㅇ + W-vowel (이전엔 ㄹ; 현대 발음 /w/)
  ą → 옹 (nasal o)
  ę → 엥 (nasal e)
  ć → 치
  ś → 시
  ź → 지
  ń → 니
  c → ㅊ (always /ts/)
  j → 야/예/이/요/유 (semi-vowel)
  w → ㅸ/ㅂ
  y → ㅡ (or ㅣ)
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
    """syllable의 중성이 ㅡ (으)인지."""
    if len(syllable) != 1: return False
    c = ord(syllable)
    if not (0xAC00 <= c <= 0xD7A3): return False
    base = c - HANGUL_BASE
    jung = (base % 588) // 28
    return jung == VOWELS_J.index('ㅡ')


VOWEL_LETTERS = set('aeiouyąęóAEIOUYĄĘÓ')


def _phonemize(word, precise):
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    s = word.lower()
    n = len(s)
    out = []
    i = 0

    sh_map = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ','y':'ㅣ','ó':'ㅛ','ą':'ㅛ','ę':'ㅖ'}

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''
        nxt2 = s[i+2] if i+2 < n else ''
        nxt3 = s[i+3] if i+3 < n else ''

        # === 4-letter ===
        if c == 's' and nxt == 'z' and nxt2 == 'c' and nxt3 == 'z':
            # szcz → 슈+치 (러시아의 щ과 비슷)
            out.append(('C', 'ㅅ', 'sh'))
            out.append(('SV', 'ㅠ'))
            out.append(('C', 'ㅊ', 'cz'))
            i += 4
            continue

        # === 3-letter (less common) ===
        # dzi/dzia... → palatal /dʑ/ → 지/자/etc.

        # === 2-letter digraphs ===
        if c == 'c' and nxt == 'h':
            # ch → ㅎ
            if nxt2 in VOWEL_LETTERS:
                out.append(('C', 'ㅎ', 'ch'))
                continue_skip = False
                # fall through to single vowel processing of nxt2
            else:
                out.append(('C', 'ㅎ', 'ch'))
            i += 2
            continue
        if c == 'c' and nxt == 'z':
            # cz → ㅊ
            out.append(('C', 'ㅊ', 'cz'))
            i += 2
            continue
        if c == 's' and nxt == 'z':
            # sz + V → palatal Korean
            if nxt2 in sh_map:
                out.append(('C', 'ㅅ', 'sh'))
                out.append(('SV', sh_map[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㅅ', 'sh'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue
        if c == 'r' and nxt == 'z':
            # rz → ㅈ
            out.append(('C', 'ㅈ', 'rz'))
            i += 2
            continue
        if c == 'd' and nxt == 'z':
            # dz → ㅈ
            out.append(('C', 'ㅈ', 'dz'))
            i += 2
            continue
        if c == 'd' and nxt == 'ż':
            # dż → ㅈ
            out.append(('C', 'ㅈ', 'dż'))
            i += 2
            continue
        if c == 'd' and nxt == 'ź':
            # dź → ㅈ. 모음 앞 → 자/제/지/조/주. 어말 → 지 (palatal).
            if nxt2 in single_v:
                pmap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ','y':'ㅣ'}
                out.append(('C', 'ㅈ', 'dź'))
                out.append(('SV', pmap.get(nxt2, single_v[nxt2])))
                i += 3
                continue
            # 어말 또는 자음 앞: 지
            out.append(('C', 'ㅈ', 'dź'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue

        # === 단일 모음 ===
        single_v = {
            'a':'ㅏ','á':'ㅏ',
            'e':'ㅔ','é':'ㅔ',
            'i':'ㅣ','í':'ㅣ',
            'o':'ㅗ','ó':'ㅜ',  # ó = /u/ in Polish
            'u':'ㅜ',
            'y':'ㅣ',  # /ɨ/ → 이
        }
        if c in single_v:
            out.append(('V', single_v[c]))
            i += 1
            continue
        # ą → 옹 (nasal o, /ɔ̃/)
        if c == 'ą':
            out.append(('NV', 'ㅗ'))
            i += 1
            continue
        # ę → 엥 (nasal e, /ɛ̃/)
        if c == 'ę':
            out.append(('NV', 'ㅔ'))
            i += 1
            continue

        # === SINGLE CONSONANTS / palatal ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b')); i += 1; continue
        if c == 'c':
            out.append(('C', 'ㅊ', 'c')); i += 1; continue
        if c == 'ć':
            # palatal /tɕ/ → 치 (with following palatal vowel if any)
            if nxt in single_v:
                out.append(('C', 'ㅊ', 'ć'))
                # palatal: 'ć + i' → 치, 'ć + a' → 차 etc.
                pmap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ','ó':'ㅛ','y':'ㅣ'}
                out.append(('SV', pmap.get(nxt, single_v[nxt])))
                i += 2
                continue
            out.append(('C', 'ㅊ', 'ć'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 'd':
            out.append(('C', 'ㄷ', 'd')); i += 1; continue
        if c == 'f':
            if precise: out.append(('OLD', F))
            else: out.append(('C', F, 'f'))
            i += 1; continue
        if c == 'g':
            out.append(('C', 'ㄱ', 'g')); i += 1; continue
        if c == 'h':
            out.append(('C', 'ㅎ', 'h')); i += 1; continue
        if c == 'j':
            ymap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ','ó':'ㅛ','ą':'ㅛ','ę':'ㅖ'}
            if nxt in ymap:
                out.append(('C', 'ㅇ', 'j'))
                out.append(('SV', ymap[nxt]))
                i += 2
                continue
            out.append(('C', 'ㅇ', 'j'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 'k':
            out.append(('C', 'ㅋ', 'k')); i += 1; continue
        if c == 'l':
            out.append(('C', 'ㄹ', 'l')); i += 1; continue
        if c == 'ł':
            # ł = /w/ → ㅇ + W-vowel
            wmap = {'a':'ㅘ','e':'ㅞ','i':'ㅟ','o':'ㅝ','u':'ㅜ','ó':'ㅜ','y':'ㅟ'}  # ły → 위 NIKL
            wnasal = {'ą':'ㅝ','ę':'ㅞ'}
            if nxt in wmap:
                out.append(('C', 'ㅇ', 'ł'))
                out.append(('SV', wmap[nxt]))
                i += 2
                continue
            if nxt in wnasal:
                out.append(('C', 'ㅇ', 'ł'))
                out.append(('NV', wnasal[nxt]))
                i += 2
                continue
            # ł alone → 우 syllable
            out.append(('C', 'ㅇ', 'ł'))
            out.append(('V', 'ㅜ'))
            i += 1; continue
        if c == 'm':
            out.append(('C', 'ㅁ', 'm')); i += 1; continue
        if c == 'n':
            out.append(('C', 'ㄴ', 'n')); i += 1; continue
        if c == 'ń':
            # palatal n → 니 + palatal vowel (모음 앞)
            # 자음 앞 또는 어말 → ㄴ받침
            if nxt in single_v:
                pmap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ','y':'ㅣ'}
                out.append(('C', 'ㄴ', 'ń'))
                out.append(('SV', pmap.get(nxt, single_v[nxt])))
                i += 2
                continue
            # 자음 앞/어말 → C ㄴ n (소문자 'n' src로 → 받침 처리)
            out.append(('C', 'ㄴ', 'n'))
            i += 1; continue
        if c == 'p':
            out.append(('C', 'ㅍ', 'p')); i += 1; continue
        if c == 'q':
            out.append(('C', 'ㅋ', 'q')); i += 1; continue
        if c == 'r':
            out.append(('C', 'ㄹ', 'r')); i += 1; continue
        if c == 's':
            out.append(('C', 'ㅅ', 's')); i += 1; continue
        if c == 'ś':
            # palatal s → 시 + palatal vowel
            if nxt in single_v:
                pmap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ','y':'ㅣ'}
                out.append(('C', 'ㅅ', 'ś'))
                out.append(('SV', pmap.get(nxt, single_v[nxt])))
                i += 2
                continue
            out.append(('C', 'ㅅ', 'ś'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 't':
            out.append(('C', 'ㅌ', 't')); i += 1; continue
        if c == 'v':
            if precise: out.append(('OLD', V_OLD))
            else: out.append(('C', V_OLD, 'v'))
            i += 1; continue
        if c == 'w':
            # Polish w = /v/ → ㅸ/ㅂ
            if precise: out.append(('OLD', 'ㅸ'))
            else: out.append(('C', 'ㅂ', 'w'))
            i += 1; continue
        if c == 'x':
            out.append(('X', None)); i += 1; continue
        if c == 'z':
            out.append(('C', 'ㅈ', 'z')); i += 1; continue
        if c == 'ż':
            out.append(('C', 'ㅈ', 'ż')); i += 1; continue
        if c == 'ź':
            # palatal z → 지
            if nxt in single_v:
                pmap = {'a':'ㅑ','e':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ','y':'ㅣ'}
                out.append(('C', 'ㅈ', 'ź'))
                out.append(('SV', pmap.get(nxt, single_v[nxt])))
                i += 2
                continue
            out.append(('C', 'ㅈ', 'ź'))
            out.append(('V', 'ㅣ'))
            i += 1; continue

        out.append(('LIT', s[i])); i += 1

    return out


ALLOW_AS_FINAL = {'ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ'}


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
        if kind == 'NV':
            syllables.append(_compose('ㅇ', ph[1], 'ㅇ')); i += 1; continue
        if kind == 'LIT':
            syllables.append(ph[1]); i += 1; continue
        # v3.38: RR handler (intervocalic L doubling + Cl cluster)
        if kind == 'RR':
            _add_jong_to_last(syllables, 'ㄹ')
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                if phonemes[i+1][0] == 'NV':
                    syllables.append(_compose('ㄹ', v, 'ㅇ'))
                else:
                    syllables.append(_compose('ㄹ', v))
                i += 2
            else:
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
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
                vph = phonemes[i+1]
                if vph[0] == 'NV':
                    syllables.append(old); syllables.append(_compose('ㅇ', vph[1], 'ㅇ'))
                else:
                    syllables.append(old); syllables.append(_compose('ㅇ', vph[1]))
                i += 2
            elif (i+2 < n and phonemes[i+1][0] == 'C' and phonemes[i+2][0] in ('V','SV','NV')):
                cph = phonemes[i+1]; vph = phonemes[i+2]
                if vph[0] == 'NV':
                    syllables.append(old); syllables.append(_compose(cph[1], vph[1], 'ㅇ'))
                else:
                    syllables.append(old); syllables.append(_compose(cph[1], vph[1]))
                i += 3
            elif i+1 >= n:
                # 어말 OLD: 으-syllable 안 붙임 (ㅸ만)
                syllables.append(old)
                i += 1
            else:
                syllables.append(old); syllables.append(_compose('ㅇ', 'ㅡ')); i += 1
            continue
        if kind == 'C':
            cho = ph[1]; src = ph[2] if len(ph) > 2 else ''
            if _next_is_vowel(phonemes, i):
                vph = phonemes[i+1]
                if vph[0] == 'NV':
                    syllables.append(_compose(cho, vph[1], 'ㅇ'))
                else:
                    syllables.append(_compose(cho, vph[1]))
                i += 2
                continue
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ')); i += 1; continue
            if src in ('l','m','n','ń'):
                if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                    if _add_jong_to_last(syllables, cho):
                        i += 1; continue
                syllables.append(_compose(cho, 'ㅡ')); i += 1; continue
            if src in ('c','k','q') and cho == 'ㅋ':
                # v3.38: 어말 k → 크 separate (NIKL Polish: rynek 리네크, park 파르크, żurek 주레크)
                if i+1 >= n:
                    syllables.append(_compose('ㅋ', 'ㅡ')); i += 1; continue
                # 으-syllable에 받침 추가 안 함 (스+크 패턴 보존)
                if syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㄱ'):
                        i += 1; continue
                syllables.append(_compose('ㅋ', 'ㅡ')); i += 1; continue
            if src == 'p' and cho == 'ㅍ':
                if syllables and not _has_jong(syllables[-1]) and not _is_eu_syll(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㅂ'):
                        i += 1; continue
                syllables.append(_compose('ㅍ', 'ㅡ')); i += 1; continue
            # v3.38: 어말 devoicing — b/w → 프 (chleb 흘레프, Kraków 크라쿠프, Wrocław 브로츠와프)
            if i+1 >= n:
                if src == 'b' and cho == 'ㅂ':
                    syllables.append(_compose('ㅍ', 'ㅡ')); i += 1; continue
                if src == 'w' and cho == 'ㅂ':
                    syllables.append(_compose('ㅍ', 'ㅡ')); i += 1; continue
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



def _intervocalic_l_post(phonemes):
    """Polish: intervocalic L doubling + Cl cluster (NIKL convention).

    ulica 우리차 → 울리차 (intervocalic l → 받침-ㄹ + ㄹV)
    chleb 흐레브 → 흘레프 (Cl cluster, 흘+레)
    """
    # v3.38: 'ㅁ' added (mleko 므레코→믈레코)
    CLUSTER_C = {'ㅂ', 'ㅍ', 'ㄱ', 'ㅋ', 'ㄷ', 'ㅌ', 'ㅎ', 'ㆄ', 'ㅁ'}
    out2 = []
    for k, ph in enumerate(phonemes):
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('V', 'SV')
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_double'))
            continue
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('C', 'OLD')
                and len(phonemes[k-1]) >= 2 and phonemes[k-1][1] in CLUSTER_C
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_cluster'))
            continue
        out2.append(ph)
    return out2

def transcribe_pl(text, precise=True, mode='hangul', phonetic=False):
    """pl → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+$', part):
            out.append(part); continue
        phs_raw = _phonemize(part, precise)
        if mode == 'hangul':
            # v3.38: Enable Cl-cluster + intervocalic l post-pass (was dead code)
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
        if not re.match(r'^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+$', part):
            out.append(part); continue
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


if __name__ == '__main__':
    tests = [
        ('Warszawa', 'ㅸ아르샤ㅸ아', '바르샤바'),
        ('Kraków', '크라쿠ㅸ', '크라쿠브'),  # ó = u, w final = ㅸ/ㅂ
        ('Polska', '폴스카', '폴스카'),
        ('Wisła', 'ㅸ이스와', '비스와'),  # ł = /w/
        ('Łódź', '우지', '우지'),
        ('Gdańsk', '그단스크', '그단스크'),
        ('Poznań', '포즈난', '포즈난'),
        ('Wrocław', 'ㅸ로츠와ㅸ', '브로츠와브'),
        ('Częstochowa', '쳉스토호ㅸ아', '쳉스토호바'),
        ('pierogi', '피에로기', '피에로기'),
        ('dziękuję', '지엥쿠예', '지엥쿠예'),
        ('Lech', '레흐', '레흐'),
        ('Wałęsa', 'ㅸ아웽사', '바웽사'),
    ]
    print("=== POLISH PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_pl(inp, True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")
    print("\n=== POLISH BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_pl(inp, False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
