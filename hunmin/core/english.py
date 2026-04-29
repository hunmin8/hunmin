"""Hunmin Precise — English (en) ARPABET → UHPS jamo.

전략: 영어는 spelling 불규칙 → CMU ARPABET 음소 사전 사용.
- v1의 phoneme.py 매핑 (이미 UHPS와 호환) 활용
- nltk 없는 환경 대비 inline essential dict (~100 words)
- 외부 cmudict 사용 가능시 자동 활용

ARPABET → UHPS 매핑:
  TH → ㅅ (/θ/), DH → ㄷ (/ð/)
  ZH → ㅈ (/ʒ/), SH → ㅅ (/ʃ/)
  F → ㆄ (/f/), V → ㅸ (/v/), Z → ㅿ (/z/)
  CH → ㅊ (/tʃ/), JH → ㅈ (/dʒ/)
  R → ㄹ (/ɹ/)
  AE → ㅐ (/æ/), AH → ㅓ (/ə,ʌ/)
  IH → ㅣ (/ɪ/), UH → ㅜ (/ʊ/)
"""
import re
from pathlib import Path

# === ARPABET → UHPS jamo (with stress digit stripped) ===
# Based on v1/core/transliteration/phoneme.py — UHPS 호환 검증됨

CONSONANTS = {
    # Plosives
    'P': 'ㅍ', 'B': 'ㅂ', 'T': 'ㅌ', 'D': 'ㄷ', 'K': 'ㅋ', 'G': 'ㄱ',
    # Nasals
    'M': 'ㅁ', 'N': 'ㄴ', 'NG': 'ㅇ',
    # Fricatives (UHPS: F→ㆄ, V→ㅸ, Z→ㅿ in precise)
    'F': 'ㆄ', 'V': 'ㅸ', 'S': 'ㅅ', 'Z': 'ㅿ',
    'SH': 'ㅅ', 'ZH': 'ㅈ',
    'TH': 'ㅅ', 'DH': 'ㄷ',
    'HH': 'ㅎ',
    # Affricates
    'CH': 'ㅊ', 'JH': 'ㅈ',
    # Liquids
    'L': 'ㄹ', 'R': 'ㄹ',
    # Glides
    'W': 'ㅇ', 'Y': 'ㅇ',  # placeholder, vowel attaches
}

# Basic mode (옛한글 X)
CONSONANTS_BASIC = dict(CONSONANTS)
CONSONANTS_BASIC.update({'F': 'ㅍ', 'V': 'ㅂ', 'Z': 'ㅈ'})

VOWELS = {
    'AA': 'ㅏ',   # father
    'AE': 'ㅐ',   # cat
    'AH': 'ㅓ',   # but, about (schwa)
    'AO': 'ㅗ',   # caught
    'AW': ('ㅏ', 'ㅜ'),  # cow
    'AY': ('ㅏ', 'ㅣ'),  # my
    'EH': 'ㅔ',   # bed
    'ER': ('ㅓ', 'ㄹ'),  # bird (벌)
    'EY': ('ㅔ', 'ㅣ'),  # day
    'IH': 'ㅣ',   # bit
    'IY': 'ㅣ',   # bee
    'OW': ('ㅗ', 'ㅜ'),  # go
    'OY': ('ㅗ', 'ㅣ'),  # boy
    'UH': 'ㅜ',   # book
    'UW': 'ㅜ',   # boot
}

# Y/W + vowel → palatal/W vowel
Y_VOWEL = {'AA':'ㅑ','AE':'ㅒ','AH':'ㅑ','AO':'ㅛ','EH':'ㅖ','IH':'ㅣ','IY':'ㅣ','UH':'ㅠ','UW':'ㅠ'}
W_VOWEL = {'AA':'ㅘ','AE':'ㅙ','AH':'ㅝ','AO':'ㅝ','EH':'ㅞ','IH':'ㅟ','IY':'ㅟ','UH':'ㅜ','UW':'ㅜ'}


# === Essential CMU dictionary (inline, ~100 words for testing) ===
# Format: word → ARPABET phoneme list (stress digit stripped)
ESSENTIAL_CMU = {
    # /θ/ /ð/ minimal pairs
    'think': ['TH','IH','NG','K'],
    'thank': ['TH','AE','NG','K'],
    'three': ['TH','R','IY'],
    'this': ['DH','IH','S'],
    'that': ['DH','AE','T'],
    'they': ['DH','EY'],
    'sin': ['S','IH','N'],
    'sing': ['S','IH','NG'],
    'son': ['S','AH','N'],
    # /v/ /b/ minimal pairs
    'vine': ['V','AY','N'],
    'bine': ['B','AY','N'],
    'very': ['V','EH','R','IY'],
    'berry': ['B','EH','R','IY'],
    'vote': ['V','OW','T'],
    'boat': ['B','OW','T'],
    # /f/ /p/ minimal pairs
    'fast': ['F','AE','S','T'],
    'past': ['P','AE','S','T'],
    'father': ['F','AA','DH','ER'],
    'phone': ['F','OW','N'],
    'fish': ['F','IH','SH'],
    # /z/ /s/ minimal pairs
    'zoo': ['Z','UW'],
    'sue': ['S','UW'],
    'zebra': ['Z','IY','B','R','AH'],
    'zone': ['Z','OW','N'],
    # /ʒ/ minimal
    'vision': ['V','IH','ZH','AH','N'],
    'measure': ['M','EH','ZH','ER'],
    'pleasure': ['P','L','EH','ZH','ER'],
    # /ʃ/ /tʃ/
    'shoe': ['SH','UW'],
    'show': ['SH','OW'],
    'cheese': ['CH','IY','Z'],
    'church': ['CH','ER','CH'],
    # /ɹ/ /l/
    'red': ['R','EH','D'],
    'led': ['L','EH','D'],
    'right': ['R','AY','T'],
    'light': ['L','AY','T'],
    'rice': ['R','AY','S'],
    'lice': ['L','AY','S'],
    # 일반 단어
    'hello': ['HH','AH','L','OW'],
    'world': ['W','ER','L','D'],
    'student': ['S','T','UW','D','AH','N','T'],
    'teacher': ['T','IY','CH','ER'],
    'book': ['B','UH','K'],
    'cat': ['K','AE','T'],
    'dog': ['D','AO','G'],
    'house': ['HH','AW','S'],
    'water': ['W','AO','T','ER'],
    'apple': ['AE','P','AH','L'],
    'orange': ['AO','R','AH','N','JH'],
    'mother': ['M','AH','DH','ER'],
    'brother': ['B','R','AH','DH','ER'],
    'sister': ['S','IH','S','T','ER'],
    'family': ['F','AE','M','AH','L','IY'],
    'love': ['L','AH','V'],
    'live': ['L','IH','V'],
    'leave': ['L','IY','V'],
    'happy': ['HH','AE','P','IY'],
    'school': ['S','K','UW','L'],
    'work': ['W','ER','K'],
    'play': ['P','L','EY'],
    'read': ['R','IY','D'],
    'write': ['R','AY','T'],
    'speak': ['S','P','IY','K'],
    'listen': ['L','IH','S','AH','N'],
    'good': ['G','UH','D'],
    'bad': ['B','AE','D'],
    'big': ['B','IH','G'],
    'small': ['S','M','AO','L'],
    'new': ['N','UW'],
    'old': ['OW','L','D'],
    'hot': ['HH','AA','T'],
    'cold': ['K','OW','L','D'],
    'fast': ['F','AE','S','T'],
    'slow': ['S','L','OW'],
    'one': ['W','AH','N'],
    'two': ['T','UW'],
    'three': ['TH','R','IY'],
    'four': ['F','AO','R'],
    'five': ['F','AY','V'],
    'yes': ['Y','EH','S'],
    'no': ['N','OW'],
    'please': ['P','L','IY','Z'],
    'thanks': ['TH','AE','NG','K','S'],
    'sorry': ['S','AA','R','IY'],
    'time': ['T','AY','M'],
    'day': ['D','EY'],
    'night': ['N','AY','T'],
    'morning': ['M','AO','R','N','IH','NG'],
    'evening': ['IY','V','N','IH','NG'],
    'year': ['Y','IH','R'],
    # Names (lowercase keys for lookup consistency)
    'boston': ['B','AO','S','T','AH','N'],
    'paris': ['P','AE','R','IH','S'],
    'london': ['L','AH','N','D','AH','N'],
    'tokyo': ['T','OW','K','IY','OW'],
    'seoul': ['S','OW','L'],
    'america': ['AH','M','EH','R','AH','K','AH'],
    'africa': ['AE','F','R','AH','K','AH'],
    'korea': ['K','AO','R','IY','AH'],
    'christmas': ['K','R','IH','S','M','AH','S'],
    # 외래어 자주 쓰는
    'computer': ['K','AH','M','P','Y','UW','T','ER'],
    'internet': ['IH','N','T','ER','N','EH','T'],
    'phone': ['F','OW','N'],
    'email': ['IY','M','EY','L'],
    'coffee': ['K','AO','F','IY'],
    'tea': ['T','IY'],
    'pizza': ['P','IY','T','S','AH'],
    'music': ['M','Y','UW','Z','IH','K'],
    'movie': ['M','UW','V','IY'],
    'video': ['V','IH','D','IY','OW'],
    'song': ['S','AO','NG'],
    'dance': ['D','AE','N','S'],
    'food': ['F','UW','D'],
    'drink': ['D','R','IH','NG','K'],
    'sleep': ['S','L','IY','P'],
    'eat': ['IY','T'],
}


# Try loading external CMU dict if available
def _try_load_external_cmu():
    """Look for cmudict.dict in data/ or use nltk."""
    cmu = {}
    # Try local file first
    candidates = [
        Path(__file__).resolve().parent.parent / 'data' / 'cmudict.dict',
    ]
    for p in candidates:
        if p.exists():
            try:
                for line in p.read_text().splitlines():
                    if not line.strip() or line.startswith(';;;') or line.startswith('HTTP'):
                        continue
                    parts = line.strip().split(' ', 1)
                    if len(parts) != 2: continue
                    word, ph = parts
                    word = word.lower().split('(')[0]  # strip variant marker (1)
                    phs = [re.sub(r'[0-9]', '', p) for p in ph.split()]
                    if word not in cmu:  # keep first variant
                        cmu[word] = phs
                if cmu:
                    return cmu
            except Exception:
                pass
    # Try nltk
    try:
        from nltk.corpus import cmudict
        d = cmudict.dict()
        for word, phs_list in d.items():
            cmu[word.lower()] = [re.sub(r'[0-9]', '', p) for p in phs_list[0]]
        return cmu
    except Exception:
        pass
    return {}


_EXT_CMU = _try_load_external_cmu()


def get_phonemes(word):
    """word → ARPABET list (stress stripped). None if not found."""
    w = word.lower()
    # Essential first (testing 우선)
    if w in ESSENTIAL_CMU:
        return ESSENTIAL_CMU[w]
    if w in _EXT_CMU:
        return _EXT_CMU[w]
    return None


# === Hangul composition ===
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


# === Phonemize: ARPABET list → phoneme tuple list (UHPS) ===
def _phonemize_arpabet(phs, precise):
    """ARPABET list → UHPS phoneme tuple list."""
    cmap = CONSONANTS if precise else CONSONANTS_BASIC
    out = []
    i = 0
    n = len(phs)
    while i < n:
        p = phs[i]
        nxt = phs[i+1] if i+1 < n else ''
        # Y + V → palatal
        if p == 'Y' and nxt in Y_VOWEL:
            out.append(('C', 'ㅇ', 'y'))
            out.append(('SV', Y_VOWEL[nxt]))
            i += 2; continue
        # W + V → W vowel
        if p == 'W' and nxt in W_VOWEL:
            out.append(('C', 'ㅇ', 'w'))
            out.append(('SV', W_VOWEL[nxt]))
            i += 2; continue
        # Vowel
        if p in VOWELS:
            v = VOWELS[p]
            if isinstance(v, tuple):
                # diphthong → 2 V (or V + ㄹ for ER)
                if p == 'ER':
                    out.append(('V', v[0]))
                    out.append(('C', v[1], 'r'))
                else:
                    out.append(('V', v[0]))
                    out.append(('V', v[1]))
            else:
                out.append(('V', v))
            i += 1; continue
        # Consonant
        if p in cmap:
            jamo = cmap[p]
            # 옛한글 처리
            if jamo in ('ㆄ', 'ㅸ', 'ㅿ'):
                out.append(('OLD', jamo))
            else:
                # src 추적: 받침 정책용
                src = p.lower()
                out.append(('C', jamo, src))
            i += 1; continue
        # Unknown
        i += 1
    return out


def _add_jong_to_last(syllables, jong):
    if not syllables: return False
    last = syllables[-1]
    if len(last) == 1:
        c = ord(last)
        if 0xAC00 <= c <= 0xD7A3:
            base = c - HANGUL_BASE
            cho = base // 588; jung = (base % 588) // 28; jg = base % 28
            if jg == 0 and jong in FINALS:
                syllables[-1] = chr(HANGUL_BASE + cho*588 + jung*28 + FINALS.index(jong))
                return True
    return False


def _has_jong(s):
    if len(s) != 1: return True
    c = ord(s)
    if not (0xAC00 <= c <= 0xD7A3): return False
    return (c - HANGUL_BASE) % 28 != 0


ALLOW_AS_FINAL = {'ㄴ', 'ㅁ', 'ㄹ', 'ㅇ'}


def _next_is_vowel(phs, i):
    return i+1 < len(phs) and phs[i+1][0] in ('V', 'SV')


def _assemble(phonemes, precise):
    syllables = []
    i = 0
    n = len(phonemes)
    while i < n:
        ph = phonemes[i]
        kind = ph[0]
        if kind in ('V', 'SV'):
            syllables.append(_compose('ㅇ', ph[1])); i += 1; continue
        if kind == 'OLD':
            old = ph[1]
            if _next_is_vowel(phonemes, i):
                syllables.append(old)
                syllables.append(_compose('ㅇ', phonemes[i+1][1]))
                i += 2
            else:
                syllables.append(old); i += 1
            continue
        if kind == 'C':
            cho = ph[1]; src = ph[2] if len(ph) > 2 else ''
            if _next_is_vowel(phonemes, i):
                syllables.append(_compose(cho, phonemes[i+1][1])); i += 2
                continue
            # 어말/자음 앞
            if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                if _add_jong_to_last(syllables, cho):
                    i += 1; continue
            # k/t/p 어말 → ㄱ/ㅅ/ㅂ 받침
            if src in ('k', 'g') and cho == 'ㅋ' and syllables and not _has_jong(syllables[-1]):
                if _add_jong_to_last(syllables, 'ㄱ'): i += 1; continue
            if src == 't' and cho == 'ㅌ' and syllables and not _has_jong(syllables[-1]):
                if _add_jong_to_last(syllables, 'ㅅ'): i += 1; continue
            if src == 'p' and cho == 'ㅍ' and syllables and not _has_jong(syllables[-1]):
                if _add_jong_to_last(syllables, 'ㅂ'): i += 1; continue
            # 그 외 → 으-syll
            syllables.append(_compose(cho, 'ㅡ')); i += 1
            continue
        i += 1
    return ''.join(syllables)


def _to_jamo_seq(phonemes):
    out = []
    for ph in phonemes:
        kind = ph[0]
        if kind in ('V', 'SV'):
            out.append(ph[1])
        elif kind == 'C':
            if ph[1] == 'ㅇ' and len(ph) > 2 and ph[2] in ('y','w'):
                pass
            else:
                out.append(ph[1])
        elif kind == 'OLD':
            out.append(ph[1])
    return ''.join(out)


def transcribe_en(text, precise=True, mode='hangul'):
    """English → Hangul. CMU phoneme based.

    Returns:
      hangul: 음절 합성 (사람 읽기)
      jamo:   UHPS jamo sequence (ML)
      spaced: spaced jamo
    """
    parts = re.split(r'(\s+|[^\w\']+)', text)
    out = []
    for part in parts:
        if not part: continue
        if not re.match(r"^[A-Za-z']+$", part):
            out.append(part); continue
        phs = get_phonemes(part)
        if phs is None:
            out.append(f'[?{part}]')  # not in dict
            continue
        ph_tuples = _phonemize_arpabet(phs, precise)
        if mode == 'hangul':
            out.append(_assemble(ph_tuples, precise))
        elif mode == 'jamo':
            out.append(_to_jamo_seq(ph_tuples))
        elif mode == 'spaced':
            out.append(' '.join(_to_jamo_seq(ph_tuples)))
        else:
            raise ValueError(f"Unknown mode: {mode}")
    return ''.join(out)


# === Test ===
if __name__ == '__main__':
    print(f'Essential dict: {len(ESSENTIAL_CMU)} words')
    print(f'External CMU loaded: {len(_EXT_CMU)} words')
    print()
    print('=== Minimal pair tests ===')
    pairs = [
        ('think', 'sin'),       # /θ/ vs /s/
        ('this', 'sis'),        # /ð/ vs /s/
        ('vine', 'bine'),       # /v/ vs /b/
        ('fast', 'past'),       # /f/ vs /p/
        ('zoo', 'sue'),         # /z/ vs /s/
        ('red', 'led'),         # /ɹ/ vs /l/
        ('right', 'light'),
        ('vision', 'measure'),  # /ʒ/
    ]
    for a, b in pairs:
        ja = transcribe_en(a, mode='jamo', precise=True)
        jb = transcribe_en(b, mode='jamo', precise=True)
        ha = transcribe_en(a, mode='hangul', precise=True)
        hb = transcribe_en(b, mode='hangul', precise=True)
        same = '✗ collision!' if ja == jb else '✓ distinct'
        print(f'  {a:<10} jamo={ja:<14} hangul={ha:<10} | {b:<10} jamo={jb:<14} hangul={hb:<10} | {same}')

    print()
    print('=== Sample words ===')
    samples = ['hello', 'world', 'student', 'teacher', 'computer', 'family', 'happy',
               'father', 'mother', 'water', 'apple', 'orange', 'pizza', 'coffee',
               'Boston', 'Paris', 'London', 'Christmas']
    for w in samples:
        h = transcribe_en(w, mode='hangul', precise=True)
        j = transcribe_en(w, mode='jamo', precise=True)
        hb = transcribe_en(w, mode='hangul', precise=False)
        print(f'  {w:<14} precise={h:<14} basic={hb:<14} jamo={j}')
