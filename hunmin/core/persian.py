"""Hunmin Precise — Persian/Farsi (fa) Arabic-script → Hangul.

NIKL 외래어 표기법 페르시아어 핵심:
  - Arabic 문자 + Persian 추가 자모 (پ چ ژ گ)
  - Short vowels는 글자로 안 적힘 — schwa 'a' 자동 삽입
  - 매핑 (NIKL):
      ا → 아 (or initial vowel carrier)
      ب → ㅂ, پ → ㅍ, ت → ㅌ, ث → ㅅ
      ج → ㅈ, چ → ㅊ, ح → ㅎ, خ → 흐
      د → ㄷ, ذ → ㅈ, ر → ㄹ, ز → ㅈ, ژ → 주
      س → ㅅ, ش → ㅅ palatal, ص → ㅅ, ض → ㅈ
      ط → ㅌ, ظ → ㅈ, ع → silent, غ → 흐
      ف → ㅍ (또는 ㆄ in precise), ق → ㄱ
      ک → ㅋ, گ → ㄱ, ل → ㄹ
      م → ㅁ, ن → ㄴ, و → ㅂ/ㅜ, ه → ㅎ, ی → ㅣ/ㅇ+y
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


# Persian consonant → Hangul (NIKL)
CONS_MAP = {
    'ب':'ㅂ','پ':'ㅍ','ت':'ㅌ','ث':'ㅅ',
    'ج':'ㅈ','چ':'ㅊ','ح':'ㅎ','خ':'ㅎ',  # خ = 흐 (separate -syll)
    'د':'ㄷ','ذ':'ㅈ','ر':'ㄹ','ز':'ㅈ','ژ':'ㅈ',
    'س':'ㅅ','ش':'ㅅ','ص':'ㅅ','ض':'ㅈ',
    'ط':'ㅌ','ظ':'ㅈ',
    'غ':'ㄱ',  # 흐/ㄱ — NIKL: 가/ㄱ
    'ف':'ㅍ','ق':'ㄱ','ك':'ㅋ','ک':'ㅋ','گ':'ㄱ',
    'ل':'ㄹ','م':'ㅁ','ن':'ㄴ','ه':'ㅎ',
    # و, ي/ی는 별도 처리 (vowel/glide)
}

# Long vowel anchors
LONG_VOWELS = {
    'ا': 'ㅏ',  # alef = long /ɒː/ NIKL → 아
    'آ': 'ㅏ',  # alef madda = long a → 아
    'و': 'ㅜ',  # vav (vowel) = long /uː/ → 우
    'ی': 'ㅣ',  # ya (vowel) = long /iː/ → 이
    'ي': 'ㅣ',
}

# Vowel diacritics (rare)
DIACRITIC_VOWELS = {
    'َ': 'ㅏ',   # fatha
    'ِ': 'ㅣ',   # kasra (실제는 e인데 i 근사)
    'ُ': 'ㅗ',   # damma (실제는 o)
}

DEFAULT_VOWEL = 'ㅏ'  # 자음 사이 default schwa → 아


def _is_persian_letter(c):
    return c in CONS_MAP or c in LONG_VOWELS or c in DIACRITIC_VOWELS


def _phonemize(word, precise=False):
    """Persian word → list of jamo tokens.
    Strategy: 자음 + 다음 글자 결합 (vowel anchor 없으면 default 'ㅏ').
    """
    s = word
    F = 'ㆄ' if precise else 'ㅍ'
    out = []
    i = 0
    n = len(s)

    while i < n:
        c = s[i]
        nxt = s[i+1] if i+1 < n else ''

        # ا/آ at start: silent carrier — 다음 글자에 의존
        if i == 0 and c in ('ا', 'آ'):
            # 첫 alef: '아' syllable 또는 다음 vowel 결정 위해 skip
            # 일반적으로 آ → '아', ا 단독 시작은 보통 'a'
            if nxt in DIACRITIC_VOWELS:
                v = DIACRITIC_VOWELS[nxt]
                out.append(_compose('ㅇ', v))
                i += 2; continue
            out.append(_compose('ㅇ', 'ㅏ'))
            i += 1; continue

        # ع: silent
        if c == 'ع':
            i += 1; continue

        # ی/ي semi-vowel: 자음 뒤면 vowel modifier, 어두면 'ㅇ + y-vowel'
        if c in ('ی', 'ي'):
            # 어말이면 'ㅣ' single
            if not nxt or not _is_persian_letter(nxt):
                out.append(_compose('ㅇ', 'ㅣ'))
            else:
                # vowel position 'ㅣ'
                out.append(_compose('ㅇ', 'ㅣ'))
            i += 1; continue

        # و: vowel /uː/ when after consonant, 또는 /v/ initial
        if c == 'و':
            if i == 0:
                # 어두 و = /v/ → ㅂ (NIKL) or ㅸ precise
                cho = 'ㅸ' if precise else 'ㅂ'
                # 다음 vowel과 결합
                v = 'ㅏ'
                if nxt in DIACRITIC_VOWELS:
                    v = DIACRITIC_VOWELS[nxt]
                    out.append(_compose(cho, v))
                    i += 2; continue
                out.append(_compose(cho, v))
                i += 1; continue
            # 자음 뒤 و → 'ㅜ' vowel 형성
            if out and len(out[-1]) == 1 and 0xAC00 <= ord(out[-1]) <= 0xD7A3:
                # 직전이 syllable이면 'ㅜ' 추가
                out.append(_compose('ㅇ', 'ㅜ'))
            else:
                out.append(_compose('ㅇ', 'ㅜ'))
            i += 1; continue

        # ا/آ: long /ɒ/ → 아
        if c in ('ا', 'آ'):
            out.append(_compose('ㅇ', 'ㅏ'))
            i += 1; continue

        # خ → 흐 separate (어말) or 'ㅎ + V'
        if c == 'خ':
            if nxt in DIACRITIC_VOWELS:
                v = DIACRITIC_VOWELS[nxt]
                out.append(_compose('ㅎ', v))
                i += 2; continue
            elif nxt in LONG_VOWELS:
                v = LONG_VOWELS[nxt]
                out.append(_compose('ㅎ', v))
                i += 2; continue
            elif _is_persian_letter(nxt):
                # 다음 자음 — schwa 삽입
                out.append(_compose('ㅎ', DEFAULT_VOWEL))
            else:
                # 어말
                out.append('흐')
            i += 1; continue

        # 일반 자음
        if c in CONS_MAP:
            cho = CONS_MAP[c]
            if c == 'ف' and precise:
                cho = F
            # 다음 글자 보고 vowel 결정
            if nxt in DIACRITIC_VOWELS:
                v = DIACRITIC_VOWELS[nxt]
                out.append(_compose(cho, v))
                i += 2; continue
            elif nxt in LONG_VOWELS:
                v = LONG_VOWELS[nxt]
                out.append(_compose(cho, v))
                i += 2; continue
            elif nxt and _is_persian_letter(nxt):
                # 다음 자음 → schwa 삽입
                out.append(_compose(cho, DEFAULT_VOWEL))
                i += 1; continue
            else:
                # 어말
                # 받침 가능: ㄴ/ㅁ/ㄹ/ㅇ — 받침으로 흡수
                if (out and len(out[-1]) == 1 and 0xAC00 <= ord(out[-1]) <= 0xD7A3
                        and cho in ('ㄴ','ㅁ','ㄹ')):
                    base = ord(out[-1]) - HANGUL_BASE
                    cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
                    if jong_idx == 0:
                        out[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index(cho))
                        i += 1; continue
                # 어말 자음 → ㅡ-syll
                mute = {'ㅂ':'브','ㅍ':'프','ㄷ':'드','ㅌ':'트','ㄱ':'그','ㅋ':'크',
                         'ㅈ':'즈','ㅊ':'츠','ㅁ':'므','ㄴ':'느','ㄹ':'르','ㅅ':'스','ㅎ':'흐'}
                out.append(mute.get(cho, _compose(cho, 'ㅡ')))
                i += 1; continue

        # Diacritic alone (이전 자음에 attach 못 했을 때)
        if c in DIACRITIC_VOWELS:
            i += 1; continue

        # 모르는 글자 — pass
        i += 1

    return out


# v3.38: NIKL Persian word-specific overrides
# (Persian short vowels not written → 음운 룰만으로는 정확도 한계.
#  실제 발음 기반 transliteration을 단어별로 매핑.)
_HANGUL_OVERRIDES = {
    'خانه': '하네', 'خانواده': '하네바데', 'عشق': '에시크',
    'ماه': '마', 'آب': '압', 'کوه': '쿠', 'شهر': '샤르',
    'کتابخانه': '케타바네', 'پل': '펄', 'جنگل': '잔갈',
    'کباب': '카밥', 'پلو': '펠로', 'مدرسه': '마드라세',
    'دانشگاه': '다네시가', 'رستوران': '레스토란', 'بازار': '바자르',
    'میدان': '메이단', 'جزیره': '자지레', 'تهران': '테헤란',
    'مشهد': '마샤드', 'کرمان': '케르만', 'مسجد': '마세이드',
    'دریاچه': '다리아체', 'اصفهان': '에스파한', 'بیمارستان': '비마레스탄',
    'آتش': '아타시', 'روستا': '루스타', 'پارک': '파르크',
    'آفتاب': '아프타브', 'تبریز': '타브리즈',
}


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Persian/Farsi text → Hangul (NIKL convention)."""
    parts = re.split(r'(\s+|[,.!?;:،؛؟])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:،؛؟]', part):
            out.append(part); continue
        # v3.38: word-specific override (NIKL convention, hangul mode + not precise/phonetic만)
        if mode == 'hangul' and not precise and not phonetic and part in _HANGUL_OVERRIDES:
            out.append(_HANGUL_OVERRIDES[part])
            continue
        syls = _phonemize(part, precise=precise)
        out.append(''.join(syls))
    return ''.join(out)
