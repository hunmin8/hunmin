"""Hunmin Precise — Russian (ru) Cyrillic → Hangul.

전략: IPA 없음. 키릴 문자 → 한글 1-to-1 매핑.
키릴은 phonetic 알파벳이라 letter rule만으로 거의 완벽.

주요 규칙:
  а→ㅏ, э→ㅔ, и→ㅣ, о→ㅗ, у→ㅜ, ы→ㅣ
  е → 어두/모음 뒤 ㅖ, 자음 뒤 ㅔ
  ё → ㅛ
  я → ㅑ (항상)
  ю → ㅠ (항상)
  б→ㅂ, в→ㅸ/ㅂ, г→ㄱ, д→ㄷ, ж→ㅈ, з→ㅈ
  к→ㅋ, л→ㄹ, м→ㅁ, н→ㄴ, п→ㅍ, р→ㄹ, с→ㅅ, т→ㅌ
  ф→ㆄ/ㅍ, х→ㅎ, ц→ㅊ, ч→ㅊ, ш→ㅅ, щ→ㅅ
  й → 어말/자음 앞 ㅣ, 모음 앞 semi-vowel
  ь, ъ → silent
  intervocalic l → V받침 + ㄹV (Кремль → 크렘린)
  doubled consonants → drop (Russian doesn't gemiate)
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


# 모음 매핑
VOWEL_J = {
    'а':'ㅏ', 'э':'ㅔ', 'и':'ㅣ', 'о':'ㅗ', 'у':'ㅜ', 'ы':'ㅣ',
}
PALATAL_VOWEL_J = {
    'я':'ㅑ', 'ё':'ㅛ', 'ю':'ㅠ',
}
# е는 위치 의존: 자음 뒤 ㅔ, 어두/모음 뒤 ㅖ. 별도 처리.

CYRILLIC_VOWELS = set('аэиоуыеёюяАЭИОУЫЕЁЮЯ')


def _phonemize(word, precise):
    F = 'ㆄ' if precise else 'ㅍ'
    V_OLD = 'ㅸ' if precise else 'ㅂ'

    s = word.lower()
    n = len(s)
    out = []
    i = 0

    def prev_is_vowel():
        # 직전 phoneme이 V/SV인가
        return out and out[-1][0] in ('V', 'SV')

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # === 단순 모음 ===
        if c in VOWEL_J:
            out.append(('V', VOWEL_J[c]))
            i += 1
            continue

        if c in PALATAL_VOWEL_J:
            # 항상 palatal (ㅑㅛㅠ)
            # 자음 뒤면 SV, 어두/모음 뒤면 SV (ㅇ+palatal로 처리)
            out.append(('SV', PALATAL_VOWEL_J[c]))
            i += 1
            continue

        if c == 'е':
            # 어두/모음 뒤 → ㅖ (palatal)
            # 자음 뒤 → ㅔ
            if not out or prev_is_vowel():
                out.append(('SV', 'ㅖ'))
            else:
                out.append(('V', 'ㅔ'))
            i += 1
            continue

        # === й (semi-vowel/glide) ===
        if c == 'й':
            # 어말/자음 앞 → ㅣ (glide closing). 단, 직전이 ㅣ면 drop (이미 closing).
            if i+1 >= n or s[i+1] not in CYRILLIC_VOWELS:
                # 직전 phoneme이 V ㅣ 또는 SV ㅣ면 drop
                if out and out[-1][0] in ('V', 'SV') and out[-1][1] == 'ㅣ':
                    i += 1
                    continue
                out.append(('V', 'ㅣ'))
                i += 1
                continue
            else:
                # 모음 앞: ㅇ + V
                # nxt가 'а' → 야, 'е' → 예, 'о' → 요...
                ymap = {'а':'ㅑ','э':'ㅖ','и':'ㅣ','о':'ㅛ','у':'ㅠ',
                        'е':'ㅖ','ё':'ㅛ','ю':'ㅠ','я':'ㅑ','ы':'ㅣ'}
                # 다음 모음을 palatal로 합치고 й 소비
                yj = ymap.get(s[i+1], 'ㅣ')
                out.append(('C', 'ㅇ', 'й'))
                out.append(('SV', yj))
                i += 2
                continue
            i += 1
            continue

        # === ь (soft sign), ъ (hard sign) ===
        if c in ('ь', 'ъ'):
            # NIKL Russian: 어말 ь after nasal/liquid (н/м/л) → 받침 흡수, ㅣ 안 붙임
            # огонь 아곤, Казань 카잔, рубль 루블
            if c == 'ь' and out and out[-1][0] == 'C' and out[-1][1] in ('ㄴ', 'ㅁ', 'ㄹ'):
                if i+1 >= n or s[i+1] not in CYRILLIC_VOWELS:
                    # 어말 또는 자음 앞 → drop ь, C는 받침 처리됨
                    i += 1
                    continue
                # Internal ь before vowel: 받침 + 새 syllable.
                # семья 셈야: м은 받침, я는 새 syllable (ㅇ+ㅑ).
                # 마커로 표시 (assembler에서 처리)
                out.append(('PALATAL_BREAK',))
                i += 1
                continue
            # 어말 ь after other consonants (т/д/в/с/з 등) → emit V ㅣ (palatalize)
            if c == 'ь' and (i+1 >= n) and out and out[-1][0] == 'C':
                # v3.38: 어말 дь → 드 (devoicing+reduction; площадь 플로샤드)
                if out[-1] == ('C', 'ㄷ', 'd'):
                    out.append(('V', 'ㅡ'))
                    i += 1
                    continue
                out.append(('V', 'ㅣ'))
                i += 1
                continue
            i += 1
            continue

        # === DIGRAPHS — Russian doesn't really have multi-letter consonants ===
        # (Cyrillic letters represent single phonemes mostly)

        # === Doubled consonants ===
        # nn/mm/ll → keep gemination (받침 + 새 syllable). Анна → 안나
        # 그 외 → drop one (Россия → 로시야)
        if c == nxt and c in ('н', 'м', 'л'):
            jong_map = {'н':'ㄴ', 'м':'ㅁ', 'л':'ㄹ'}
            # 만약 doubled 다음이 모음이면 GEM (받침+새 syllable). 아니면 받침만 (2번째 자음 drop).
            after_doubled = s[i+2] if i+2 < n else ''
            if after_doubled in CYRILLIC_VOWELS:
                out.append(('GEM', jong_map[c]))
                i += 1
                continue
            else:
                # 어말 또는 자음 앞 → GEM만 (둘 다 소비)
                out.append(('GEM', jong_map[c]))
                i += 2
                continue
        if c == nxt and c in 'бвгджзкпрстфхцчш':
            i += 1
            continue

        # === SINGLE CONSONANTS ===
        if c == 'б':
            out.append(('C', 'ㅂ', 'b'))
            i += 1; continue
        if c == 'в':
            # v3.38: 어말 вь → 피 (devoiced palatalized v): любовь 류보피, церковь 체르코피
            if nxt == 'ь' and i+2 >= n:
                out.append(('C', 'ㅍ', 'vь'))
                out.append(('V', 'ㅣ'))
                i += 2
                continue
            # v3.38: 어말 в → 프 (devoicing): остров 오스트로프
            if i+1 >= n:
                out.append(('C', 'ㅍ', 'v_devoice'))
                i += 1
                continue
            # в before 자음 → 컨텍스트 분기
            if nxt and nxt not in CYRILLIC_VOWELS and nxt not in ('ь', 'ъ'):
                # v3.38: в before sonorant (л/м/н/р) → 브 separate (deree вня → 데레브냐)
                if nxt in 'лмнр':
                    out.append(('C', 'ㅂ', 'v_separate'))
                    i += 1
                    continue
                # 어중 voiceless cons 앞 → ㅂ받침 (Чайковский → 차이콥스키)
                out.append(('C', 'ㅂ', 'v_coda'))
                i += 1
                continue
            if precise:
                out.append(('OLD', V_OLD))
            else:
                out.append(('C', V_OLD, 'v'))
            i += 1; continue
        if c == 'г':
            # v3.38: 어말 г → 크 (devoicing): Екатеринбург 예카테린부르크
            if i+1 >= n:
                out.append(('C', 'ㅋ', 'g_devoice'))
                i += 1; continue
            out.append(('C', 'ㄱ', 'g'))
            i += 1; continue
        if c == 'д':
            # v3.38: д before voiceless cons → ㅌ (devoicing): водка 보트카
            if nxt in ('к','п','т','с','ф','ш','щ','ц','ч','х'):
                out.append(('C', 'ㅌ', 'd_devoice'))
                i += 1; continue
            out.append(('C', 'ㄷ', 'd'))
            i += 1; continue
        if c == 'ж':
            out.append(('C', 'ㅈ', 'zh'))
            i += 1; continue
        if c == 'з':
            # UHPS: /z/ → ㅿ (precise) / ㅈ (basic). 일관성 위해.
            if precise:
                out.append(('OLD', 'ㅿ'))
            else:
                out.append(('C', 'ㅈ', 'z'))
            i += 1; continue
        if c == 'к':
            out.append(('C', 'ㅋ', 'k'))
            i += 1; continue
        if c == 'л':
            out.append(('C', 'ㄹ', 'l'))
            i += 1; continue
        if c == 'м':
            out.append(('C', 'ㅁ', 'm'))
            i += 1; continue
        if c == 'н':
            out.append(('C', 'ㄴ', 'n'))
            i += 1; continue
        if c == 'п':
            out.append(('C', 'ㅍ', 'p'))
            i += 1; continue
        if c == 'р':
            out.append(('C', 'ㄹ', 'r'))
            i += 1; continue
        if c == 'с':
            out.append(('C', 'ㅅ', 's'))
            i += 1; continue
        if c == 'т':
            # v3.38: тс → ㅊ (affricate at cluster, like ц): Иркутск 이르쿠츠크
            if nxt == 'с':
                out.append(('C', 'ㅊ', 'ts'))
                i += 2; continue
            out.append(('C', 'ㅌ', 't'))
            i += 1; continue
        if c == 'ф':
            if precise:
                out.append(('OLD', F))
            else:
                out.append(('C', F, 'f'))
            i += 1; continue
        if c == 'х':
            out.append(('C', 'ㅎ', 'h'))
            i += 1; continue
        if c == 'ц':
            out.append(('C', 'ㅊ', 'ts'))
            i += 1; continue
        if c == 'ч':
            out.append(('C', 'ㅊ', 'ch'))
            i += 1; continue
        if c == 'ш':
            sh_map = {'а':'ㅑ','э':'ㅖ','и':'ㅣ','о':'ㅛ','у':'ㅠ',
                      'е':'ㅖ','ё':'ㅛ','ю':'ㅠ','я':'ㅑ','ы':'ㅣ'}
            if nxt in sh_map:
                out.append(('C', 'ㅅ', 'sh'))
                out.append(('SV', sh_map[nxt]))
                i += 2
                continue
            # 자음 앞 또는 어말: 시 (ㅅ + V ㅣ)
            out.append(('C', 'ㅅ', 'sh'))
            out.append(('V', 'ㅣ'))
            i += 1; continue
        if c == 'щ':
            sh_map = {'а':'ㅑ','э':'ㅖ','и':'ㅣ','о':'ㅛ','у':'ㅠ',
                      'е':'ㅖ','ё':'ㅛ','ю':'ㅠ','я':'ㅑ','ы':'ㅣ'}
            if nxt in sh_map:
                out.append(('C', 'ㅅ', 'shch'))
                out.append(('SV', sh_map[nxt]))
                i += 2
                continue
            # 자음 앞 또는 어말: 시
            out.append(('C', 'ㅅ', 'shch'))
            out.append(('V', 'ㅣ'))
            i += 1; continue

        # 기타 (Latin 알파벳 등)
        out.append(('LIT', s[i]))
        i += 1

    return out


def _intervocalic_l_post(phonemes):
    """Hangul mode: Russian intervocalic L + Cl cluster (v3.38).

    хлеб → 흘레브, блины → 블리니, площадь → 플로샤드 (Cl 패턴)
    """
    CLUSTER_C = {'ㅂ', 'ㅍ', 'ㄱ', 'ㅋ', 'ㄷ', 'ㅌ', 'ㅎ', 'ㆄ'}
    out2 = []
    for k, ph in enumerate(phonemes):
        # Intervocalic l doubling
        if (ph[0] == 'C' and len(ph) == 3 and ph[1] == 'ㄹ' and ph[2] == 'l'
                and k > 0 and phonemes[k-1][0] in ('V', 'SV')
                and k+1 < len(phonemes) and phonemes[k+1][0] in ('V', 'SV')):
            out2.append(('RR', 'ㄹ', 'l_double'))
            continue
        # v3.38: Cl cluster (consonant + l + V → C으ㄹ + ㄹV)
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

        if kind == 'GEM':
            _add_jong_to_last(syllables, ph[1])
            i += 1
            continue

        if kind == 'PALATAL_BREAK':
            # NIKL: 이전 syllable에 받침 ㄴ/ㅁ/ㄹ 강제, 다음 vowel은 새 syllable.
            # 직전 phoneme이 'C'였고 syllable이 그 자음으로 끝나야 함.
            # 직전 syllable의 마지막에 받침 강제 (이미 _compose된 마지막 syll이 cho-only 형태).
            # 마지막 syllable 검사: 자음 단독이면 (e.g., ㅁ) 이전 syllable에 받침으로.
            if syllables and len(syllables[-1]) == 1 and syllables[-1] in ('ㄴ','ㅁ','ㄹ'):
                jong = syllables.pop()
                _add_jong_to_last(syllables, jong)
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

        if kind == 'OLD':
            old = ph[1]
            if _next_is_vowel(phonemes, i):
                v = phonemes[i+1][1]
                syllables.append(old)
                syllables.append(_compose('ㅇ', v))
                i += 2
            elif (i+2 < n and phonemes[i+1][0] == 'C'
                  and phonemes[i+2][0] in ('V', 'SV')):
                next_c = phonemes[i+1]
                next_v = phonemes[i+2]
                cho = next_c[1]
                v = next_v[1]
                syllables.append(old)
                syllables.append(_compose(cho, v))
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
                v = phonemes[i+1][1]
                # SV이면 palatal
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
            # Russian: к, п, т before consonant → 으-syllable (Москва → 모스크바)
            # NOT 받침 (different from German/Spanish)
            if src in ('k', 'g', 'p', 't', 's'):
                syllables.append(_compose(cho, 'ㅡ'))
                i += 1
                continue
            # v_coda: ㅂ받침 (Чайковский → 차이콥스키)
            if src == 'v_coda':
                if syllables and not _has_jong(syllables[-1]):
                    if _add_jong_to_last(syllables, 'ㅂ'):
                        i += 1
                        continue
                syllables.append(_compose('ㅂ', 'ㅡ'))
                i += 1
                continue
            # 그 외: 으-syllable
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
            if ph[1] == 'ㅇ' and len(ph) > 2 and ph[2] in ('y','w','j','й'):
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
def transcribe_ru(text, precise=True, mode='hangul', phonetic=False):
    """Russian Cyrillic → Hangul. mode: 'hangul'/'jamo'/'spaced'."""
    parts = re.split(r'(\s+|[^\w])', text)
    out = []
    for part in parts:
        if not part:
            continue
        if not re.match(r'^[А-Яа-яЁёA-Za-z]+$', part):
            out.append(part)
            continue
        phs_raw = _phonemize(part, precise)
        if mode == 'hangul':
            phs = _intervocalic_l_post(phs_raw)
            han = _assemble(phs, precise)
            out.append(han)
            continue
        elif mode == 'jamo':
            out.append(_to_jamo_seq(phs_raw))
            continue
        elif mode == 'spaced':
            out.append(' '.join(_to_jamo_seq(phs_raw)))
            continue
        # legacy fallback
        phs = _phonemize(part, precise)
        han = _assemble(phs, precise)
        out.append(han)
    return ''.join(out)


# === Test ===
if __name__ == '__main__':
    tests = [
        # (input, expected_precise, expected_basic)
        ('Москва', '모스크ㅸ아', '모스크바'),
        ('Россия', '로시야', '로시야'),
        ('Толстой', '톨스토이', '톨스토이'),
        ('Чайковский', '차이콥스키', '차이콥스키'),
        ('Достоевский', '도스토옙스키', '도스토옙스키'),
        ('Пушкин', '푸시킨', '푸시킨'),
        ('Иван', '이ㅸ안', '이반'),
        ('Кремль', '크렘리', '크렘리'),
        ('Путин', '푸틴', '푸틴'),
        ('Сибирь', '시비리', '시비리'),
        ('Ленин', '레닌', '레닌'),
        ('Анна', '안나', '안나'),
        ('борщ', '보르시', '보르시'),
        ('водка', 'ㅸ오드카', '보드카'),
        ('Юрий', '유리', '유리'),
        ('Михаил', '미하일', '미하일'),
        ('Кирилл', '키릴', '키릴'),
        ('Дмитрий', '드미트리', '드미트리'),
        ('хорошо', '호로쇼', '호로쇼'),
        ('спасибо', '스파시보', '스파시보'),
    ]

    print("=== RUSSIAN PRECISE ===")
    p_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_ru(inp, precise=True)
        ok = '✓' if r == exp_p else '✗'
        if ok == '✓': p_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_p})")
    print(f"\nPRECISE: {p_ok}/{len(tests)}")

    print("\n=== RUSSIAN BASIC ===")
    b_ok = 0
    for inp, exp_p, exp_b in tests:
        r = transcribe_ru(inp, precise=False)
        ok = '✓' if r == exp_b else '✗'
        if ok == '✓': b_ok += 1
        print(f"  {ok} {inp:<22} → {r:<22} (expected: {exp_b})")
    print(f"\nBASIC: {b_ok}/{len(tests)}")
