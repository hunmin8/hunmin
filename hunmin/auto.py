"""Hunmin auto-routing — Mixed-script encoding (v3.8).

모든 입력을 100% UHPS jamo 공간으로 인코딩:
1. 스크립트별 chunk 분리
2. chunk별 적절한 lang 라우팅
3. 숫자/기호 transliteration

설계 원칙: leak 0 — 입력 어떤 글자든 한글로 변환되어야 함.
"""
import re
import unicodedata


# === Unicode script detection ===
# Vietnamese-specific diacritics (Latin Extended Additional + signature chars)
_VN_DIACRITICS = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệ'
                      'ìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
                      'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆ'
                      'ÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ')

def _detect_script(ch):
    """Return script name for a character based on Unicode block."""
    if ch.isspace():
        return 'Space'
    cp = ord(ch)
    # Common ASCII letters
    if 0x0041 <= cp <= 0x007A:
        return 'Latin'
    # Latin Extended (À, é, ñ, ç, ł, ø, ü, etc.)
    if 0x00C0 <= cp <= 0x024F:
        return 'Latin'
    # ASCII symbols (& $ % + etc) — separate from punctuation
    if cp < 128 and ch in '&$%+=*@#/':
        return 'Symbol'
    # Cyrillic
    if 0x0400 <= cp <= 0x04FF or 0x0500 <= cp <= 0x052F:
        return 'Cyrillic'
    # Greek
    if 0x0370 <= cp <= 0x03FF:
        return 'Greek'
    # Arabic
    if 0x0600 <= cp <= 0x06FF or 0xFB50 <= cp <= 0xFDFF:
        return 'Arabic'
    # Devanagari (Hindi)
    if 0x0900 <= cp <= 0x097F:
        return 'Devanagari'
    # Thai
    if 0x0E00 <= cp <= 0x0E7F:
        return 'Thai'
    # Vietnamese (Latin Extended Additional)
    if 0x1E00 <= cp <= 0x1EFF:
        return 'Latin'
    # Hangul
    if 0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF or 0x3130 <= cp <= 0x318F:
        return 'Hangul'
    # CJK Unified (한자)
    if 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF:
        return 'CJK'
    # Hiragana
    if 0x3040 <= cp <= 0x309F:
        return 'Hiragana'
    # Katakana
    if 0x30A0 <= cp <= 0x30FF:
        return 'Katakana'
    # Digits (ASCII)
    if 0x0030 <= cp <= 0x0039:
        return 'Digit'
    # ASCII punctuation/symbols
    if cp < 128:
        return 'Punct'
    # Combining marks (don't break chunks)
    cat = unicodedata.category(ch)
    if cat.startswith('M'):
        return 'Combining'
    return 'Other'


# === Script → preferred Hunmin lang ===
_SCRIPT_TO_LANG = {
    'Latin':      None,        # use primary_lang
    'Cyrillic':   'ru',
    'Greek':      'el',
    'Arabic':     'ar',
    'Devanagari': 'hi',
    'Thai':       'th',
    'Hangul':     None,        # already Korean — pass through
    'CJK':        'zh',
    'Hiragana':   'ja',
    'Katakana':   'ja',
}


# === Digit transliteration ===
DIGITS_SINO = {
    '0':'영','1':'일','2':'이','3':'삼','4':'사',
    '5':'오','6':'육','7':'칠','8':'팔','9':'구',
}
DIGITS_NATIVE = {
    '0':'영','1':'하나','2':'둘','3':'셋','4':'넷',
    '5':'다섯','6':'여섯','7':'일곱','8':'여덟','9':'아홉',
}
# 영어 digit names (then run through en transcribe)
DIGITS_NAME_EN = {
    '0':'zero','1':'one','2':'two','3':'three','4':'four',
    '5':'five','6':'six','7':'seven','8':'eight','9':'nine',
}


# === Symbol transliteration (optional, drop by default) ===
SYMBOL_TO_KOR = {
    '&': '앤드',
    '@': '앳',
    '#': '샤프',
    '$': '달러',
    '%': '퍼센트',
    '+': '플러스',
    '=': '이콜',
    '*': '스타',
    '/': '슬래시',
}


def _split_by_script(text):
    """Split text into [(chunk, script), ...]"""
    if not text:
        return []
    chunks = []
    cur_chunk = [text[0]]
    cur_script = _detect_script(text[0])
    for ch in text[1:]:
        s = _detect_script(ch)
        # Combining marks attach to previous
        if s == 'Combining':
            cur_chunk.append(ch)
            continue
        # Same script (or both Latin/Hangul/CJK groups) → continue
        if s == cur_script:
            cur_chunk.append(ch)
        else:
            chunks.append((''.join(cur_chunk), cur_script))
            cur_chunk = [ch]
            cur_script = s
    chunks.append((''.join(cur_chunk), cur_script))
    return chunks


def _transliterate_digits(digit_str, mode, primary_lang='en'):
    """'5' → '오' (sino) / '다섯' (native) / 'five'→'파이브' (read)"""
    from .api import transcribe as _tr
    if mode == 'keep':
        return digit_str
    if mode == 'sino':
        return ''.join(DIGITS_SINO.get(c, c) for c in digit_str)
    if mode == 'native':
        # Native Korean only goes 1-99 cleanly; sino fallback for >9
        if len(digit_str) == 1:
            return DIGITS_NATIVE.get(digit_str, digit_str)
        return ''.join(DIGITS_SINO.get(c, c) for c in digit_str)
    if mode == 'read':
        # Read digits as words in primary_lang, then transcribe
        if primary_lang == 'en':
            words = ' '.join(DIGITS_NAME_EN.get(c, c) for c in digit_str)
            try: return _tr(words, 'en', level=1)
            except Exception: return digit_str
        # Korean default → sino
        return ''.join(DIGITS_SINO.get(c, c) for c in digit_str)
    return digit_str


def _transliterate_symbol(sym, mode, primary_lang='en'):
    """'$' → '달러' (kor) or transcribed name (read)"""
    if mode == 'keep':
        return sym
    if mode == 'kor':
        return SYMBOL_TO_KOR.get(sym, sym)
    if mode == 'drop':
        return ''
    return sym


def _detect_latin_lang(chunk):
    """Latin chunk를 더 세분 — Vietnamese 등 특수 diacritic 감지."""
    if any(c in _VN_DIACRITICS for c in chunk):
        return 'vi'
    return None


# === Manual letter → IPA mappings for scripts not supported by epitran ===
# epitran 미지원 언어는 직접 IPA로 변환해서 lang='ipa' 경로로 전사.
_GREEK_TO_IPA = {
    'α': 'a', 'β': 'v', 'γ': 'ɣ', 'δ': 'ð', 'ε': 'e',
    'ζ': 'z', 'η': 'i', 'θ': 'θ', 'ι': 'i', 'κ': 'k',
    'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'ks', 'ο': 'o',
    'π': 'p', 'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't',
    'υ': 'i', 'φ': 'f', 'χ': 'x', 'ψ': 'ps', 'ω': 'o',
    # 강세 모음 (액센트 제거 후 base)
    'ά': 'a', 'έ': 'e', 'ή': 'i', 'ί': 'i', 'ό': 'o',
    'ύ': 'i', 'ώ': 'o', 'ϊ': 'i', 'ϋ': 'i', 'ΐ': 'i', 'ΰ': 'i',
}

def _greek_to_ipa(text):
    """Modern Greek text → IPA (rough). lang='ipa' 경로로 전사하기 위함."""
    s = text.lower()
    # Digraphs/diphthongs (longer first)
    s = s.replace('μπ', 'b').replace('ντ', 'd').replace('γκ', 'g')
    s = s.replace('αι', 'e').replace('ει', 'i').replace('οι', 'i')
    s = s.replace('αυ', 'av').replace('ευ', 'ev').replace('ου', 'u')
    return ''.join(_GREEK_TO_IPA.get(c, c) for c in s)


def _detect_cjk_lang(chunk, full_text):
    """CJK 한자 chunk — full_text에 hiragana/katakana 있으면 ja, 아니면 zh."""
    for ch in full_text:
        s = _detect_script(ch)
        if s in ('Hiragana', 'Katakana'):
            return 'ja'
    return 'zh'


def transcribe_auto(text, primary_lang='en', mode=None,
                     digits='sino', symbols='kor',
                     punct='keep', strict=True):
    """Auto-routing transcribe — guarantees 100% UHPS encoding (no leak).

    Args:
      text: 임의 입력 (mixed scripts, digits, symbols).
      primary_lang: Latin/ASCII chunk가 어떤 lang으로 처리될지 (default 'en').
      mode: HUNMIN_NIKL / HUNMIN_PHONETIC / UHPS_CORE / UHPS_JAMO / UHPS_FULL
            (None = HUNMIN_NIKL).
      digits: 'sino'(default,오) / 'native'(다섯) / 'read'(파이브) / 'keep'(5).
      symbols: 'kor'(default,달러) / 'drop' / 'keep'.
      punct: 'keep'(default) / 'drop'.
      strict: True면 인코딩 못한 글자가 있으면 ValueError.

    Returns:
      str: 모든 글자가 한글/UHPS-jamo로 변환된 결과.
    """
    from .api import transcribe as _tr, HUNMIN_NIKL
    if mode is None:
        mode = HUNMIN_NIKL

    out = []
    leaked = []

    for chunk, script in _split_by_script(text):
        if script == 'Space':
            out.append(chunk); continue
        if script == 'Punct':
            if punct == 'keep':
                out.append(chunk)
            else:
                out.append('')  # drop
            continue
        if script == 'Symbol':
            piece = ''.join(_transliterate_symbol(c, symbols, primary_lang)
                              for c in chunk)
            out.append(piece)
            if symbols == 'keep':
                leaked.extend(c for c in chunk if c not in SYMBOL_TO_KOR)
            continue
        if script == 'Digit':
            out.append(_transliterate_digits(chunk, digits, primary_lang))
            continue
        if script == 'Hangul':
            out.append(chunk)  # already Korean
            continue
        if script == 'Other':
            # Unknown — try symbol fallback
            piece = ''.join(_transliterate_symbol(c, symbols, primary_lang)
                              for c in chunk)
            if symbols == 'keep':
                out.append(chunk)
                leaked.extend(chunk)
            else:
                out.append(piece)
            continue
        # Greek — manual IPA fallback (epitran 미지원)
        if script == 'Greek':
            ipa = _greek_to_ipa(chunk)
            try:
                out.append(_tr(ipa, 'ipa', mode=mode))
            except Exception:
                if strict:
                    leaked.extend(chunk)
                else:
                    out.append(chunk)
            continue

        # Letter scripts
        target_lang = _SCRIPT_TO_LANG.get(script)
        if target_lang is None:
            target_lang = primary_lang
        # Latin sub-detection: Vietnamese 등
        if script == 'Latin':
            sub = _detect_latin_lang(chunk)
            if sub:
                target_lang = sub
        # CJK sub-detection: Japanese vs Chinese
        if script == 'CJK':
            target_lang = _detect_cjk_lang(chunk, text)
        try:
            out.append(_tr(chunk, target_lang, mode=mode))
        except Exception:
            # Universal/IPA fallback
            try:
                out.append(_tr(chunk, target_lang, level=1))
            except Exception:
                if strict:
                    leaked.extend(chunk)
                else:
                    out.append(chunk)

    result = ''.join(out)
    if strict and leaked:
        raise ValueError(
            f"Could not encode {len(leaked)} character(s) to UHPS: {leaked!r}. "
            f"Use strict=False to leave them as-is, or extend mappings.")
    return result
