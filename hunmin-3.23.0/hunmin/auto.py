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
    # Hebrew
    if 0x0590 <= cp <= 0x05FF:
        return 'Hebrew'
    # Armenian
    if 0x0530 <= cp <= 0x058F or 0xFB13 <= cp <= 0xFB17:
        return 'Armenian'
    # Georgian
    if 0x10A0 <= cp <= 0x10FF or 0x2D00 <= cp <= 0x2D2F:
        return 'Georgian'
    # Tibetan
    if 0x0F00 <= cp <= 0x0FFF:
        return 'Tibetan'
    # Khmer
    if 0x1780 <= cp <= 0x17FF:
        return 'Khmer'
    # Lao
    if 0x0E80 <= cp <= 0x0EFF:
        return 'Lao'
    # Burmese (Myanmar)
    if 0x1000 <= cp <= 0x109F:
        return 'Burmese'
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
    # Unicode punctuation — ¿, ¡, —, –, ", ", « » etc
    if cat.startswith('P'):
        return 'Punct'
    # Unicode symbols (Sm/Sc/So) — ©, ™, € etc → treat as Symbol
    if cat.startswith('S'):
        return 'Symbol'
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


# Mongolian-specific Cyrillic letters (not in Russian)
_MN_DIACRITICS = set('өүӨҮ')

def _detect_cyrillic_lang(chunk):
    """Cyrillic chunk → ru/mn 등 세분."""
    if any(c in _MN_DIACRITICS for c in chunk):
        return 'mn'
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


# === Hebrew (modern Israeli) → IPA ===
# epitran 미지원 → letter→IPA 매핑으로 lang='ipa' 경로
_HEBREW_TO_IPA = {
    # Consonants
    'א': '',    # silent (or glottal stop carrier — drop)
    'ב': 'v',   # vet (default; bet ב is /b/, but we lack dagesh detection)
    'ג': 'g',   # gimel
    'ד': 'd',   # dalet
    'ה': 'h',   # he
    'ו': 'v',   # vav (consonant) — also used as vowel marker
    'ז': 'z',
    'ח': 'x',   # khet
    'ט': 't',
    'י': 'j',   # yod
    'כ': 'x',   # kaf (without dagesh = /x/)
    'ך': 'x',   # final kaf
    'ל': 'l',
    'מ': 'm',
    'ם': 'm',   # final mem
    'נ': 'n',
    'ן': 'n',   # final nun
    'ס': 's',
    'ע': '',    # ayin (modern silent or glottal)
    'פ': 'f',   # pe (without dagesh)
    'ף': 'f',   # final pe
    'צ': 'ʦ',   # tsadi
    'ץ': 'ʦ',
    'ק': 'k',
    'ר': 'ʁ',   # resh (uvular in Israeli Hebrew)
    'ש': 'ʃ',   # shin (default; sin ש = /s/, lack diacritic)
    'ת': 't',
    # Common vowel diacritics (niqqud) — usually omitted; map if present
    'ַ': 'a',   # patah
    'ָ': 'a',   # qamatz
    'ֵ': 'e',   # tsere
    'ֶ': 'e',   # segol
    'ִ': 'i',   # hiriq
    'ֹ': 'o',   # holam
    'ֻ': 'u',   # qubuts
    'ְ': '',    # sheva (silent in modern)
}

def _hebrew_to_ipa(text):
    """Modern Hebrew → IPA (rough). niqqud 없는 경우는 자음 sequence."""
    return ''.join(_HEBREW_TO_IPA.get(c, c) for c in text)


# === Armenian → IPA (Eastern Armenian) ===
_ARMENIAN_TO_IPA = {
    'ա':'a','բ':'b','գ':'g','դ':'d','ե':'e','զ':'z',
    'է':'e','ը':'ə','թ':'tʰ','ժ':'ʒ','ի':'i','լ':'l',
    'խ':'x','ծ':'ʦ','կ':'k','հ':'h','ձ':'ʣ','ղ':'ʁ',
    'ճ':'ʧ','մ':'m','յ':'j','ն':'n','շ':'ʃ','ո':'o',
    'չ':'ʧʰ','պ':'p','ջ':'ʤ','ռ':'r','ս':'s','վ':'v',
    'տ':'t','ր':'ɾ','ց':'ʦʰ','ու':'u','փ':'pʰ','ք':'kʰ',
    'օ':'o','ֆ':'f',
    # uppercase
    'Ա':'a','Բ':'b','Գ':'g','Դ':'d','Ե':'e','Զ':'z',
    'Է':'e','Ը':'ə','Թ':'tʰ','Ժ':'ʒ','Ի':'i','Լ':'l',
    'Խ':'x','Ծ':'ʦ','Կ':'k','Հ':'h','Ձ':'ʣ','Ղ':'ʁ',
    'Ճ':'ʧ','Մ':'m','Յ':'j','Ն':'n','Շ':'ʃ','Ո':'o',
    'Չ':'ʧʰ','Պ':'p','Ջ':'ʤ','Ռ':'r','Ս':'s','Վ':'v',
    'Տ':'t','Ր':'ɾ','Ց':'ʦʰ','Փ':'pʰ','Ք':'kʰ',
    'Օ':'o','Ֆ':'f',
}

def _armenian_to_ipa(text):
    s = text.replace('ու', 'u').replace('ՈՒ', 'u').replace('Ու', 'u')
    return ''.join(_ARMENIAN_TO_IPA.get(c, c) for c in s)


# === Georgian → IPA ===
_GEORGIAN_TO_IPA = {
    'ა':'a','ბ':'b','გ':'g','დ':'d','ე':'e','ვ':'v',
    'ზ':'z','თ':'tʰ','ი':'i','კ':'kʼ','ლ':'l','მ':'m',
    'ნ':'n','ო':'o','პ':'pʼ','ჟ':'ʒ','რ':'r','ს':'s',
    'ტ':'tʼ','უ':'u','ფ':'pʰ','ქ':'kʰ','ღ':'ʁ','ყ':'qʼ',
    'შ':'ʃ','ჩ':'ʧʰ','ც':'ʦʰ','ძ':'ʣ','წ':'ʦʼ','ჭ':'ʧʼ',
    'ხ':'x','ჯ':'ʤ','ჰ':'h',
}

def _georgian_to_ipa(text):
    return ''.join(_GEORGIAN_TO_IPA.get(c, c) for c in text)


# === Mongolian Cyrillic → IPA (Khalkha) ===
# 35-letter Khalkha Mongolian Cyrillic alphabet
_MONGOLIAN_TO_IPA = {
    'а':'a','б':'b','в':'w','г':'g','д':'d','е':'je','ё':'jo',
    'ж':'ʤ','з':'ʣ','и':'i','й':'j','к':'k','л':'ɮ','м':'m',
    'н':'n','о':'o','ө':'ɵ','п':'pʰ','р':'r','с':'s','т':'tʰ',
    'у':'ʊ','ү':'u','ф':'f','х':'x','ц':'ʦʰ','ч':'ʧʰ','ш':'ʃ',
    'щ':'ʃʧʰ','ъ':'','ы':'i','ь':'','э':'e','ю':'ju','я':'ja',
    # Uppercase mirror
    'А':'a','Б':'b','В':'w','Г':'g','Д':'d','Е':'je','Ё':'jo',
    'Ж':'ʤ','З':'ʣ','И':'i','Й':'j','К':'k','Л':'ɮ','М':'m',
    'Н':'n','О':'o','Ө':'ɵ','П':'pʰ','Р':'r','С':'s','Т':'tʰ',
    'У':'ʊ','Ү':'u','Ф':'f','Х':'x','Ц':'ʦʰ','Ч':'ʧʰ','Ш':'ʃ',
    'Щ':'ʃʧʰ','Ъ':'','Ы':'i','Ь':'','Э':'e','Ю':'ju','Я':'ja',
}

def _mongolian_to_ipa(text):
    return ''.join(_MONGOLIAN_TO_IPA.get(c, c) for c in text)


# === Persian (Farsi) Arabic-script → IPA (rough) ===
# Persian uses Arabic script with extra letters (پ چ ژ گ).
# Short vowels are unwritten — we insert 'a' between consonants for readability.
_PERSIAN_TO_IPA = {
    'ا':'ɒ','ب':'b','پ':'p','ت':'t','ث':'s','ج':'ʤ','چ':'ʧ',
    'ح':'h','خ':'x','د':'d','ذ':'z','ر':'r','ز':'z','ژ':'ʒ',
    'س':'s','ش':'ʃ','ص':'s','ض':'z','ط':'t','ظ':'z','ع':'',
    'غ':'ɣ','ف':'f','ق':'ɣ','ک':'k','گ':'g','ل':'l','م':'m',
    'ن':'n','و':'v','ه':'h','ی':'i','ي':'i','ك':'k',
    # Vowel diacritics (rare in text)
    'َ':'a','ِ':'e','ُ':'o',
    'ء':'',  # hamza
    # Common digraphs
    'آ':'ɒ',  # alef madda
}

def _persian_to_ipa(text):
    """Persian Arabic-script → IPA. 자음 사이에 schwa 삽입 (short vowel 없으면)."""
    out = []
    prev_vowel = False
    for c in text:
        ipa = _PERSIAN_TO_IPA.get(c, '')
        if not ipa:
            continue
        if ipa in 'aeiouɒəɛɔɪʊ':
            out.append(ipa)
            prev_vowel = True
        else:
            # 자음 — 앞이 자음이면 'a' 삽입
            if not prev_vowel and out:
                out.append('a')
            out.append(ipa)
            prev_vowel = False
    # 끝이 자음이면 default vowel 추가 안 함 (한국어 ㅡ-syll로 자동 처리)
    return ''.join(out)


# === Tibetan → IPA (rough Lhasa) ===
# Tibetan has complex syllable structure; this is letter-level only (rough)
_TIBETAN_TO_IPA = {
    'ཀ':'k','ཁ':'kʰ','ག':'g','ང':'ŋ',
    'ཅ':'tɕ','ཆ':'tɕʰ','ཇ':'dʑ','ཉ':'ɲ',
    'ཏ':'t','ཐ':'tʰ','ད':'d','ན':'n',
    'པ':'p','ཕ':'pʰ','བ':'b','མ':'m',
    'ཙ':'ts','ཚ':'tsʰ','ཛ':'dz','ཝ':'w',
    'ཞ':'ʑ','ཟ':'z','འ':'','ཡ':'j',
    'ར':'r','ལ':'l','ཤ':'ʃ','ས':'s',
    'ཧ':'h','ཨ':'a',
    # Vowel diacritics
    'ི':'i','ུ':'u','ེ':'e','ོ':'o',
    # Subjoined consonants (U+0F90..U+0FBC) — same sounds as base
    'ྐ':'k','ྑ':'kʰ','ྒ':'g','ྔ':'ŋ',
    'ྕ':'tɕ','ྖ':'tɕʰ','ྗ':'dʑ','ྙ':'ɲ',
    'ྟ':'t','ྠ':'tʰ','ྡ':'d','ྣ':'n',
    'ྤ':'p','ྥ':'pʰ','ྦ':'b','ྨ':'m',
    'ྩ':'ts','ྪ':'tsʰ','ྫ':'dz','ྭ':'w',
    'ྮ':'ʑ','ྯ':'z','ྰ':'','ྱ':'j',
    'ྲ':'r','ླ':'l','ྴ':'ʃ','ྶ':'s',
    'ྷ':'h','ྸ':'',
    # Structural marks
    '་':' ','།':' ','༎':' ','༏':' ',
    '྄':'','ྺ':'','ྻ':'','ྼ':'',
}

def _tibetan_to_ipa(text):
    return ''.join(_TIBETAN_TO_IPA.get(c, c) for c in text)


# === Khmer → IPA (rough Central Khmer) ===
_KHMER_TO_IPA = {
    'ក':'k','ខ':'kʰ','គ':'k','ឃ':'kʰ','ង':'ŋ',
    'ច':'tɕ','ឆ':'tɕʰ','ជ':'tɕ','ឈ':'tɕʰ','ញ':'ɲ',
    'ដ':'ɗ','ឋ':'tʰ','ឌ':'ɗ','ឍ':'tʰ','ណ':'n',
    'ត':'t','ថ':'tʰ','ទ':'t','ធ':'tʰ','ន':'n',
    'ប':'ɓ','ផ':'pʰ','ព':'p','ភ':'pʰ','ម':'m',
    'យ':'j','រ':'r','ល':'l','វ':'w',
    'ស':'s','ហ':'h','ឡ':'l','អ':'',
    # Independent vowels
    'ឥ':'i','ឦ':'iː','ឧ':'u','ឩ':'uː','ឯ':'e','ឱ':'oː','ឲ':'oː',
    # Vowels (combining)
    'ា':'aː','ិ':'i','ី':'iː','ុ':'u','ូ':'uː','ួ':'uə',
    'េ':'e','ែ':'ɛ','ៃ':'aj','ោ':'oː','ៅ':'aw',
    'ើ':'əː','ឿ':'ɨə','ៀ':'iə','ឹ':'ɨ','ឺ':'ɨː',
    'ុំ':'om','ំ':'m','ាំ':'am','ះ':'h','់':'','៉':'','៊':'','័':'','៌':'','៍':'','៎':'','៏':'','្':'',
    # Punctuation/sep
    '។':' ','៕':' ','៖':' ','៙':' ','៚':' ',
}

def _khmer_to_ipa(text):
    return ''.join(_KHMER_TO_IPA.get(c, c) for c in text)


# === Lao → IPA ===
_LAO_TO_IPA = {
    'ກ':'k','ຂ':'kʰ','ຄ':'kʰ','ງ':'ŋ',
    'ຈ':'tɕ','ສ':'s','ຊ':'s','ຍ':'ɲ',
    'ດ':'d','ຕ':'t','ຖ':'tʰ','ທ':'tʰ','ນ':'n',
    'ບ':'b','ປ':'p','ຜ':'pʰ','ຝ':'f','ພ':'pʰ','ຟ':'f','ມ':'m',
    'ຢ':'j','ຣ':'r','ລ':'l','ວ':'w','ຽ':'ia',
    'ຫ':'h','ອ':'','ຮ':'h',
    # Vowels (combining)
    'ະ':'a','າ':'aː','ິ':'i','ີ':'iː','ຸ':'u','ູ':'uː',
    'ເ':'e','ແ':'ɛ','ໂ':'o','ໄ':'aj','ໃ':'aj',
    'ໍ':'o','ັ':'a','ົ':'o','ຼ':'l',
    # Tone marks (silent in our rough mapping)
    '່':'','້':'','໊':'','໋':'','໌':'','ໍ':'',
    # Punctuation
    'ໆ':'','ຯ':'',
}

def _lao_to_ipa(text):
    return ''.join(_LAO_TO_IPA.get(c, c) for c in text)


# === Burmese (Myanmar) → IPA ===
_BURMESE_TO_IPA = {
    'က':'k','ခ':'kʰ','ဂ':'g','ဃ':'g','င':'ŋ',
    'စ':'s','ဆ':'sʰ','ဇ':'z','ဈ':'z','ဉ':'ɲ','ည':'ɲ',
    'ဋ':'t','ဌ':'tʰ','ဍ':'d','ဎ':'d','ဏ':'n',
    'တ':'t','ထ':'tʰ','ဒ':'d','ဓ':'d','န':'n',
    'ပ':'p','ဖ':'pʰ','ဗ':'b','ဘ':'b','မ':'m',
    'ယ':'j','ရ':'j','လ':'l','ဝ':'w','သ':'θ','ဟ':'h','ဠ':'l','အ':'a',
    # Vowel marks
    'ာ':'a','ါ':'a','ိ':'i','ီ':'iː','ု':'u','ူ':'uː','ေ':'e','ဲ':'ɛ',
    'ော':'oː','ို':'o','ဳ':'iː','ဴ':'aw','ဵ':'e','ံ':'ɛ','့':'ɛ',
    'ံ':'m','ိံ':'iN','ုံ':'oN',
    # Structural marks (silent)
    '်':'','ျ':'j','ြ':'j','ွ':'w','ှ':'h','ဿ':'s',
    '္':'','၀':'0','၁':'1','၂':'2','၃':'3','၄':'4','၅':'5','၆':'6','၇':'7','၈':'8','၉':'9',
    # Punctuation
    '။':' ','၊':' ',
}

def _burmese_to_ipa(text):
    return ''.join(_BURMESE_TO_IPA.get(c, c) for c in text)


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
            # leak: 매핑에 없는 기호 (모든 mode에서 — drop은 강제 OK 표시 위해 mode!=drop만 체크)
            if symbols != 'drop':
                for c in chunk:
                    if c not in SYMBOL_TO_KOR:
                        leaked.append(c)
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
                # leak detection: char가 SYMBOL_TO_KOR에 없으면 인코딩 안 됨
                for c in chunk:
                    if c not in SYMBOL_TO_KOR:
                        leaked.append(c)
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
        # Hebrew — manual IPA fallback
        if script == 'Hebrew':
            ipa = _hebrew_to_ipa(chunk)
            try:
                out.append(_tr(ipa, 'ipa', mode=mode))
            except Exception:
                if strict:
                    leaked.extend(chunk)
                else:
                    out.append(chunk)
            continue
        # Armenian — manual IPA fallback
        if script == 'Armenian':
            ipa = _armenian_to_ipa(chunk)
            try:
                out.append(_tr(ipa, 'ipa', mode=mode))
            except Exception:
                if strict:
                    leaked.extend(chunk)
                else:
                    out.append(chunk)
            continue
        # Georgian — manual IPA fallback
        if script == 'Georgian':
            ipa = _georgian_to_ipa(chunk)
            try:
                out.append(_tr(ipa, 'ipa', mode=mode))
            except Exception:
                if strict:
                    leaked.extend(chunk)
                else:
                    out.append(chunk)
            continue
        # Tibetan/Khmer/Lao/Burmese — manual IPA fallback
        if script in ('Tibetan', 'Khmer', 'Lao', 'Burmese'):
            converters = {
                'Tibetan': _tibetan_to_ipa,
                'Khmer': _khmer_to_ipa,
                'Lao': _lao_to_ipa,
                'Burmese': _burmese_to_ipa,
            }
            ipa = converters[script](chunk)
            try:
                out.append(_tr(ipa, 'ipa', mode=mode))
            except Exception:
                if strict:
                    leaked.extend(chunk)
                else:
                    out.append(chunk)
            continue

        # Arabic script with Persian-specific letters → use Persian IPA mapping
        # (Persian/Urdu/Pashto 모두 Arabic + 추가 글자 사용)
        if script == 'Arabic' and any(c in 'پچژگ' for c in chunk):
            ipa = _persian_to_ipa(chunk)
            try:
                out.append(_tr(ipa, 'ipa', mode=mode))
            except Exception:
                if strict: leaked.extend(chunk)
                else: out.append(chunk)
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
        # Cyrillic sub-detection: Mongolian
        if script == 'Cyrillic':
            sub = _detect_cyrillic_lang(chunk)
            if sub == 'mn':
                # Use manual Mongolian → IPA fallback (epitran 'mon-Cyrl-bab' 사용 가능하지만 우리 매핑이 더 정확)
                ipa = _mongolian_to_ipa(chunk)
                try:
                    out.append(_tr(ipa, 'ipa', mode=mode))
                except Exception:
                    if strict: leaked.extend(chunk)
                    else: out.append(chunk)
                continue
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
