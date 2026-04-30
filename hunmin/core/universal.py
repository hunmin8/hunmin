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


# === IPA phoneme → UHPS jamo (precise mode = Old Hangul 사용) ===
# 표는 IPA → (kind, jamo) — kind는 'C' (자음), 'V' (모음), 'SV' (반모음)
_IPA_PHONEMES = {
    # Plosives (stops) — 어두에서 ㅋ/ㅌ/ㅍ (aspirated default for foreign)
    'p': ('C', 'ㅍ'), 'b': ('C', 'ㅂ'),
    't': ('C', 'ㅌ'), 'd': ('C', 'ㄷ'),
    'k': ('C', 'ㅋ'), 'ɡ': ('C', 'ㄱ'), 'g': ('C', 'ㄱ'),
    'q': ('C', 'ㅋ'),  # uvular k
    'ʔ': ('C', 'ㆆ'),  # glottal stop (Old Hangul)
    # Nasals
    'm': ('C', 'ㅁ'), 'n': ('C', 'ㄴ'),
    'ɲ': ('C', 'ㄴ'),  # palatal n (will be palatalized)
    'ŋ': ('C', 'ㆁ'),  # eng (Old Hangul) — basic 모드는 ㅇ jong
    # Fricatives
    'f': ('OLD', 'ㆄ'),  # /f/ — UHPS ㆄ
    'v': ('OLD', 'ㅸ'),  # /v/ — UHPS ㅸ
    's': ('C', 'ㅅ'), 'z': ('OLD', 'ㅿ'),  # /z/ — ㅿ
    'ʃ': ('C', 'ㅅ'),  # /ʃ/ → 시 (palatal context)
    'ʒ': ('C', 'ㅈ'),
    'h': ('C', 'ㅎ'), 'ɦ': ('C', 'ㅎ'),
    'x': ('C', 'ㅎ'),  # German Bach
    'ç': ('C', 'ㅎ'),  # German ich
    'θ': ('C', 'ㅅ'), 'ð': ('C', 'ㄷ'),
    'ɣ': ('C', 'ㄱ'),  # voiced velar fricative
    'ɸ': ('OLD', 'ㆄ'),  # bilabial f
    'β': ('OLD', 'ㅸ'),  # bilabial v
    'ʁ': ('C', 'ㄹ'),  # French R
    'χ': ('C', 'ㅎ'),
    # Affricates (multi-char; handled separately too)
    # 't͡ʃ' → ㅊ, 'd͡ʒ' → ㅈ — preprocessed
    # Liquids / R
    'l': ('C', 'ㄹ'), 'ɭ': ('C', 'ㄹ'), 'ɮ': ('C', 'ㄹ'),
    'r': ('C', 'ㄹ'), 'ɾ': ('C', 'ㄹ'), 'ɹ': ('C', 'ㄹ'),
    'ʀ': ('C', 'ㄹ'), 'ɽ': ('C', 'ㄹ'),
    # Glides / approximants
    'j': ('SV_MARKER', 'y'),  # 다음 모음과 합쳐 palatal vowel
    'w': ('SV_MARKER', 'w'),  # 다음 모음과 합쳐 W vowel
    'ɥ': ('SV_MARKER', 'y'),  # French u-glide → y로 처리
    # Vowels
    'a': ('V', 'ㅏ'), 'ɑ': ('V', 'ㅏ'), 'ɐ': ('V', 'ㅏ'),
    'æ': ('V', 'ㅐ'), 'ɛ': ('V', 'ㅔ'), 'e': ('V', 'ㅔ'),
    'ə': ('V', 'ㅓ'), 'ʌ': ('V', 'ㅓ'),
    'ɜ': ('V', 'ㅓ'), 'ɞ': ('V', 'ㅓ'),
    'i': ('V', 'ㅣ'), 'ɪ': ('V', 'ㅣ'), 'ɨ': ('V', 'ㅡ'), 'ɯ': ('V', 'ㅡ'),
    'o': ('V', 'ㅗ'), 'ɔ': ('V', 'ㅗ'),
    'u': ('V', 'ㅜ'), 'ʊ': ('V', 'ㅜ'),
    'y': ('V', 'ㅟ'), 'ø': ('V', 'ㅚ'), 'œ': ('V', 'ㅚ'),
    'ɵ': ('V', 'ㅓ'), 'ɤ': ('V', 'ㅓ'),
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


def _assemble(tokens, precise=True):
    """Token list → Hangul syllable string.
    precise=True: 옛한글 (ㆄ/ㅸ/ㅿ) 사용, False: ㅍ/ㅂ/ㅈ 으로 대체.
    """
    OLD_TO_BASIC = {'ㆄ':'ㅍ', 'ㅸ':'ㅂ', 'ㅿ':'ㅈ', 'ㆁ':'ㅇ', 'ㆆ':'ㅎ'}
    syllables = []
    i = 0
    n = len(tokens)
    while i < n:
        kind, val = tokens[i]
        nxt = tokens[i+1] if i+1 < n else None
        if kind == 'SPACE':
            syllables.append(' ')
            i += 1; continue
        if kind == 'PUNCT':
            syllables.append(val)
            i += 1; continue
        # SV_MARKER (j/w) + V → palatal/W vowel
        if kind == 'SV_MARKER':
            if nxt and nxt[0] == 'V':
                vowel = nxt[1]
                if val == 'y':
                    new_v = _Y_VOWEL.get(vowel, vowel)
                    # 자음 onset (앞에 free C 있으면 그것 위에)
                    if syllables and len(syllables[-1]) == 1:
                        last = syllables[-1]
                        # 자음 단독이면 합치기 (rare in this design)
                        pass
                    syllables.append(_compose('ㅇ', new_v))
                else:  # w
                    new_v = _W_VOWEL.get(vowel, vowel)
                    syllables.append(_compose('ㅇ', new_v))
                i += 2; continue
            # SV_MARKER alone: insert ㅇ + filler
            syllables.append(_compose('ㅇ', 'ㅡ'))
            i += 1; continue
        # OLD jamo (ㆄ ㅸ ㅿ ㆁ ㆆ)
        if kind == 'OLD':
            jamo = val if precise else OLD_TO_BASIC.get(val, val)
            if nxt and nxt[0] == 'V':
                if precise and jamo in ('ㆄ', 'ㅸ', 'ㅿ', 'ㆁ', 'ㆆ'):
                    # 옛한글은 모음과 결합 X, 단독으로 표시
                    syllables.append(jamo)
                    syllables.append(_compose('ㅇ', nxt[1]))
                    i += 2; continue
                else:
                    syllables.append(_compose(jamo, nxt[1]))
                    i += 2; continue
            else:
                syllables.append(jamo if precise else jamo)
                i += 1; continue
        # V (모음 단독) — 앞에 자음 있으면 합쳤어야 하는데 여기까지 왔으면 ㅇ-syll
        if kind == 'V':
            syllables.append(_compose('ㅇ', val))
            i += 1; continue
        # C (자음)
        if kind == 'C':
            cho = val
            # SV_MARKER (j/w) + V 가 다음이면 palatal/W vowel + 자음 onset
            if nxt and nxt[0] == 'SV_MARKER' and i+2 < n and tokens[i+2][0] == 'V':
                sv_kind = nxt[1]
                v = tokens[i+2][1]
                if sv_kind == 'y':
                    new_v = _Y_VOWEL.get(v, v)
                else:
                    new_v = _W_VOWEL.get(v, v)
                if cho in INITIALS:
                    syllables.append(_compose(cho, new_v))
                else:
                    syllables.append(cho + _compose('ㅇ', new_v))
                i += 3; continue
            # 다음이 V면 합치기
            if nxt and nxt[0] == 'V':
                syllables.append(_compose(cho, nxt[1]))
                i += 2; continue
            # 다음이 SPACE/PUNCT/end/자음 → 받침 또는 으-syll
            # 어말/자음 앞 자음
            ALLOW_FINAL = {'ㄴ','ㅁ','ㄹ','ㅇ','ㅂ','ㅅ','ㄱ','ㄷ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'}
            if syllables and len(syllables[-1]) == 1:
                last = syllables[-1]
                code = ord(last)
                if 0xAC00 <= code <= 0xD7A3:
                    base = code - HANGUL_BASE
                    cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
                    if jong_idx == 0 and cho in FINALS:
                        # 받침 추가
                        syllables[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + FINALS.index(cho))
                        i += 1; continue
            # 으-syll
            if cho in INITIALS:
                syllables.append(_compose(cho, 'ㅡ'))
            else:
                syllables.append(cho)
            i += 1; continue
        i += 1
    return ''.join(syllables)


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
