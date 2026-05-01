"""Hunmin Precise — French (fr) letter-by-letter → Hangul.

전략: IPA 없음. spelling 기반 룰. 프랑스어는 phonetic 70-80% (silent letters, 비음화).

주요 규칙:
  비음화 (V + n/m + 자음/어말):
    an/am, en/em → ㅏㅇ (앙)
    in/im, ain/aim, ein → ㅐㅇ (앵)
    on/om → ㅗㅇ (옹)
    un/um → ㅓㅇ (엉) — 외래어 표기법 convention

  모음 디그래프:
    ai/aî/ei/eî → ㅔ
    au/eau → ㅗ
    eu/œu → ㅚ
    oi/oî → ㅘ (/wa/)
    ou/oû → ㅜ
    ui → ㅟ

  자음:
    c + e/i/y → ㅅ (cinéma → 시네마)
    c + a/o/u → ㅋ
    ç → ㅅ (garçon → 가르송)
    g + e/i/y → ㅈ
    g + a/o/u → ㄱ
    h → silent
    j → ㅈ
    qu → ㅋ (silent u)
    ch → ㅅ + palatal vowel (chat → 샤, Champs → 샹)
    gn → 냐/뇨 (palatal n)
    ph → ㆄ/ㅍ
    th → ㅌ
    ill (after vowel) → palatal y (Camille → 카미유, but 어려움)

  v → ㅸ/ㅂ
  f → ㆄ/ㅍ

  묵음:
    어말 e (mute) → silent
    어말 자음 s, t, d, x, z, p → silent
    어말 자음 c, f, l, r → 보통 발음
    h → 항상 silent
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
    return False


def _has_jong(syllable):
    if len(syllable) != 1: return True
    c = ord(syllable)
    if not (0xAC00 <= c <= 0xD7A3): return False
    return (c - HANGUL_BASE) % 28 != 0


VOWEL_LETTERS = set('aeiouyàâäéèêëîïôöùûüÿœæ')


def _phonemize(word, precise):
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    s = word.lower()
    # 어말 묵음 자음 cluster 전처리: 어말 ptdsxzg... 등 strip (단, 비음 m/n은 유지)
    SILENT_FINAL = set('ptdsxzg')
    while len(s) > 1 and s[-1] in SILENT_FINAL:
        s = s[:-1]
    n = len(s)
    out = []
    i = 0

    def is_vowel(ch):
        return ch in VOWEL_LETTERS

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''
        nxt2 = s[i+2] if i+2 < n else ''
        nxt3 = s[i+3] if i+3 < n else ''

        # === 어말 mute e (마지막 글자가 e면 drop) ===
        if c == 'e' and i == n-1 and i > 0 and s[i-1] not in VOWEL_LETTERS:
            # 단, 단음절 (le, je 등)은 drop 안 함
            if i > 0:  # word 길이 > 1
                # 어말 e silence (e.g., belle → 벨, France → 프랑스)
                # 단, 어말 -ie, -ue 등은 다른 처리 (이미 위 디지그래프에서)
                i += 1
                continue

        # === Trigraphs / vowel patterns first ===

        # eau → ㅗ
        if c == 'e' and nxt == 'a' and nxt2 == 'u':
            out.append(('V', 'ㅗ'))
            i += 3
            continue
        # ain/aim, ein/eim → 앵 (ㅐㅇ)
        if c in ('a', 'e') and nxt == 'i' and nxt2 in ('n', 'm') and (i+3 >= n or s[i+3] not in VOWEL_LETTERS or s[i+3] in ('n','m')):
            out.append(('NV', 'ㅐ'))
            i += 3
            continue
        # ien (i + en) → 이앙 (이 + ㅏㅇ): bien → 비앙
        if c == 'i' and nxt == 'e' and nxt2 == 'n' and (i+3 >= n or s[i+3] not in VOWEL_LETTERS):
            out.append(('V', 'ㅣ'))
            out.append(('NV', 'ㅐ'))
            i += 3
            continue
        # œu → ㅚ
        if c == 'œ' and nxt == 'u':
            out.append(('V', 'ㅚ'))
            i += 2
            continue

        # === 모음 디그래프 ===
        di = c + nxt
        # ai/aî/ay → ㅔ
        if di in ('ai', 'aî', 'aï', 'ay'):
            out.append(('V', 'ㅔ'))
            i += 2
            continue
        # ei/eî → ㅔ
        if di in ('ei', 'eî'):
            out.append(('V', 'ㅔ'))
            i += 2
            continue
        # au → ㅗ
        if di == 'au':
            out.append(('V', 'ㅗ'))
            i += 2
            continue
        # eu → ㅚ
        if di in ('eu', 'eû'):
            out.append(('V', 'ㅚ'))
            i += 2
            continue
        # oi/oî → ㅜ + ㅏ (separate, Korean convention: Renoir → 르누아르)
        if di in ('oi', 'oî', 'oï'):
            out.append(('V', 'ㅜ'))
            out.append(('V', 'ㅏ'))
            i += 2
            continue
        # ou/oû → ㅜ
        if di in ('ou', 'oû'):
            out.append(('V', 'ㅜ'))
            i += 2
            continue
        # ui → ㅟ
        if di == 'ui':
            out.append(('V', 'ㅟ'))
            i += 2
            continue

        # === 비음화 ===
        # 비음화 트리거: V + n/m + (자음/어말). 단, doubled n/m + 모음 → 비음화 안 함.
        def _nasalizes(after_pos):
            after = s[after_pos] if after_pos < n else ''
            if not after:
                return True
            if after in VOWEL_LETTERS:
                return False
            if after in ('n', 'm'):
                # doubled n/m: peek further. If 다음이 모음 → 비음화 안 함.
                after2 = s[after_pos+1] if after_pos+1 < n else ''
                if after2 and after2 in VOWEL_LETTERS:
                    return False
                return True
            return True

        if c in ('a', 'à', 'â', 'è', 'ê') and nxt in ('n', 'm') and _nasalizes(i+2):
            out.append(('NV', 'ㅏ'))
            i += 2
            continue
        if c == 'e' and nxt in ('n', 'm') and _nasalizes(i+2):
            out.append(('NV', 'ㅏ'))
            i += 2
            continue
        if c in ('i', 'î', 'y') and nxt in ('n', 'm') and _nasalizes(i+2):
            out.append(('NV', 'ㅐ'))
            i += 2
            continue
        if c in ('o', 'ô') and nxt in ('n', 'm') and _nasalizes(i+2):
            out.append(('NV', 'ㅗ'))
            i += 2
            continue
        if c in ('u', 'û') and nxt in ('n', 'm') and _nasalizes(i+2):
            out.append(('NV', 'ㅓ'))
            i += 2
            continue

        # === 'e' (regular) — context-dependent ===
        # e + (자음 + 모음) → 으 (schwa, open syllable: Renoir → 르)
        # e + (자음 + 자음) or e + (어말) → ㅔ (closed syllable: merci → 메, mer → 메르)
        if c == 'e':
            after1 = s[i+1] if i+1 < n else ''
            after2 = s[i+2] if i+2 < n else ''
            if not after1:
                # 어말 e — 위에서 mute drop 처리됐을 텐데, 통과 시 으
                out.append(('V', 'ㅡ'))
                i += 1
                continue
            if after1 in VOWEL_LETTERS:
                # 모음 디그래프는 위에서 처리됨 → 도달하면 'e'+모음 fallback (드뭄): ㅔ
                out.append(('V', 'ㅔ'))
                i += 1
                continue
            # after1은 자음
            if not after2 or after2 not in VOWEL_LETTERS:
                # 자음 + 자음/어말 → 닫힌 음절 → ㅔ
                out.append(('V', 'ㅔ'))
            else:
                # 자음 + 모음 → 열린 음절 → 으 (schwa)
                out.append(('V', 'ㅡ'))
            i += 1
            continue

        # === 단일 모음 ===
        single_v = {
            'a':'ㅏ', 'à':'ㅏ', 'â':'ㅏ', 'ä':'ㅏ',
            'é':'ㅔ', 'è':'ㅔ', 'ê':'ㅔ', 'ë':'ㅔ',
            'i':'ㅣ', 'î':'ㅣ', 'ï':'ㅣ',
            'o':'ㅗ', 'ô':'ㅗ', 'ö':'ㅗ',
            'u':'ㅟ', 'ù':'ㅟ', 'û':'ㅟ', 'ü':'ㅟ',
            'y':'ㅣ', 'ÿ':'ㅣ',
            'œ':'ㅚ', 'æ':'ㅔ',
        }
        if c in single_v:
            out.append(('V', single_v[c]))
            i += 1
            continue

        # === Digraphs (consonant) ===
        # ch + V → 샤/셰/시/쇼/슈. ch + V + n/m + 자음/end → 비음화 (Champs → 샹)
        if c == 'c' and nxt == 'h':
            sh_map = {'a':'ㅑ','e':'ㅖ','é':'ㅖ','è':'ㅖ','ê':'ㅖ',
                      'i':'ㅣ','î':'ㅣ','o':'ㅛ','ô':'ㅛ','u':'ㅠ','y':'ㅣ'}
            sh_nasal_map = {'a':'ㅑ','e':'ㅑ','i':'ㅒ','o':'ㅛ','u':'ㅠ'}
            if nxt2 in sh_map:
                # 비음화 체크: nxt2 + 'n/m' + (자음/end)
                v3 = s[i+3] if i+3 < n else ''
                v4 = s[i+4] if i+4 < n else ''
                if v3 in ('n','m') and (not v4 or v4 not in VOWEL_LETTERS):
                    out.append(('C', 'ㅅ', 'sh'))
                    out.append(('NV', sh_nasal_map.get(nxt2, sh_map[nxt2])))
                    i += 4
                    continue
                out.append(('C', 'ㅅ', 'sh'))
                out.append(('SV', sh_map[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㅅ', 'sh'))
            i += 2
            continue
        # gn + V → 냐/녜/...
        if c == 'g' and nxt == 'n':
            ymap = {'a':'ㅑ','e':'ㅖ','é':'ㅖ','i':'ㅣ','o':'ㅛ','u':'ㅠ'}
            if nxt2 in ymap:
                out.append(('C', 'ㄴ', 'gn'))
                out.append(('SV', ymap[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㄴ', 'gn'))
            out.append(('V', 'ㅣ'))
            i += 2
            continue
        # ph → ㆄ/ㅍ
        if c == 'p' and nxt == 'h':
            if precise:
                out.append(('OLD', 'ㆄ'))
            else:
                out.append(('C', 'ㅍ', 'ph'))
            i += 2
            continue
        # th → ㅌ
        if c == 't' and nxt == 'h':
            out.append(('C', 'ㅌ', 't'))
            i += 2
            continue
        # qu + V → ㅋ + V (silent u)
        if c == 'q' and nxt == 'u':
            if nxt2 in single_v:
                out.append(('C', 'ㅋ', 'q'))
                out.append(('V', single_v[nxt2]))
                i += 3
                continue
            out.append(('C', 'ㅋ', 'q'))
            i += 2
            continue
        # ille (after consonant) → 이으 / palatal y
        if c == 'i' and nxt == 'l' and nxt2 == 'l':
            # ille → 이으 (Camille → 카미유): treat as semi-vowel
            # Simple: ille + (e mute) → V ㅣ + V ㅠ (이유). 하지만 단순화: V ㅠ
            after = s[i+3] if i+3 < n else ''
            if after == 'e' and (i+4 >= n or s[i+4] not in VOWEL_LETTERS):
                # ille at end (or before consonant) → 이유 (V ㅣ + SV ㅠ) → simplified 유
                # Actually 표준: 카미유 → ka-mi-yu where 'mille' → 미유 = 미+유 (ㅁㅣ + ㅇㅠ)
                # So 'ill' → ㅣ + ㅠ syllables
                out.append(('V', 'ㅣ'))
                out.append(('V', 'ㅠ'))
                i += 4  # consume 'ille'
                continue
            # ill alone (rare) → ㅣ + ㅠ
            out.append(('V', 'ㅣ'))
            out.append(('SV', 'ㅠ'))
            i += 3
            continue

        # === Doubled consonants ===
        # 보통 단순화 (drop). 단, 어말 + l/r/n/m 의 받침 처리 별도.
        if c == nxt and c in 'bcdfgklmnpqrstvz':
            i += 1
            continue

        # === SINGLE CONSONANTS ===
        if c == 'b':
            out.append(('C', 'ㅂ', 'b'))
            i += 1; continue
        if c == 'c':
            if nxt in ('e', 'é', 'è', 'ê', 'i', 'î', 'y'):
                out.append(('C', 'ㅅ', 'c'))
            else:
                out.append(('C', 'ㅋ', 'c'))
            i += 1; continue
        if c == 'ç':
            out.append(('C', 'ㅅ', 'ç'))
            i += 1; continue
        if c == 'd':
            # 어말 d → silent
            if i+1 >= n:
                i += 1
                continue
            out.append(('C', 'ㄷ', 'd'))
            i += 1; continue
        if c == 'f':
            if precise:
                out.append(('OLD', F))
            else:
                out.append(('C', F, 'f'))
            i += 1; continue
        if c == 'g':
            # 어말 -ge (e mute) → -주 (g + ㅜ)
            if nxt == 'e' and i+2 >= n:
                out.append(('C', 'ㅈ', 'g'))
                out.append(('V', 'ㅜ'))
                i += 2
                continue
            if nxt in ('e', 'é', 'è', 'ê', 'i', 'î', 'y'):
                out.append(('C', 'ㅈ', 'g'))
            else:
                out.append(('C', 'ㄱ', 'g'))
            i += 1; continue
        if c == 'h':
            i += 1; continue  # silent
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
            # 어말 p → silent (보통)
            if i+1 >= n:
                i += 1
                continue
            out.append(('C', 'ㅍ', 'p'))
            i += 1; continue
        if c == 'q':
            out.append(('C', 'ㅋ', 'q'))
            i += 1; continue
        if c == 'r':
            out.append(('C', 'ㄹ', 'r'))
            i += 1; continue
        if c == 's':
            # 어말 s → silent
            if i+1 >= n:
                i += 1
                continue
            # 모음 사이 s → ㅈ (maison → 메종)
            prev_is_v = out and out[-1][0] in ('V', 'SV', 'NV')
            if prev_is_v and nxt in VOWEL_LETTERS:
                out.append(('C', 'ㅈ', 's'))
                i += 1
                continue
            out.append(('C', 'ㅅ', 's'))
            i += 1; continue
        if c == 't':
            # 어말 t → silent (보통)
            if i+1 >= n:
                i += 1
                continue
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
            # 어말 x → silent
            if i+1 >= n:
                i += 1
                continue
            out.append(('X', None))
            i += 1; continue
        if c == 'z':
            # 어말 z → silent
            if i+1 >= n:
                i += 1
                continue
            out.append(('C', 'ㅈ', 'z'))
            i += 1; continue

        out.append(('LIT', s[i]))
        i += 1

    return out


def _intervocalic_l_post(phonemes):
    """Hangul mode only: intervocalic L doubling + Cl cluster.

    NIKL French: Cl 클러스터 → 받침-ㄹ + ㄹV (glace 글라스, plage 플라주, fleur 플뢰르, plaisir 플레지르)
    """
    CLUSTER_C = {'ㅂ', 'ㅍ', 'ㄱ', 'ㅋ', 'ㄷ', 'ㅌ', 'ㆄ'}
    out2 = []
    for k, ph in enumerate(phonemes):
        # Existing intervocalic L
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('V', 'SV')
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_double'))
            continue
        # Cl cluster (consonant + 'l' + V) → 받침-ㄹ + ㄹV
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('C', 'OLD')
                and len(phonemes[k-1]) >= 2 and phonemes[k-1][1] in CLUSTER_C
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_cluster'))
            continue
        out2.append(ph)
    return out2


# === 음소 → 한글 ===
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
            i += 1
            continue

        if kind == 'SV':
            syllables.append(_compose('ㅇ', ph[1]))
            i += 1
            continue

        if kind == 'NV':
            # nasal vowel: V + ㅇ받침
            syllables.append(_compose('ㅇ', ph[1], 'ㅇ'))
            i += 1
            continue

        if kind == 'LIT':
            syllables.append(ph[1])
            i += 1
            continue

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
                vph = phonemes[i+1]
                v = vph[1]
                if vph[0] == 'NV':
                    syllables.append(old)
                    syllables.append(_compose('ㅇ', v, 'ㅇ'))
                else:
                    syllables.append(old)
                    syllables.append(_compose('ㅇ', v))
                i += 2
            elif (i+2 < n and phonemes[i+1][0] == 'C'
                  and phonemes[i+2][0] in ('V', 'SV', 'NV')):
                next_c = phonemes[i+1]
                next_v = phonemes[i+2]
                cho = next_c[1]
                if next_v[0] == 'NV':
                    syllables.append(old)
                    syllables.append(_compose(cho, next_v[1], 'ㅇ'))
                else:
                    syllables.append(old)
                    syllables.append(_compose(cho, next_v[1]))
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
            # 어말/자음 앞
            if src == 'r':
                syllables.append(_compose('ㄹ', 'ㅡ'))
                i += 1
                continue
            if src in ('l', 'm', 'n', 'gn'):
                if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                    if _add_jong_to_last(syllables, cho):
                        i += 1
                        continue
                syllables.append(_compose(cho, 'ㅡ'))
                i += 1
                continue
            # French: 자음 자음 앞 → 으-syllable (보통)
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


def transcribe_fr(text, precise=True, mode='hangul', phonetic=False):
    """fr → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r'^[A-Za-zàâäéèêëîïôöùûüÿœæç]+$', part):
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
        if not re.match(r'^[A-Za-zàâäéèêëîïôöùûüÿœæç]+$', part):
            out.append(part)
            continue
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


# === Test ===
if __name__ == '__main__':
    tests = [
        # (input, expected_precise, expected_basic)
        ('bonjour', '봉주르', '봉주르'),
        ('merci', '메르시', '메르시'),
        ('Paris', '파리', '파리'),
        ('France', 'ㆄ랑스', '프랑스'),
        ('chocolat', '쇼콜라', '쇼콜라'),
        ('amour', '아무르', '아무르'),
        ('enfant', '앙ㆄ앙', '앙팡'),
        ('maison', '메종', '메종'),
        ('belle', '벨', '벨'),
        ('Voltaire', 'ㅸ올테르', '볼테르'),
        ('Macron', '마크롱', '마크롱'),
        ('Cézanne', '세잔', '세잔'),
        ('Renoir', '르누아르', '르누아르'),
        ('garçon', '가르송', '가르송'),
        ('vin', 'ㅸ앵', '뱅'),
        ('pain', '팽', '팽'),
        ('un', '엉', '엉'),
        ('eau', '오', '오'),
        ('beau', '보', '보'),
        ('Champs', '샹', '샹'),
        ('rouge', '루주', '루주'),
        ('chat', '샤', '샤'),
    ]

    print("=== FRENCH PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_fr(inp, precise=True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")

    print("\n=== FRENCH BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_fr(inp, precise=False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
