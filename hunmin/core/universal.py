"""Universal IPA → UHPS Hangul transcriber.

100+ 언어를 한글 발음 표기로 변환. epitran 라이브러리로 IPA 추출 →
UHPS jamo 매핑 → Hangul 음절 합성.

설치: pip install hunmin[universal]  (epitran 필요)

지원 언어 (epitran 매핑 162개):
  spa, fra, deu, ita, por, nld, swe, dan, nor, fin, pol, ces, ron,
  hun, ell, tur, vie, hau, swh, amh, hin, ben, urd, ara, fas, tha,
  ind, msa, fil, jav, ... (전체 162개)
"""
import re
import unicodedata


# === IPA phoneme → UHPS v2 jamo (옛한글 + 한글 자모 확장 사용) ===
# IPA 78개 phoneme을 한글 자모에 1:1 매핑. precise=True일 때 활용.
# basic (precise=False)은 modern Korean 자모로 대체.
#
# 사용 자모 (Unicode):
#   현대 한글 (U+3131-U+318F)
#   옛한글: ㆄ U+3184 (/f/), ㅸ U+3178 (/v/), ㅿ U+317F (/z/),
#          ㆁ U+3181 (/ŋ/), ㆆ U+3186 (/ʔ/), ㆅ U+3185 (/x/, 쌍히읗)
#          ㅱ U+3171 (/ɱ/, 미음+이응)
#          ㅥ U+3165 (/ɲ/, 쌍니은)
#          ㅼ U+317C (/θ/, 시옷+디귿) — 영어 think
#          ㅽ U+317D (/ð/, 시옷+비읍) — 영어 this
#          ᄾ U+113E (/ʃ/, 치두음 시옷) — 영어 shoe (mandarin sibilant)
#          ᄶ U+1136 (/ʒ/, 치두음 지읒) — 영어 pleasure
#          ᄛ U+111B (/ʁ/, 가벼운 ㄹ) — 프랑스 R
#          ㆍ U+318D (/ɑ/, 아래아) — 영어 father
#          ㆎ U+318E (/ɔ/, 아래아+이) — 영어 caught
#          ㅙ U+3159 (/œ/) — 프랑스 oeuvre (재활용)

_IPA_PHONEMES = {
    # === Plosives ===
    'p': ('C', 'ㅍ'), 'b': ('C', 'ㅂ'),
    't': ('C', 'ㅌ'), 'd': ('C', 'ㄷ'),
    'k': ('C', 'ㅋ'), 'ɡ': ('C', 'ㄱ'), 'g': ('C', 'ㄱ'),
    'q': ('C', 'ㅋ'),  # uvular k (rough — same as k)
    'ɢ': ('C', 'ㄱ'),  # uvular g — merge to k-voiced
    'ʈ': ('C', 'ㅌ'),  # retroflex t (Hindi/Mandarin context — merger to t)
    'ɖ': ('C', 'ㄷ'),  # retroflex d
    'c': ('C', 'ㅋ'),  # palatal k (rare; merge to k)
    'ɟ': ('C', 'ㅈ'),  # palatal g (Hungarian gy)
    'ʔ': ('C', 'ㆆ'),  # glottal stop — 옛한글 여린히읗
    # 흡착음/임플로시브 (rough)
    'ɓ': ('C', 'ㅂ'), 'ɗ': ('C', 'ㄷ'), 'ɠ': ('C', 'ㄱ'),
    # === Nasals ===
    'm': ('C', 'ㅁ'), 'n': ('C', 'ㄴ'),
    'ɲ': ('C_PALATAL_N', 'ㅥ'),  # palatal n — 쌍니은 U+3165 (palatalize next vowel)
    'ŋ': ('C', 'ㆁ'),  # velar n — 옛한글 옛이응
    'ɴ': ('C', 'ㆁ'),  # uvular n
    'ɳ': ('C', 'ㄴ'),  # retroflex n — merge to n
    'ɱ': ('C', 'ㅱ'),  # labiodental m — 옛한글 미음+이응 U+3171
    # === Fricatives ===
    'f': ('OLD', 'ㆄ'),     # /f/ — 옛한글 피읖+이응 U+3184
    'v': ('OLD', 'ㅸ'),     # /v/ — 옛한글 비읍+이응 U+3178
    'ɸ': ('OLD', 'ㆄ'),     # bilabial f
    'β': ('OLD', 'ㅸ'),     # bilabial v
    's': ('C', 'ㅅ'),
    'z': ('OLD', 'ㅿ'),     # /z/ — 반시옷 U+317F
    'θ': ('OLD', 'ㅼ'),     # English 'think' th — 시옷+디귿 U+317C
    'ð': ('OLD', 'ㅽ'),     # English 'this' th — 시옷+비읍 U+317D
    'ʃ': ('OLD', 'ᄾ'),     # English 'shoe' — 치두음 시옷 U+113E
    'ʒ': ('OLD', 'ᄶ'),     # English 'pleasure' — 치두음 지읒 U+1136
    'ɕ': ('OLD', 'ᄾ'),     # alveolo-palatal s
    'ʑ': ('OLD', 'ᄶ'),     # alveolo-palatal z
    'ʂ': ('OLD', 'ᄾ'),     # retroflex s
    'ʐ': ('OLD', 'ᄶ'),     # retroflex z
    'h': ('C', 'ㅎ'), 'ɦ': ('C', 'ㅎ'),
    'x': ('OLD', 'ㆅ'),     # German 'Bach' — 쌍히읗 U+3185
    'ɣ': ('OLD', 'ㆅ'),     # voiced velar fricative
    'ç': ('OLD', 'ㆅ'),     # German 'ich' — palatal h
    'ʝ': ('SV_MARKER', 'y'), # voiced palatal fricative — y-glide (Greek/Czech)
    'χ': ('OLD', 'ㆅ'),     # uvular x
    'ʁ': ('OLD', 'ᄛ'),     # French R — 가벼운 ㄹ U+111B
    'ʀ': ('OLD', 'ᄛ'),     # uvular trilled R
    'ʙ': ('C', 'ㅂ'),       # bilabial trill — merge to b
    'ħ': ('OLD', 'ㆅ'),     # Arabic pharyngeal h
    'ʕ': ('C', 'ㆆ'),       # Arabic pharyngeal voiced (~ glottal)
    'ʜ': ('OLD', 'ㆅ'),
    'ʢ': ('C', 'ㆆ'),
    'ɬ': ('OLD', 'ㅼ'),     # voiceless lateral fricative (Welsh ll) — merge to θ approximant
    # === Approximants ===
    'ɻ': ('C', 'ㄹ'),       # retroflex approximant — merge to r
    'ɰ': ('SV_MARKER', 'w'), # velar approximant — w-glide
    'ʟ': ('C', 'ㄹ'),       # velar lateral approximant
    # === Affricates (multi-char digraphs handled separately) ===
    'ʧ': ('C', 'ㅊ'),  # tʃ
    'ʤ': ('C', 'ㅈ'),  # dʒ
    'ʦ': ('C', 'ㅊ'),  # ts
    'ʣ': ('C', 'ㅈ'),  # dz
    # === Liquids ===
    'l': ('C', 'ㄹ'), 'ɭ': ('C', 'ㄹ'), 'ɮ': ('C', 'ㄹ'), 'ʎ': ('C', 'ㄹ'),
    'r': ('C', 'ㄹ'), 'ɾ': ('C', 'ㄹ'), 'ɹ': ('C', 'ㄹ'),
    'ɽ': ('C', 'ㄹ'),
    # === Glides / Approximants ===
    'j': ('SV_MARKER', 'y'),
    'w': ('SV_MARKER', 'w'),
    'ɥ': ('SV_MARKER', 'y'),
    'ʋ': ('OLD', 'ㅸ'),
    # === R-colored vowels (English ɚ, ɝ) ===
    'ɚ': ('V_R', 'ㅓ'),  # r-colored schwa (English butter)
    'ɝ': ('V_R', 'ㅓ'),  # r-colored ɜ
    # === Vowels ===
    # Front
    'i': ('V', 'ㅣ'), 'ɪ': ('V', 'ㅣ'),
    'e': ('V', 'ㅔ'), 'ɛ': ('V', 'ㅔ'),
    'æ': ('V', 'ㅐ'), 'a': ('V', 'ㅏ'),
    # Front rounded
    'y': ('V', 'ㅟ'), 'ʏ': ('V', 'ㅟ'),
    'ø': ('V', 'ㅚ'), 'œ': ('V', 'ㅙ'),  # ø vs œ 구별
    # Central
    'ɨ': ('V', 'ㅡ'), 'ʉ': ('V', 'ㅡ'),
    'ə': ('V', 'ㅓ'), 'ɵ': ('V', 'ㅓ'),
    'ɐ': ('V', 'ㅏ'),
    'ɘ': ('V', 'ㅓ'),  # close-mid central unrounded — merge to schwa
    'ɜ': ('V', 'ㅓ'),  # open-mid central unrounded — merge to schwa
    'ɞ': ('V', 'ㅓ'),  # open-mid central rounded — merge to schwa
    'ɶ': ('V', 'ㅙ'),  # open front rounded — merge to œ
    # Back
    'ɯ': ('V', 'ㅡ'), 'u': ('V', 'ㅜ'), 'ʊ': ('V', 'ㅜ'),
    'ɤ': ('V', 'ㅓ'), 'o': ('V', 'ㅗ'),
    'ʌ': ('V', 'ㅓ'),
    'ɔ': ('OLD', 'ㆎ'),    # /ɔ/ — 아래아+이 (open-mid back rounded) U+318E
    'ɑ': ('OLD', 'ㆍ'),    # /ɑ/ — 아래아 (open back unrounded) U+318D
    'ɒ': ('OLD', 'ㆍ'),    # /ɒ/ — open back rounded
    # 비음 모음 (French) — V + 코다 ㆁ 추가
    'ã': ('V_NASAL', 'ㅏ'),
    'ɛ̃': ('V_NASAL', 'ㅔ'),
    'ɔ̃': ('V_NASAL', 'ㆎ'),
    'œ̃': ('V_NASAL', 'ㅙ'),
}

# 다중자 IPA → 단일 토큰 변환 (preprocessing)
# Order matters: longer/more-specific patterns first (with tie bar before without)
_IPA_DIGRAPHS = [
    # with tie bar (U+0361)
    ('t͡ʃ', 'ʧ'), ('d͡ʒ', 'ʤ'),
    ('t͡ɕ', 'ʧ'), ('d͡ʑ', 'ʤ'),   # alveolo-palatal (Mandarin j/q, Vietnamese ch)
    ('t͡ʂ', 'ʧ'), ('d͡ʐ', 'ʤ'),   # retroflex (using plain t/d)
    ('ʈ͡ʂ', 'ʧ'), ('ɖ͡ʐ', 'ʤ'),   # retroflex (true retroflex stop letters: Mandarin zh/ch, Polish cz)
    ('t͡s', 'ʦ'), ('d͡z', 'ʣ'),
    # without tie bar
    ('tʃ', 'ʧ'),  ('dʒ', 'ʤ'),
    ('tɕ', 'ʧ'),  ('dʑ', 'ʤ'),
    ('tʂ', 'ʧ'),  ('dʐ', 'ʤ'),
    ('ʈʂ', 'ʧ'),  ('ɖʐ', 'ʤ'),
    ('ts', 'ʦ'),  ('dz', 'ʣ'),
]
_IPA_PHONEMES['ʧ'] = ('C', 'ㅊ')
_IPA_PHONEMES['ʤ'] = ('C', 'ㅈ')
_IPA_PHONEMES['ʦ'] = ('C', 'ㅊ')
_IPA_PHONEMES['ʣ'] = ('C', 'ㅈ')

# === 폰트 호환성 fallback ===
# 결합 Hangul Jamo 블록 (U+1100~11FF)는 단독 표시 미지원 폰트 많음
# safe_fonts=True 모드에서 Compat 블록(U+3131~318F) 또는 modern jamo로 대체
_FONT_SAFE_FALLBACK = {
    'ᄾ': 'ㅅ',   # /ʃ/ — 치두음 시옷 → 시옷 (구별 손실)
    'ᄶ': 'ㅈ',   # /ʒ/ — 치두음 지읒 → 지읒
    'ᄛ': 'ㄹ',   # /ʁ/ — 가벼운 ㄹ → ㄹ
}

# Y/W + 모음 → palatal/W vowel (existing UHPS pattern)
_Y_VOWEL = {'ㅏ':'ㅑ','ㅐ':'ㅒ','ㅓ':'ㅕ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ','ㅡ':'ㅡ'}
_W_VOWEL = {'ㅏ':'ㅘ','ㅐ':'ㅙ','ㅓ':'ㅝ','ㅔ':'ㅞ','ㅗ':'ㅗ','ㅜ':'ㅜ','ㅣ':'ㅟ'}


# IPA diacritics 정책 (UHPS 모드별)
# UHPS-core (level=3): phoneme 중심, suprasegmental 제거
# UHPS-full (level=5): 장단/성조/강세/aspiration/labialization 모두 보존
_REMOVE_DIACRITICS_BASIC = {  # level=1 (대중) — 모두 제거
    'ː', 'ˑ', 'ˈ', 'ˌ', '͡', '̩', '̯',
    'ʰ', 'ʷ', 'ʲ', '̞', '̥', '̬', 'ˀ',
    '˥', '˦', '˧', '˨', '˩',
    '1','2','3','4','5',
}
_REMOVE_DIACRITICS_CORE = {  # level=3 UHPS-core — phoneme tie/syllable mark만 제거
    '͡', '̩', '̯',
    'ʰ', 'ʷ', 'ʲ',
    '̞', '̥', '̬', 'ˀ',
}
_REMOVE_DIACRITICS_FULL = {  # level=5 UHPS-full — phoneme tie만 제거 (나머지는 모두 보존)
    '͡',
}

# 옛 훈민정음 방점 (傍點) — Hangul tone marks
_PANJEOM_HIGH = '〮'   # 〮 거성 (high tone, 1 dot)
_PANJEOM_RISING = '〯'  # 〯 상성 (rising tone, 2 dots)


HANGUL_BASE = 0xAC00
INITIALS = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
            'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
VOWELS = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ',
          'ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
FINALS = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ',
          'ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
          'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


def _compose(cho, jung, jong=''):
    if cho in INITIALS and jung in VOWELS:
        c = INITIALS.index(cho); j = VOWELS.index(jung)
        f = FINALS.index(jong) if jong in FINALS else 0
        return chr(HANGUL_BASE + c*588 + j*28 + f)
    return cho + jung + jong


def _normalize_ipa(ipa, uhps='basic'):
    """IPA preprocess. uhps mode:
    'basic' — phoneme만, suprasegmental 모두 제거 (level=1)
    'core'  — UHPS-core: 자음/모음 옛한글 매핑, 일부 diacritic 제거 (level=3)
    'full'  — UHPS-full: 장단/성조/강세까지 모두 보존 (level=5)
    """
    s = ipa
    # full 모드에선 NFD 분해 — 결합 톤 마크(́ ̀ ̌ ̂ etc) 인식하기 위함.
    # basic/core 모드는 NFC 유지 (precomposed 한 음소 매핑 가능).
    if uhps == 'full':
        s = unicodedata.normalize('NFD', s)
    else:
        s = unicodedata.normalize('NFC', s)
    # NIKL palatalized stops (Russian /tʲ/ /dʲ/) → soft consonant ㄷ
    # 'ʲ' is otherwise stripped by REMOVE_DIACRITICS, so handle explicitly first.
    s = s.replace('tʲ', 'd̥').replace('dʲ', 'd')
    for src, dst in _IPA_DIGRAPHS:
        s = s.replace(src, dst)
    if uhps == 'basic':
        diacritics = _REMOVE_DIACRITICS_BASIC
    elif uhps == 'core':
        diacritics = _REMOVE_DIACRITICS_CORE
    else:  # full
        diacritics = _REMOVE_DIACRITICS_FULL
    for d in diacritics:
        s = s.replace(d, '')
    return s


_NASAL_MAP = {
    'ɔ': 'ㆎ', 'a': 'ㅏ', 'ɛ': 'ㅔ', 'œ': 'ㅙ',
    'ã': 'ㅏ', 'õ': 'ㅗ', 'ɑ': 'ㆍ',
    'i': 'ㅣ', 'u': 'ㅜ', 'e': 'ㅔ', 'o': 'ㅗ',
}

# === Suprasegmental — IPA 운율 표기 ===
# v3.1: 5-tone category (H/R/D/F/L) + tone_style 별 시각화.
# Tone categories — abstract ID, 시각 표기에 의존하지 않음:
#   H = high level (高平 / level-5)        — Mandarin 1성, IPA ˥ ˦, ́ acute
#   R = rising (上聲 / mid→high)            — Mandarin 2성, IPA ˧˥, ̌ caron
#   D = dipping (低降昇 / low-fall-rise)    — Mandarin 3성, IPA ˨˩˦
#   F = falling (去聲 / high→low)            — Mandarin 4성, IPA ˥˩, ̂ circumflex
#   L = low (低 / level-1)                   — IPA ˨ ˩, ̀ grave
#   M = mid (level-3) / N = neutral          — 표시 없음 (생략)
#   STRESS = lexical stress                  — 별도 (강세는 tone과 다름)
TONE_STYLES = {
    # 분절체계용 stress/length만 박은 것 (default 호환)
    # tone_stress2 = 2차 강세 (ˌ) — v3.17 추가
    'panjeom':   {
        'high': '〮', 'rising': '〯', 'length': 'ː',
        'tone_H': '〮', 'tone_R': '〯', 'tone_D': '〯〮',
        'tone_F': '〮〯', 'tone_L': '', 'tone_stress': '〮', 'tone_stress2': '〮',
    },
    'ipa':       {
        'high': 'ˈ',  'rising': 'ˇ',  'length': 'ː',
        'tone_H': '˥', 'tone_R': '˧˥', 'tone_D': '˨˩˦',
        'tone_F': '˥˩', 'tone_L': '˩', 'tone_stress': 'ˈ', 'tone_stress2': 'ˌ',
    },
    'middledot': {
        'high': '·',  'rising': '··', 'length': 'ː',
        'tone_H': '·', 'tone_R': '··', 'tone_D': '··',
        'tone_F': '·', 'tone_L': '', 'tone_stress': '·', 'tone_stress2': '˗',
    },
    'ascii':     {
        'high': "'",  'rising': '^',  'length': ':',
        'tone_H': "'", 'tone_R': '^', 'tone_D': '^^',
        'tone_F': "'", 'tone_L': '_', 'tone_stress': "'", 'tone_stress2': ',',
    },
    'arrow':     {
        'high': '¯',  'rising': '↗',  'length': 'ː',
        'tone_H': '¯', 'tone_R': '↗', 'tone_D': '↘↗',
        'tone_F': '↘', 'tone_L': '↓', 'tone_stress': '·', 'tone_stress2': '˗',
    },
    'numeric':   {
        'high': '¹',  'rising': '²',  'length': 'ː',
        'tone_H': '¹', 'tone_R': '²', 'tone_D': '³',
        'tone_F': '⁴', 'tone_L': '₁', 'tone_stress': '·', 'tone_stress2': '˗',
    },
}
# 모듈 변수 (런타임 변경 가능)
_DEFAULT_TONE_STYLE = 'middledot'
PANJEOM_HIGH = TONE_STYLES[_DEFAULT_TONE_STYLE]['high']
PANJEOM_RISING = TONE_STYLES[_DEFAULT_TONE_STYLE]['rising']
LENGTH_MARK = TONE_STYLES[_DEFAULT_TONE_STYLE]['length']
HALF_LENGTH = 'ˑ'

# Stress/tone marker 종류
_STRESS_PRIMARY = {'ˈ'}                    # 강세 → 거성 〮
_STRESS_SECONDARY = {'ˌ'}                  # 부강세 → 무시 또는 별도
_TONE_HIGH = {'˥', '˦'}                    # 고성조 → H category
_TONE_MID = {'˧'}                          # 중성조 → M (생략)
_TONE_LOW = {'˨', '˩'}                     # 저성조 → L category
_LENGTH_MARKERS = {'ː', 'ˑ'}

# 옛한글 모음 (강세는 모음에만 attach)
_TOKENIZE_OLD_VOWELS = {'ㆎ', 'ㆍ', 'ㅙ'}

# Mandarin 톤 (1-5 디지트) → tone category
# v3.1: 4성을 별개 카테고리로 분리 (이전: 1=4=H, 2=3=R로 머지)
_MANDARIN_TONE_CAT = {
    '1': 'H',  # 1성 高平
    '2': 'R',  # 2성 上昇
    '3': 'D',  # 3성 低降昇 (dipping)
    '4': 'F',  # 4성 去聲 (falling)
    '5': '',   # 5성 輕聲 (neutral, no mark)
}

# IPA vowel 위 톤 diacritic (combining marks) → tone category
_TONE_DIACRITIC_CAT = {
    '́': 'H',       # ́ acute = high (Vietnamese sắc)
    '̀': 'L',       # ̀ grave = low (Vietnamese huyền)
    '̄': '',        # ̄ macron = mid (no mark)
    '̌': 'R',       # ̌ caron = rising
    '̂': 'F',       # ̂ circumflex = falling
    '̋': 'H',       # ̋ double acute = extra high
    '̏': 'L',       # ̏ double grave = extra low
    '̉': 'D',       # ̉ hook above (Vietnamese hỏi = dipping)
    # Note: ̃ tilde stays as nasal vowel marker (IPA convention), not tone.
    '̣': 'F',       # ̣ dot below (Vietnamese nặng = heavy/falling)
}

# IPA tone bar combinations → category
# (긴 패턴부터 검사 — 더 구체적인 매칭 우선)
_TONE_BAR_PATTERNS = [
    ('˨˩˦', 'D'),      # Mandarin tone 3 (low-dipping)
    ('˧˥', 'R'),       # rising
    ('˥˩', 'F'),       # falling
    ('˨˦', 'R'),       # rising variant
    ('˧˨', 'F'),       # falling variant
    ('˥', 'H'),        # high level
    ('˦', 'H'),        # high
    ('˧', ''),         # mid (no mark)
    ('˨', 'L'),        # low
    ('˩', 'L'),        # extra low
]


def _resolve_tone_mark(category):
    """Resolve abstract tone category to current tone_style 's mark."""
    if not category:
        return ''
    style = TONE_STYLES.get(_DEFAULT_TONE_STYLE, TONE_STYLES['middledot'])
    return style.get(f'tone_{category}', '')


def _tokenize_ipa(ipa, precise=False):
    """IPA 문자열 → token 리스트.
    precise=True면 stress/length/tone을 SUPRA 토큰으로 보존.
    """
    out = []
    pending_stress = None  # 다음 모음 음절에 부착될 stress mark
    i = 0
    n = len(ipa)
    while i < n:
        ch = ipa[i]
        nxt = ipa[i+1] if i+1 < n else ''
        nxt2 = ipa[i+2] if i+2 < n else ''

        # Combining tilde → 비음 모음
        if nxt == '̃':
            if ch in _NASAL_MAP:
                tok = ('V_NASAL', _NASAL_MAP[ch])
                if precise and pending_stress:
                    tok = ('V_NASAL_STRESS', _NASAL_MAP[ch], pending_stress)
                    pending_stress = None
                out.append(tok)
                i += 2
                continue

        # Stress markers (precise만)
        if ch in _STRESS_PRIMARY:
            if precise:
                pending_stress = PANJEOM_HIGH
            i += 1; continue
        if ch in _STRESS_SECONDARY:
            # v3.17: 2차 강세 표시 — primary와 마찬가지로 다음 모음에 attach
            if precise:
                style = TONE_STYLES.get(_DEFAULT_TONE_STYLE, TONE_STYLES['middledot'])
                pending_stress = style.get('tone_stress2', '')
            i += 1; continue

        # Tone bars (multi-char patterns first — D/F before H/L)
        # v3.1: 5-category tone resolution
        matched_bar = None
        for pat, cat in _TONE_BAR_PATTERNS:
            if ipa[i:i+len(pat)] == pat:
                matched_bar = (pat, cat)
                break
        if matched_bar:
            pat, cat = matched_bar
            if precise:
                mark = _resolve_tone_mark(cat)
                if mark:
                    out.append(('SUPRA', mark))
            i += len(pat); continue

        # Length markers
        if ch in _LENGTH_MARKERS:
            if precise:
                out.append(('SUPRA', LENGTH_MARK))
            i += 1; continue

        # Mandarin tone digit (1-5)
        if ch.isdigit() and ch in _MANDARIN_TONE_CAT:
            if precise:
                cat = _MANDARIN_TONE_CAT[ch]
                mark = _resolve_tone_mark(cat)
                if mark:
                    out.append(('SUPRA', mark))
            i += 1; continue

        # Tone combining diacritics on vowel
        if nxt in _TONE_DIACRITIC_CAT:
            # Process base char first, then mark
            if ch in _IPA_PHONEMES:
                tok = _IPA_PHONEMES[ch]
                if precise and pending_stress:
                    tok = (tok[0] + '_STRESS', tok[1], pending_stress)
                    pending_stress = None
                out.append(tok)
            if precise:
                cat = _TONE_DIACRITIC_CAT[nxt]
                mark = _resolve_tone_mark(cat)
                if mark:
                    out.append(('SUPRA', mark))
            i += 2; continue

        # Standard mapping
        if ch in _IPA_PHONEMES:
            tok = _IPA_PHONEMES[ch]
            # 강세는 모음에만 attach (자음 OLD 제외)
            if precise and pending_stress:
                is_vowel = (tok[0] in ('V', 'V_NASAL', 'V_R')
                            or (tok[0] == 'OLD' and tok[1] in _TOKENIZE_OLD_VOWELS))
                if is_vowel:
                    tok = (tok[0] + '_STRESS', tok[1], pending_stress)
                    pending_stress = None
            out.append(tok)
        elif ch == ' ':
            out.append(('SPACE', ' '))
            pending_stress = None
        elif unicodedata.category(ch).startswith('P'):
            out.append(('PUNCT', ch))
        i += 1
    return out


_OLD_VOWELS = {'ㆎ', 'ㆍ', 'ㅙ'}  # OLD kind 중 모음들


def _is_vowel_token(tok):
    """V / V_NASAL / V_R / OLD-vowel (STRESS 변형 포함)."""
    if not tok: return False
    k, v = tok[0], tok[1] if len(tok) > 1 else ''
    if k in ('V', 'V_NASAL', 'V_R',
             'V_STRESS', 'V_NASAL_STRESS', 'V_R_STRESS'): return True
    if k.startswith('OLD') and v in _OLD_VOWELS: return True
    return False


def _strip_stress(tok):
    """V_X_STRESS → (V_X, val, mark) 분리."""
    if not tok: return tok, None
    k = tok[0]
    if k.endswith('_STRESS'):
        base = k[:-7]
        mark = tok[2] if len(tok) > 2 else PANJEOM_HIGH
        return (base, tok[1]), mark
    return tok, None


def _is_old_consonant(tok):
    return tok and tok[0] == 'OLD' and tok[1] not in _OLD_VOWELS


def _expand_stress_tokens(tokens):
    """V_X_STRESS → V_X + ('SUPRA', PANJEOM_HIGH) 분리.
    Stress 마크를 음절 뒤에 후속 토큰으로 변환.
    """
    out = []
    for t in tokens:
        if t[0].endswith('_STRESS'):
            base_kind = t[0][:-7]
            out.append((base_kind, t[1]))
            mark = t[2] if len(t) > 2 else PANJEOM_HIGH
            out.append(('SUPRA', mark))
        else:
            out.append(t)
    return out


def _assemble(tokens, precise=True):
    """Token list → Hangul syllable string.
    precise=True: 옛한글 (ㆄ/ㅸ/ㅿ/ㆅ/ᄾ/ᄶ/ᄛ/ㅼ/ㅽ/ㅥ/ㅱ/ㆎ/ㆍ) 완전 사용.
    precise=False: 모두 modern Korean 자모로 대체.
    SUPRA 토큰 (방점/장음): 직전 음절 뒤에 부착.
    """
    tokens = _expand_stress_tokens(tokens)
    # 옛한글 → 기본 한글 fallback (precise=False 모드)
    OLD_TO_BASIC = {
        'ㆄ':'ㅍ', 'ㅸ':'ㅂ', 'ㅿ':'ㅈ', 'ㆁ':'ㅇ', 'ㆆ':'ㅎ',
        'ㆅ':'ㅎ', 'ᄾ':'ㅅ', 'ᄶ':'ㅈ', 'ᄛ':'ㄹ',
        'ㅼ':'ㅅ', 'ㅽ':'ㄷ', 'ㅥ':'ㄴ', 'ㅱ':'ㅁ',
        'ㆎ':'ㅗ', 'ㆍ':'ㅏ', 'ㅙ':'ㅚ',
    }

    def _maybe_basic(j):
        return OLD_TO_BASIC.get(j, j) if not precise else j

    syllables = []
    i = 0
    n = len(tokens)
    while i < n:
        kind, val = tokens[i]
        nxt = tokens[i+1] if i+1 < n else None

        if kind == 'SPACE':
            syllables.append(' '); i += 1; continue
        if kind == 'PUNCT':
            syllables.append(val); i += 1; continue
        # SUPRA: 방점/장음 — 직전 음절 뒤에 부착
        if kind == 'SUPRA':
            syllables.append(val); i += 1; continue

        # SV_MARKER (j/w) — 앞 자음 또는 ㅇ과 결합
        if kind == 'SV_MARKER':
            if nxt and _is_vowel_token(nxt):
                vowel = _maybe_basic(nxt[1])
                if val == 'y':
                    new_v = _Y_VOWEL.get(vowel, vowel)
                else:
                    new_v = _W_VOWEL.get(vowel, vowel)
                syllables.append(_compose('ㅇ', new_v))
                # nasal 모음 → ㆁ jong (옛한글) 또는 ㅇ jong
                if nxt[0] == 'V_NASAL':
                    nasal_jong = 'ㆁ' if precise else 'ㅇ'
                    syllables[-1] = _compose_with_jong(syllables[-1], nasal_jong)
                i += 2; continue
            syllables.append(_compose('ㅇ', 'ㅡ'))
            i += 1; continue

        # OLD jamo as 자음 (ㆄ ㅸ ㅿ ㆅ ᄾ ᄶ ᄛ ㅼ ㅽ ㅥ ㅱ) — 옛한글 자음
        if kind == 'OLD' and val in OLD_TO_BASIC and OLD_TO_BASIC[val] in INITIALS:
            jamo = _maybe_basic(val)
            # precise=True: 옛한글 + ㅇ-syll로 분리 표기 (ML 분석 가능)
            # precise=False: 기본 자음으로 합성 (대중적)
            if nxt and _is_vowel_token(nxt):
                target_v = _maybe_basic(nxt[1])
                if precise:
                    # 옛한글 + 모음 분리
                    syllables.append(val)
                    # OLD vowels (ㆍ, ㆎ)는 _compose가 literal 'ㅇㆎ' 반환 → 깔끔히 단독 출력
                    if target_v in _OLD_VOWELS and target_v not in VOWELS:
                        syllables.append(target_v)
                        # nasal 모음 일 때 ㆁ 추가 (받침 못 붙이니 단독)
                        if nxt[0] == 'V_NASAL':
                            syllables.append('ㆁ')
                    else:
                        syll = _compose('ㅇ', target_v)
                        if nxt[0] == 'V_NASAL':
                            syll = _compose_with_jong(syll, 'ㆁ') or syll
                        syllables.append(syll)
                else:
                    syll = _compose(jamo, target_v)
                    if nxt[0] == 'V_NASAL':
                        syll = _compose_with_jong(syll, 'ㅇ')
                    syllables.append(syll)
                i += 2; continue
            # 어말/자음 앞 — 단독 표시 또는 받침
            if precise:
                syllables.append(val)
            else:
                # OLD 자음 (마찰음 ㆄ/ㅸ/ㅿ/ㆅ/ᄾ/ᄶ/ㅼ/ㅽ + ᄛ + ㅥ/ㅱ) → 받침 회피
                # NIKL 컨벤션: 어말 마찰음/외래자음 → ㅡ-syll (예: Bach → 바흐, jazz → 재즈)
                # 단, 비음(ㅥ→ㄴ, ㅱ→ㅁ)는 받침 가능
                avoid_jong = val not in ('ㅥ', 'ㅱ')
                if (not avoid_jong and jamo in FINALS and syllables
                        and len(syllables[-1]) == 1):
                    syllables[-1] = _compose_with_jong(syllables[-1], jamo) or syllables[-1]
                else:
                    syllables.append(_compose(jamo, 'ㅡ'))
            i += 1; continue

        # OLD vowel (ㆎ ㆍ ㅙ) — 옛한글/특수 모음
        if kind == 'OLD' and val not in OLD_TO_BASIC:  # shouldn't happen
            syllables.append(val); i += 1; continue
        if kind == 'OLD':  # OLD 모음 (ㆎ ㆍ ㅙ)
            jung = _maybe_basic(val)
            if jung in VOWELS:
                syllables.append(_compose('ㅇ', jung))
            else:
                # ㆎ, ㆍ는 standard VOWELS 밖 → 단독 표시 (clean)
                syllables.append(jung)
            i += 1; continue

        # V (모음 단독)
        if kind == 'V':
            syllables.append(_compose('ㅇ', val))
            i += 1; continue

        # V_NASAL (비음 모음, French)
        if kind == 'V_NASAL':
            jung = _maybe_basic(val)
            nasal_jong = 'ㆁ' if precise else 'ㅇ'
            syll = _compose('ㅇ', jung)
            attached = _compose_with_jong(syll, nasal_jong)
            if attached:
                syllables.append(attached)
            else:
                # OLD vowel (ㆍ ㆎ) → 단독 + ㆁ 분리 (한글 완성형 한계)
                # 'ㅇㆍ' literal 출력 시 ㅇ 제거 후 ㆍ + ㆁ
                if jung in _OLD_VOWELS and jung not in VOWELS:
                    syllables.append(jung)
                    syllables.append(nasal_jong)
                else:
                    syllables.append(syll)
            i += 1; continue

        # V_R (r-colored vowel: butter, fur)
        if kind == 'V_R':
            jung = _maybe_basic(val)
            syll = _compose('ㅇ', jung)
            attached = _compose_with_jong(syll, 'ㄹ')
            syllables.append(attached if attached else syll)
            i += 1; continue

        # C_PALATAL_N (ɲ palatal n — palatalize next vowel)
        if kind == 'C_PALATAL_N':
            jamo = val if precise else 'ㄴ'
            if nxt and _is_vowel_token(nxt):
                v = _maybe_basic(nxt[1])
                pv = _Y_VOWEL.get(v, v)
                if precise:
                    syllables.append(jamo)
                    syll = _compose('ㅇ', pv)
                else:
                    syll = _compose('ㄴ', pv)
                if nxt[0] == 'V_NASAL':
                    syll = _compose_with_jong(syll, 'ㆁ' if precise else 'ㅇ') or syll
                syllables.append(syll)
                i += 2; continue
            # 어말 — 단독 표시
            if precise:
                syllables.append(jamo)
            else:
                syllables.append(_compose('ㄴ', 'ㅣ'))
            i += 1; continue

        # C (자음)
        if kind == 'C':
            cho = val
            # SV_MARKER + V 다음
            if nxt and nxt[0] == 'SV_MARKER' and i+2 < n and _is_vowel_token(tokens[i+2]):
                sv_kind = nxt[1]
                v = _maybe_basic(tokens[i+2][1])
                if sv_kind == 'y':
                    new_v = _Y_VOWEL.get(v, v)
                else:
                    new_v = _W_VOWEL.get(v, v)
                if cho in INITIALS:
                    syll = _compose(cho, new_v)
                else:
                    syll = cho + _compose('ㅇ', new_v)
                if tokens[i+2][0] == 'V_NASAL':
                    nasal_jong = 'ㆁ' if precise else 'ㅇ'
                    syll = _compose_with_jong(syll, nasal_jong) or syll
                syllables.append(syll)
                i += 3; continue
            # C + V/OLD/V_NASAL
            if nxt and _is_vowel_token(nxt):
                target_v = _maybe_basic(nxt[1])
                if cho in INITIALS:
                    syll = _compose(cho, target_v)
                else:
                    syll = cho + _compose('ㅇ', target_v)
                if nxt[0] == 'V_NASAL':
                    nasal_jong = 'ㆁ' if precise else 'ㅇ'
                    attached = _compose_with_jong(syll, nasal_jong)
                    if attached:
                        syll = attached
                    else:
                        # OLD vowel (ㆍ ㆎ) syll에 받침 못 붙임 → ㆁ 분리 추가
                        if target_v in _OLD_VOWELS and target_v not in VOWELS:
                            syllables.append(syll)
                            syllables.append(nasal_jong)
                            i += 2; continue
                syllables.append(syll)
                i += 2; continue
            # 자음 단독: 받침 시도 또는 으-syll
            # ㆁ (옛이응 /ŋ/) → 받침-ㅇ로 대체해서 흡수 시도
            jong_cand = 'ㅇ' if cho == 'ㆁ' else cho
            # NIKL 컨벤션: 어말 마찰음(s/z/f/v/x계열) → ㅡ-syll (받침 X)
            # 마찰음 표시는 OLD 자음들(ㆄ/ㅸ/ㅿ/ㆅ/ᄾ/ᄶ/ㅼ/ㅽ) — 받침 회피
            avoid_jong = cho in ('ㆄ','ㅸ','ㅿ','ㆅ','ᄾ','ᄶ','ㅼ','ㅽ')
            if (not avoid_jong and syllables and len(syllables[-1]) == 1
                    and jong_cand in FINALS):
                attached = _compose_with_jong(syllables[-1], jong_cand)
                if attached:
                    syllables[-1] = attached
                    i += 1; continue
            # 으-syll
            if cho in INITIALS:
                syllables.append(_compose(cho, 'ㅡ'))
            else:
                # OLD 자음 — 단독 + ㅡ-syll로 자모 보존
                if cho in OLD_TO_BASIC and OLD_TO_BASIC[cho] in INITIALS:
                    if precise:
                        syllables.append(cho)
                        syllables.append(_compose('ㅇ', 'ㅡ'))
                    else:
                        syllables.append(_compose(OLD_TO_BASIC[cho], 'ㅡ'))
                else:
                    syllables.append(cho)
            i += 1; continue
        i += 1
    return ''.join(syllables)


def _compose_with_jong(syll, jong):
    """기존 음절에 받침 추가. jong이 빈 자리이면 부착, 아니면 None 반환.

    옛한글 ㆁ은 표준 한글 완성형에서 받침 자리에 못 들어가므로 ㅇ으로 매핑하여 결합.
    NFC 정규화 후에도 ㆁ과 ㅇ받침은 시각적으로 동일.
    """
    if not syll or len(syll) != 1:
        return None
    code = ord(syll)
    if not (0xAC00 <= code <= 0xD7A3):
        return None
    base = code - HANGUL_BASE
    cho_idx = base // 588
    jung_idx = (base % 588) // 28
    jong_idx = base % 28
    if jong_idx != 0:
        return None  # 이미 받침 있음
    # ㆁ → ㅇ for actual composition (표준 한글 받침 자리)
    if jong == 'ㆁ':
        jong = 'ㅇ'
    if jong not in FINALS:
        return None
    return chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index(jong))


# ISO 639-1 / 639-3 → epitran code
# 모든 매핑은 검증됨 (99 base codes, 모두 epitran.Epitran() 로드 가능)
_ISO_TO_EPITRAN = {
    # === English (ML routing only — hardcoded path uses CMU dict) ===
    'en': 'eng-Latn',
    # === Romance ===
    'es': 'spa-Latn', 'fr': 'fra-Latn', 'it': 'ita-Latn', 'pt': 'por-Latn',
    'ca': 'cat-Latn', 'gl': 'glg-Latn', 'oc': 'oci-Latn', 'ro': 'ron-Latn',
    'sc': 'sro-Latn', 'co': 'oci-Latn',
    # === Germanic ===
    'de': 'deu-Latn', 'nl': 'nld-Latn', 'af': 'afr-Latn', 'fy': 'fry-Latn',
    'sv': 'swe-Latn', 'no': 'nno-Latn', 'nn': 'nno-Latn',
    # === Slavic ===
    'pl': 'pol-Latn', 'cs': 'ces-Latn', 'csb': 'csb-Latn',
    'hr': 'hrv-Latn', 'sl': 'slv-Latn',
    'sr': 'srp-Cyrl', 'srl': 'srp-Latn',
    'ru': 'rus-Cyrl', 'uk': 'ukr-Cyrl',
    # Linguistic-neighbor fallbacks (epitran 미지원 → 가까운 언어 라우팅)
    # v3.2: 정확도 손실 가능성 있지만 음역 가능하게 만듦
    'sk': 'ces-Latn',   # Slovak → Czech (gradient mutually intelligible)
    'bs': 'hrv-Latn',   # Bosnian → Croatian (사실상 동일 음운)
    'me': 'srp-Cyrl',   # Montenegrin → Serbian
    'mk': 'srp-Cyrl',   # Macedonian → Serbian (related Cyrillic)
    'be': 'rus-Cyrl',   # Belarusian → Russian (가까움)
    'bg': 'rus-Cyrl',   # Bulgarian → Russian (Cyrillic, 음운 다름 — 불완전 fallback)
    # === Baltic ===
    'lt': 'lit-Latn', 'lv': 'lav-Latn',
    # === Finno-Ugric ===
    'fi': 'fin-Latn', 'et': 'est-Latn', 'hu': 'hun-Latn',
    # === Celtic ===
    'ga': 'gle-Latn', 'cy': 'cym-Latn',
    # === Other Eu === (he/hy/is/eu/sk/bg/uk-be 일부는 epitran 미지원)
    'sq': 'sqi-Latn', 'mt': 'mlt-Latn', 'eo': 'epo-Latn',
    'tok': 'tok-Latn',  # 토키포나
    'ile': 'ile-Latn',  # 인테르링귀
    # === Turkic ===
    'tr': 'tur-Latn', 'az': 'aze-Latn', 'azb': 'aze-Cyrl',
    'kk': 'kaz-Cyrl', 'kkl': 'kaz-Latn',
    'ky': 'kir-Cyrl', 'kyl': 'kir-Latn', 'kya': 'kir-Arab',
    'tk': 'tuk-Latn', 'uzn': 'uzb-Latn', 'uz': 'uzb-Latn', 'uzc': 'uzb-Cyrl',
    'kmr': 'kmr-Latn',  # 쿠르드 북부
    'ug': 'uig-Arab',
    # === Iranian ===
    'fa': 'fas-Arab', 'ps': 'pbu-Arab', 'tg': 'tgk-Cyrl',
    'ckb': 'ckb-Arab',  # 쿠르드 중부 (소라니)
    # === Indic ===
    'hi': 'hin-Deva', 'bho': 'bho-Deva', 'mr': 'mar-Deva',
    'bn': 'ben-Beng', 'pa': 'pan-Guru', 'or': 'ori-Orya',
    'ta': 'tam-Taml', 'te': 'tel-Telu',
    'kn': 'kan-Knda', 'ml': 'mal-Mlym',
    'si': 'sin-Sinh', 'ur': 'urd-Arab',
    # === Semitic ===
    'ar': 'ara-Arab', 'am': 'amh-Ethi', 'ti': 'tir-Ethi',
    'syr': 'aii-Syrc',  # 시리아어
    # === Caucasian ===
    'ka': 'kat-Geor', 'av': 'ava-Cyrl', 'lez': 'lez-Cyrl',
    'kbd': 'kbd-Cyrl',  # 카바르드 (서북캅카스)
    # === Southeast Asian ===
    'vi': 'vie-Latn', 'th': 'tha-Thai', 'lo': 'lao-Laoo',
    'km': 'khm-Khmr', 'my': 'mya-Mymr',
    'id': 'ind-Latn', 'ms': 'msa-Latn',
    'jv': 'jav-Latn', 'fil': 'tgl-Latn', 'tl': 'tgl-Latn',
    'ceb': 'ceb-Latn', 'ilo': 'ilo-Latn',
    'tpi': 'tpi-Latn',  # 톡 피신 (파푸아)
    # === East Asian ===
    'ja': 'jpn-Hira',   # 일본어 (히라가나) — but Hunmin uses dedicated transcribe_ja
    'ko': 'kor-Hang',   # 한국어 — but no-op
    'zh': 'cmn-Latn',   # 중국어 (피닌 입력)
    'yue': 'yue-Latn',  # 광둥어
    'nan': 'nan-Latn',  # 민난어
    'wuu': 'wuu-Latn',  # 우어 (상하이)
    'hak': 'hak-Latn',  # 객가
    'cjy': 'cjy-Latn',  # 진어
    'hsn': 'hsn-Latn',  # 상어
    'gan': 'gan-Latn',  # 감어
    # === African ===
    'sw': 'swa-Latn', 'lg': 'lug-Latn', 'rw': 'kin-Latn', 'rn': 'run-Latn',
    'ny': 'nya-Latn', 'sn': 'sna-Latn', 'so': 'som-Latn',
    'zu': 'zul-Latn', 'xh': 'xho-Latn', 'tn': 'tsn-Latn',
    'yo': 'yor-Latn',
    'ha': 'hau-Latn', 'om': 'orm-Latn', 'sg': 'sag-Latn',
    'ff': 'ful-Latn', 'kab': 'kab-Latn',
    'aar': 'aar-Latn', 'aa': 'aar-Latn',
    # === Pacific ===
    'mi': 'mri-Latn',  # 마오리
    'mri': 'mri-Latn',
    # === Native American ===
    'qu': 'quy-Latn',
    'nhi': 'nhi-Latn',  # 나와틀
    'ht': 'hat-Latn-bab',  # 아이티어
    'jam': 'jam-Latn',  # 자메이카 크리올
    # === Mongolic ===
    'mn': 'mon-Cyrl-bab',  # 몽골 (할하)
    'mon': 'mon-Cyrl-bab',
    'khk': 'mon-Cyrl-bab',
    # === Other ===
    'cmn': 'cmn-Latn',  # 표준 중국어 (alias)
    'epo': 'epo-Latn',  # 에스페란토 (alias)
    'lat': 'ltc-Latn-bax',  # 라틴
    'la': 'ltc-Latn-bax',
    'got': 'got-Latn',  # 고트어
    # Generic fallback
    'generic': 'generic-Latn',
}


def _set_tone_style(tone_style):
    """Update module-level tone style variables.
    _DEFAULT_TONE_STYLE 를 갱신해야 _resolve_tone_mark 가 올바른 카테고리 매핑 사용."""
    global PANJEOM_HIGH, PANJEOM_RISING, LENGTH_MARK, _DEFAULT_TONE_STYLE
    style = TONE_STYLES.get(tone_style, TONE_STYLES['middledot'])
    _DEFAULT_TONE_STYLE = tone_style if tone_style in TONE_STYLES else 'middledot'
    PANJEOM_HIGH = style['high']
    PANJEOM_RISING = style['rising']
    LENGTH_MARK = style['length']


def transcribe_universal(text, lang_iso, mode='hangul', precise=True, uhps=None,
                         tone_style='middledot', safe_fonts=True,
                         return_tokens=False):
    """Universal IPA-based transcribe.

    Args:
      text: input text. lang='ipa'면 IPA 문자열 직접 입력.
      lang_iso: ISO 639-1/639-3 코드 또는 'ipa'.
      mode: 'hangul' / 'jamo' / 'spaced'.
      precise: True → UHPS-core (옛한글 자음/모음 1:1), False → 기본 한글.
      uhps: 'basic' / 'core' / 'full' (None: precise로부터 추론).
      tone_style: UHPS-full 모드에서 운율 표기 스타일.
        'middledot' (default) — · ·· ː (한글 친화, 모든 폰트 호환)
        'panjeom' — 〮 〯 ː (옛 훈민정음 정통, 옛한글 폰트 필요)
        'ipa'     — ˈ ˇ ː (IPA식)
        'ascii'   — ' ^ : (가장 안전)
      safe_fonts: True (default) → 결합블록 jamo (ᄾᄶᄛ) 를 modern 자모로 fallback.
                  False → 결합블록 그대로 (UHPS 정밀, 일부 폰트 미지원).
      return_tokens: True면 추상 토큰 시퀀스 [(KIND, value, ...), ...] 반환 (ML 학습용).
                     이때 mode/safe_fonts는 무시된다 (토큰은 표면 표기 이전 layer).
    """
    if uhps is None:
        uhps = 'core' if precise else 'basic'
    precise_inner = uhps in ('core', 'full')
    # 모듈 글로벌 mark + style id 갱신 (tokenizer/assembler 모두 사용)
    _set_tone_style(tone_style)

    def _safe_fallback(s):
        if not safe_fonts: return s
        for bad, good in _FONT_SAFE_FALLBACK.items():
            s = s.replace(bad, good)
        return s

    if lang_iso == 'ipa':
        ipa_norm = _normalize_ipa(text, uhps=uhps)
        tokens = _tokenize_ipa(ipa_norm, precise=(uhps == 'full'))
        if return_tokens:
            return _expand_stress_tokens(tokens) if uhps == 'full' else tokens
        return _safe_fallback(_assemble(tokens, precise=precise_inner))

    try:
        import epitran
    except ImportError:
        raise ImportError(
            "Universal mode requires epitran: pip install hunmin[universal]\n"
            "Or use lang='ipa' to provide IPA directly (no dependency).")

    epi_code = _ISO_TO_EPITRAN.get(lang_iso, lang_iso)
    # Cache Epitran instances — initialization is ~0.8s per language
    if not hasattr(transcribe_universal, '_epi_cache'):
        transcribe_universal._epi_cache = {}
    cache = transcribe_universal._epi_cache
    if epi_code not in cache:
        try:
            cache[epi_code] = epitran.Epitran(epi_code)
        except Exception as e:
            cache[epi_code] = None
            raise ValueError(
                f"Unsupported language {lang_iso!r} (epitran code {epi_code!r}). "
                f"Try lang='ipa' to provide IPA directly: {e}")
    epi = cache[epi_code]
    if epi is None:
        raise ValueError(f"Unsupported language {lang_iso!r}")

    ipa = epi.transliterate(text)
    if not ipa:
        return [] if return_tokens else text

    ipa_norm = _normalize_ipa(ipa, uhps=uhps)
    tokens = _tokenize_ipa(ipa_norm, precise=(uhps == 'full'))
    if return_tokens:
        return _expand_stress_tokens(tokens) if uhps == 'full' else tokens
    return _safe_fallback(_assemble(tokens, precise=precise_inner))


def supported_universal_languages():
    """Return list of supported ISO codes via universal mode."""
    return sorted(_ISO_TO_EPITRAN.keys())
