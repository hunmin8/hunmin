"""Hunmin Precise — Arabic (ar) Arabic-script → Hangul.

NIKL 외래어 표기법 아랍어 핵심:
  - Arabic 문자는 short vowels 표기 안 함 → schwa /a/ 자동 삽입
  - Long vowels: ا (alif=아), و (waw=우), ي (ya=이)
  - 자모:
      ب→ㅂ, ت→ㅌ, ث→ㅅ, ج→ㅈ, ح→ㅎ, خ→ㅎ
      د→ㄷ, ذ→ㅈ, ر→ㄹ, ز→ㅈ, س→ㅅ, ش→ㅅ
      ص→ㅅ, ض→ㄷ, ط→ㅌ, ظ→ㅈ, ع→silent, غ→ㅎ
      ف→ㅍ, ق→ㄱ, ك→ㅋ, ل→ㄹ, م→ㅁ, ن→ㄴ, ه→ㅎ
  - hamza (ء) → 어두 silent / 어중 마찰
  - shadda (ّ) → 자음 doubling (NIKL: ignore)
  - ال (al-) 정관사 → 알- (sun letters에서 동화)
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


CONS_MAP = {
    'ب':'ㅂ','ت':'ㅌ','ث':'ㅅ','ج':'ㅈ','ح':'ㅎ','خ':'ㅎ',
    'د':'ㄷ','ذ':'ㅈ','ر':'ㄹ','ز':'ㅈ','س':'ㅅ','ش':'ㅅ',
    'ص':'ㅅ','ض':'ㄷ','ط':'ㅌ','ظ':'ㅈ','غ':'ㄱ',
    'ف':'ㅍ','ق':'ㄱ','ك':'ㅋ','ل':'ㄹ','م':'ㅁ','ن':'ㄴ','ه':'ㅎ',
    'ك':'ㅋ',  # u+0643
}

# Long vowel anchors
LONG_VOWELS = {
    'ا': 'ㅏ',  # alif
    'آ': 'ㅏ',  # alif madda
    'و': 'ㅜ',  # waw (vowel context)
    'ي': 'ㅣ',  # ya (vowel context)
    'ى': 'ㅏ',  # alef maksura → 'a'
}

# Short vowel diacritics (rare in modern text)
DIACRITIC = {
    'َ': 'ㅏ',  # fatha
    'ِ': 'ㅣ',  # kasra
    'ُ': 'ㅜ',  # damma
    'ً': 'ㅏ',  # fathatan
    'ٍ': 'ㅣ',  # kasratan
    'ٌ': 'ㅜ',  # dammatan
    'ْ': '',    # sukun (no vowel)
    'ّ': '',    # shadda (doubling — NIKL ignore)
}


def _phonemize(word, precise=False):
    """Arabic word → list of hangul syllables."""
    s = word
    n = len(s)
    out = []
    i = 0
    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # Skip diacritics (assumed unwritten in most NIKL inputs)
        if c in DIACRITIC:
            i += 1
            continue

        # Hamza (ء) — usually silent at word start
        if c == 'ء':
            i += 1
            continue
        if c in ('أ', 'إ'):  # alif with hamza
            out.append(_compose('ㅇ', 'ㅏ'))
            i += 1
            continue
        if c == 'ؤ':  # waw with hamza
            out.append(_compose('ㅇ', 'ㅜ'))
            i += 1
            continue
        if c == 'ئ':  # ya with hamza
            out.append(_compose('ㅇ', 'ㅣ'))
            i += 1
            continue
        if c == 'ة':  # ta marbuta (어말 → ㅏ)
            out.append(_compose('ㅇ', 'ㅏ'))
            i += 1
            continue

        # Long vowel (in vowel position — usually after consonant)
        if c in LONG_VOWELS:
            v = LONG_VOWELS[c]
            # Check if previous was consonant — append to it
            if out and len(out[-1]) == 1 and 0xAC00 <= ord(out[-1]) <= 0xD7A3:
                last = out[-1]
                base = ord(last) - HANGUL_BASE
                cho_idx = base // 588
                jung_idx = (base % 588) // 28
                jong_idx = base % 28
                # 자음+ㅏ 기본 → 자음+long-vowel
                if jung_idx == VOWELS_J.index('ㅏ') and jong_idx == 0:
                    out[-1] = _compose(INITIALS[cho_idx], v)
                    i += 1
                    continue
            # Otherwise standalone vowel
            out.append(_compose('ㅇ', v))
            i += 1
            continue

        # Consonant
        if c in CONS_MAP:
            cho = CONS_MAP[c]
            # 자음 + 자음 (or end) → 자음 + ㅡ (transcribed) 또는 받침
            # NIKL Arabic: short 'a' default 삽입
            # 다음이 모음이면 그 모음 사용, 자음이면 default ㅏ
            nxt_is_vowel = nxt in LONG_VOWELS or nxt in DIACRITIC
            if nxt_is_vowel:
                # Will be merged with next vowel
                out.append(_compose(cho, 'ㅏ'))
            elif i + 1 == n:
                # Word end — append as separate or 받침
                # 'l/m/n/r' → 받침 가능
                if cho in ('ㄴ', 'ㅁ', 'ㄹ', 'ㅇ', 'ㅂ', 'ㄱ', 'ㅅ') and out:
                    last = out[-1]
                    if (len(last) == 1 and 0xAC00 <= ord(last) <= 0xD7A3
                        and (ord(last) - HANGUL_BASE) % 28 == 0):
                        base = ord(last) - HANGUL_BASE
                        cho_idx = base // 588
                        jung_idx = (base % 588) // 28
                        out[-1] = chr(HANGUL_BASE + cho_idx*588
                                      + jung_idx*28 + FINALS.index(cho))
                        i += 1
                        continue
                out.append(_compose(cho, 'ㅡ'))
            else:
                # Mid-word — default 'a' inherent
                out.append(_compose(cho, 'ㅏ'))
            i += 1
            continue

        # ع (ayn) — silent
        if c == 'ع':
            i += 1
            continue

        # Whitespace / punctuation / unknown
        out.append(c)
        i += 1

    return out


# 자주 쓰이는 아랍어 단어/지명/문화 (NIKL 표기 — table-driven)
_HANGUL_OVERRIDES = {
    # 인사/일상
    'سلام': '살람',
    'مرحبا': '마르하바',
    'شكرا': '슈크란',
    'نعم': '나암',
    'لا': '라',
    # 지명
    'القاهرة': '카이로',
    'بغداد': '바그다드',
    'دمشق': '다마스쿠스',
    'الرياض': '리야드',
    'دبي': '두바이',
    'مكة': '메카',
    'المدينة': '메디나',
    'القدس': '예루살렘',
    'بيروت': '베이루트',
    'الدوحة': '도하',
    'عمان': '암만',
    'الخرطوم': '하르툼',
    'الجزائر': '알제',
    'تونس': '튀니스',
    'الرباط': '라바트',
    'طرابلس': '트리폴리',
    'صنعاء': '사나',
    'مسقط': '무스카트',
    'الكويت': '쿠웨이트',
    # 음식/문화
    'كباب': '케밥',
    'فلافل': '팔라펠',
    'حمص': '후무스',
    'كسكس': '쿠스쿠스',
    'بقلاوة': '바클라바',
    # 종교/문화
    'القرآن': '쿠란',
    'الإسلام': '이슬람',
    'مسجد': '모스크',
    'إمام': '이맘',
    'حلال': '할랄',
    'حرام': '하람',
    # 인명 (대표적)
    'محمد': '무함마드',
    'علي': '알리',
    'حسن': '하산',
    'حسين': '후세인',
}


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Arabic text → Hangul (NIKL convention).

    NIKL 외래어 표기법 — Arabic short vowels는 표기되지 않으므로
    word-specific override가 우선. 룰만으로는 거친 근사.
    """
    parts = re.split(r'(\s+|[,.!?;:،؛؟])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:،؛؟]', part):
            out.append(part); continue
        # Override 우선
        if mode == 'hangul' and not precise and not phonetic and part in _HANGUL_OVERRIDES:
            out.append(_HANGUL_OVERRIDES[part])
            continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)


if __name__ == '__main__':
    samples = [
        ('سلام', '살람'),
        ('القاهرة', '카이로'),
        ('بغداد', '바그다드'),
        ('دبي', '두바이'),
        ('كباب', '케밥'),
        ('القرآن', '쿠란'),
        ('محمد', '무함마드'),
    ]
    for inp, exp in samples:
        r = transcribe(inp)
        ok = '✓' if r == exp else '✗'
        print(f'{ok} {inp:15} → {r:15} (expected: {exp})')
