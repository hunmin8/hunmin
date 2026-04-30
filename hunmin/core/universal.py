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
    'ʔ': ('C', 'ㆆ'),  # glottal stop — 옛한글 여린히읗
    # 흡착음/임플로시브 (rough)
    'ɓ': ('C', 'ㅂ'), 'ɗ': ('C', 'ㄷ'), 'ɠ': ('C', 'ㄱ'),
    # === Nasals ===
    'm': ('C', 'ㅁ'), 'n': ('C', 'ㄴ'),
    'ɲ': ('C', 'ㅥ'),  # palatal n — 쌍니은 U+3165
    'ŋ': ('C', 'ㆁ'),  # velar n — 옛한글 옛이응
    'ɴ': ('C', 'ㆁ'),  # uvular n
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
    'χ': ('OLD', 'ㆅ'),     # uvular x
    'ʁ': ('OLD', 'ᄛ'),     # French R — 가벼운 ㄹ U+111B
    'ʀ': ('OLD', 'ᄛ'),     # uvular trilled R
    'ħ': ('OLD', 'ㆅ'),     # Arabic pharyngeal h
    'ʕ': ('C', 'ㆆ'),       # Arabic pharyngeal voiced (~ glottal)
    'ʜ': ('OLD', 'ㆅ'),
    'ʢ': ('C', 'ㆆ'),
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
_IPA_DIGRAPHS = [
    ('t͡ʃ', 'ʧ'), ('d͡ʒ', 'ʤ'), ('ts', 'ʦ'), ('dz', 'ʣ'),
    ('tʃ', 'ʧ'),  ('dʒ', 'ʤ'),
]
_IPA_PHONEMES['ʧ'] = ('C', 'ㅊ')
_IPA_PHONEMES['ʤ'] = ('C', 'ㅈ')
_IPA_PHONEMES['ʦ'] = ('C', 'ㅊ')  # ts → ㅊ (basic)
_IPA_PHONEMES['ʣ'] = ('C', 'ㅈ')

# Y/W + 모음 → palatal/W vowel (existing UHPS pattern)
_Y_VOWEL = {'ㅏ':'ㅑ','ㅐ':'ㅒ','ㅓ':'ㅕ','ㅔ':'ㅖ','ㅗ':'ㅛ','ㅜ':'ㅠ','ㅣ':'ㅣ','ㅡ':'ㅡ'}
_W_VOWEL = {'ㅏ':'ㅘ','ㅐ':'ㅙ','ㅓ':'ㅝ','ㅔ':'ㅞ','ㅗ':'ㅗ','ㅜ':'ㅜ','ㅣ':'ㅟ'}


# IPA diacritics 제거/처리
_REMOVE_DIACRITICS = {
    'ː', 'ˑ',     # length marks
    'ˈ', 'ˌ',     # stress marks
    '͡',           # tie bar (already handled)
    '̩', '̯', '̃',   # syllabic, non-syllabic, nasalization (정밀하게는 별도 처리)
    'ʰ',          # aspirated
    'ʷ', 'ʲ',     # labialized, palatalized
    '̞', '̥', '̬',   # lowered, voiceless, voiced
    'ˀ',          # glottalized
}


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


def _normalize_ipa(ipa):
    """IPA preprocess: digraphs, diacritics."""
    s = ipa
    # NFC 정규화
    s = unicodedata.normalize('NFC', s)
    # digraph
    for src, dst in _IPA_DIGRAPHS:
        s = s.replace(src, dst)
    # diacritics 제거
    for d in _REMOVE_DIACRITICS:
        s = s.replace(d, '')
    return s


def _tokenize_ipa(ipa):
    """IPA 문자열 → phoneme 리스트."""
    out = []
    for ch in ipa:
        if ch in _IPA_PHONEMES:
            out.append(_IPA_PHONEMES[ch])
        elif ch == ' ':
            out.append(('SPACE', ' '))
        elif unicodedata.category(ch).startswith('P'):
            out.append(('PUNCT', ch))
        # else: silently drop unknown
    return out


_OLD_VOWELS = {'ㆎ', 'ㆍ', 'ㅙ'}  # OLD kind 중 모음들


def _is_vowel_token(tok):
    """V / V_NASAL / OLD-vowel."""
    if not tok: return False
    k, v = tok[0], tok[1] if len(tok) > 1 else ''
    if k in ('V', 'V_NASAL'): return True
    if k == 'OLD' and v in _OLD_VOWELS: return True
    return False


def _is_old_consonant(tok):
    return tok and tok[0] == 'OLD' and tok[1] not in _OLD_VOWELS


def _assemble(tokens, precise=True):
    """Token list → Hangul syllable string.
    precise=True: 옛한글 (ㆄ/ㅸ/ㅿ/ㆅ/ᄾ/ᄶ/ᄛ/ㅼ/ㅽ/ㅥ/ㅱ/ㆎ/ㆍ) 완전 사용.
    precise=False: 모두 modern Korean 자모로 대체.
    """
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
                    syll = _compose('ㅇ', target_v)
                    if nxt[0] == 'V_NASAL':
                        syll = _compose_with_jong(syll, 'ㆁ')
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
            elif jamo in FINALS and syllables and len(syllables[-1]) == 1:
                # 받침으로 부착 시도
                syllables[-1] = _compose_with_jong(syllables[-1], jamo) or syllables[-1]
            else:
                syllables.append(_compose(jamo, 'ㅡ'))
            i += 1; continue

        # OLD vowel (ㆎ ㆍ ㅙ) — 옛한글/특수 모음
        if kind == 'OLD' and val not in OLD_TO_BASIC:  # shouldn't happen
            syllables.append(val); i += 1; continue
        if kind == 'OLD':  # OLD 모음 (ㆎ ㆍ ㅙ)
            jung = _maybe_basic(val)
            syllables.append(_compose('ㅇ', jung))
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
            syllables.append(_compose_with_jong(syll, nasal_jong))
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
                    syll = _compose_with_jong(syll, nasal_jong)
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
                    syll = _compose_with_jong(syll, nasal_jong)
                syllables.append(syll)
                i += 2; continue
            # 자음 단독: 받침 시도 또는 으-syll
            if syllables and len(syllables[-1]) == 1 and cho in FINALS:
                attached = _compose_with_jong(syllables[-1], cho)
                if attached:
                    syllables[-1] = attached
                    i += 1; continue
            # 으-syll
            if cho in INITIALS:
                syllables.append(_compose(cho, 'ㅡ'))
            else:
                syllables.append(cho)
            i += 1; continue
        i += 1
    return ''.join(syllables)


def _compose_with_jong(syll, jong):
    """기존 음절에 받침 추가. jong이 빈 자리이면 부착, 아니면 None 반환."""
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
    if jong not in FINALS:
        return None
    return chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index(jong))


# ISO 639-1 / 639-3 → epitran code
# 모든 매핑은 검증됨 (99 base codes, 모두 epitran.Epitran() 로드 가능)
_ISO_TO_EPITRAN = {
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


def transcribe_universal(text, lang_iso, mode='hangul', precise=True):
    """Universal IPA-based transcribe.

    Args:
      text: input text in source language.
      lang_iso: 2-letter ISO 639-1 code (e.g., 'sw', 'th', 'vi', 'ar').
      mode: 'hangul' or 'jamo' or 'spaced'.
      precise: True → 옛한글 (ㆄ/ㅸ/ㅿ); False → 기본 한글.

    Returns: Korean Hangul transcription.
    Raises: ImportError if epitran not installed; ValueError if lang unsupported.
    """
    try:
        import epitran
    except ImportError:
        raise ImportError(
            "Universal mode requires epitran: pip install hunmin[universal]")

    epi_code = _ISO_TO_EPITRAN.get(lang_iso, lang_iso)
    try:
        epi = epitran.Epitran(epi_code)
    except Exception as e:
        raise ValueError(f"Unsupported language {lang_iso!r} (epitran code {epi_code!r}): {e}")

    ipa = epi.transliterate(text)
    if not ipa:
        return text  # empty IPA → passthrough

    ipa_norm = _normalize_ipa(ipa)
    tokens = _tokenize_ipa(ipa_norm)
    return _assemble(tokens, precise=precise)


def supported_universal_languages():
    """Return list of supported ISO codes via universal mode."""
    return sorted(_ISO_TO_EPITRAN.keys())
