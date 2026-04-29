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
    'ER': 'ㅓ',   # bird (버) — Korean Loanword: 어말 R 미실현
    'EY': ('ㅔ', 'ㅣ'),  # day
    'IH': 'ㅣ',   # bit
    'IY': 'ㅣ',   # bee
    'OW': 'ㅗ',   # go (단순화 — Korean: phone→폰, no→노)
    'OY': ('ㅗ', 'ㅣ'),  # boy
    'UH': 'ㅜ',   # book
    'UW': 'ㅜ',   # boot
}

# 긴 모음 / 이중모음 — 어말 K/T/P 받침 룰 차단용
_LONG_VOWELS = {'IY','UW','AY','AW','EY','OW','OY','ER'}

# Y/W + vowel → palatal/W vowel
Y_VOWEL = {'AA':'ㅑ','AE':'ㅒ','AH':'ㅑ','AO':'ㅛ','EH':'ㅖ','IH':'ㅣ','IY':'ㅣ','UH':'ㅠ','UW':'ㅠ'}
W_VOWEL = {'AA':'ㅘ','AE':'ㅙ','AH':'ㅝ','AO':'ㅝ','EH':'ㅞ','ER':'ㅝ','IH':'ㅟ','IY':'ㅟ','UH':'ㅜ','UW':'ㅜ'}


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
    'tube': ['T','UW','B'],
    'duke': ['D','UW','K'],
    'duty': ['D','UW','T','IY'],
    'tune': ['T','UW','N'],
    'tuna': ['T','UW','N','AH'],
    'news': ['N','UW','Z'],
    'super': ['S','Y','UW','P','ER'],   # 슈퍼 (Korean convention)
    'suit': ['S','Y','UW','T'],          # 슈트
    'soon': ['S','UW','N'],
    # Common nouns
    'bird': ['B','ER','D'],
    'her': ['HH','ER'],
    'him': ['HH','IH','M'],
    'hard': ['HH','AA','R','D'],
    'card': ['K','AA','R','D'],
    'star': ['S','T','AA','R'],
    'far': ['F','AA','R'],
    'car': ['K','AA','R'],
    'back': ['B','AE','K'],
    'park': ['P','AA','R','K'],
    'rock': ['R','AA','K'],
    'hand': ['HH','AE','N','D'],
    'face': ['F','EY','S'],
    'eye': ['AY'],
    'man': ['M','AE','N'],
    'woman': ['W','UH','M','AH','N'],
    'boy': ['B','OY'],
    'girl': ['G','ER','L'],
    'cup': ['K','AH','P'],
    'box': ['B','AA','K','S'],
    'door': ['D','AO','R'],
    'window': ['W','IH','N','D','OW'],
    'street': ['S','T','R','IY','T'],
    'money': ['M','AH','N','IY'],
    'baby': ['B','EY','B','IY'],
    'name': ['N','EY','M'],
    'game': ['G','EY','M'],
    'movie': ['M','UW','V','IY'],
    'office': ['AO','F','AH','S'],
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


# === Hangul overrides (NIKL 외래어 표기 conventions) ===
# B로 못 잡는 word-specific irregularities — 직접 Hangul 매핑
_HANGUL_OVERRIDES = {
    # AH schwa ambiguity
    'hello': '헬로',
    'mother': '마더',
    'brother': '브라더',
    'sister': '시스터',
    'father': '파더',
    'water': '워터',
    'system': '시스템',
    'item': '아이템',
    # AE/AA - ㅏ vs ㅐ vs ㅗ
    'camera': '카메라',
    'animal': '애니멀',
    'pencil': '펜슬',
    'about': '어바웃',
    'around': '어라운드',
    'america': '아메리카',
    # AA from 'o' - ㅏ 케이스 (default ㅗ override 풀림)
    'hot': '핫',
    'box': '박스',
    'god': '갓',
    'doctor': '닥터',
    'pop': '팝',
    'rock': '록',
    'lock': '락',
    'stock': '스톡',
    'mom': '맘',
    'dad': '대드',
    # K/T 코다 vs 으-suff
    'park': '파크',
    'work': '워크',
    'walk': '워크',
    'talk': '토크',
    'cake': '케이크',
    # OW + N
    'phone': '폰',
    'home': '홈',
    'note': '노트',
    'flag': '플래그',
    # 일반 brand/tech (CMU에 있어도 컨벤션)
    'google': '구글',
    'apple': '애플',
    'amazon': '아마존',
    'samsung': '삼성',
    'microsoft': '마이크로소프트',
    'youtube': '유튜브',
    'twitter': '트위터',
    'facebook': '페이스북',
    'netflix': '넷플릭스',
    'instagram': '인스타그램',
    'spotify': '스포티파이',
    'github': '깃허브',
    'firebase': '파이어베이스',
    'whatsapp': '왓츠앱',
    'upload': '업로드',
    'download': '다운로드',
    'online': '온라인',
    # 일반 단어
    'shop': '숍',
    'shoe': '슈',
    'show': '쇼',
    'shake': '셰이크',
    'name': '네임',
    'game': '게임',
    'time': '타임',
    'love': '러브',
    'good': '굿',
    'cool': '쿨',
    'new': '뉴',
    'old': '올드',
    'fast': '패스트',
    'slow': '슬로우',
    'tea': '티',
    'coffee': '커피',
    'pizza': '피자',
    'salad': '샐러드',
    'milk': '밀크',
    'bread': '브레드',
    'bus': '버스',
    'car': '카',
    'taxi': '택시',
    'train': '트레인',
    'plane': '플레인',
    'doctor': '닥터',
    'student': '스튜던트',
    'teacher': '티처',
    'computer': '컴퓨터',
    # === NIKL 외래어 표기 — places ===
    'seoul': '서울',
    'tokyo': '도쿄',
    'osaka': '오사카',
    'kyoto': '교토',
    'beijing': '베이징',
    'shanghai': '상하이',
    'paris': '파리',
    'london': '런던',
    'berlin': '베를린',
    'rome': '로마',
    'madrid': '마드리드',
    'moscow': '모스크바',
    'boston': '보스턴',
    'chicago': '시카고',
    'dallas': '댈러스',
    'miami': '마이애미',
    'sydney': '시드니',
    'melbourne': '멜버른',
    'vancouver': '밴쿠버',
    'toronto': '토론토',
    'america': '아메리카',
    'korea': '코리아',
    'japan': '재팬',
    'china': '차이나',
    'russia': '러시아',
    'canada': '캐나다',
    'mexico': '멕시코',
    'brazil': '브라질',
    'italy': '이탈리아',
    'spain': '스페인',
    'germany': '독일',  # Korean prefers 독일 over 저머니
    'france': '프랑스',
    'india': '인도',
    'thailand': '태국',
    'vietnam': '베트남',
    'singapore': '싱가포르',
    'philippines': '필리핀',
    # === Common foods (NIKL 표기) ===
    'orange': '오렌지',
    'banana': '바나나',
    'strawberry': '스트로베리',
    'chocolate': '초콜릿',
    'sandwich': '샌드위치',
    'pasta': '파스타',
    'sugar': '슈거',
    'egg': '에그',
    'fish': '피시',
    'meat': '미트',
    'rice': '라이스',
    'soup': '수프',
    'cake': '케이크',
    'cookie': '쿠키',
    'candy': '캔디',
    'tea': '티',
    'coffee': '커피',
    'milk': '밀크',
    'water': '워터',
    'bread': '브레드',
    'cheese': '치즈',
    # === Tech/business terms ===
    'monitor': '모니터',
    'software': '소프트웨어',
    'hardware': '하드웨어',
    'website': '웹사이트',
    'internet': '인터넷',
    'email': '이메일',
    'laptop': '랩톱',
    'keyboard': '키보드',
    'mouse': '마우스',
    'click': '클릭',
    'video': '비디오',
    'audio': '오디오',
    'photo': '포토',
    'data': '데이터',
    'server': '서버',
    'database': '데이터베이스',
    # === Brand/proper nouns ===
    'nvidia': '엔비디아',
    'toyota': '도요타',
    'honda': '혼다',
    'adidas': '아디다스',
    'coca': '코카',
    'pepsi': '펩시',
    'starbucks': '스타벅스',
    'mcdonald': '맥도날드',
    'burger': '버거',
    'shakespeare': '셰익스피어',
    'einstein': '아인슈타인',
    'mozart': '모차르트',
    'beethoven': '베토벤',
    'newton': '뉴턴',
    'edison': '에디슨',
    # === Misc ===
    'birthday': '버스데이',
    'weekend': '위크엔드',
    'basketball': '농구',  # actually 농구 is preferred Korean
    'football': '풋볼',
    'baseball': '야구',
    'happy': '해피',
    'love': '러브',
    'song': '송',
    'dance': '댄스',
    'music': '뮤직',
    'movie': '무비',
    'pop': '팝',
    'come': '컴',
    'button': '버튼',
    'biden': '바이든',
    'echo': '에코',
    'hero': '히어로',
    'logo': '로고',
    'photo': '포토',
    'piano': '피아노',
}


# === Acronym handler (letter-by-letter Korean naming) ===
# 영문자 한국식 이름 (외래어 표기 관행)
_LETTER_NAMES = {
    'a': '에이', 'b': '비',   'c': '씨',   'd': '디',   'e': '이',
    'f': '에프', 'g': '지',   'h': '에이치', 'i': '아이', 'j': '제이',
    'k': '케이', 'l': '엘',   'm': '엠',   'n': '엔',   'o': '오',
    'p': '피',   'q': '큐',   'r': '알',   's': '에스', 't': '티',
    'u': '유',   'v': '브이', 'w': '더블유', 'x': '엑스', 'y': '와이',
    'z': '제트',
}

# Letter → ARPABET (jamo 모드용)
_LETTER_ARPABET = {
    'a': ['EY'],          'b': ['B','IY'],     'c': ['S','IY'],
    'd': ['D','IY'],      'e': ['IY'],         'f': ['EH','F'],
    'g': ['JH','IY'],     'h': ['EY','CH'],    'i': ['AY'],
    'j': ['JH','EY'],     'k': ['K','EY'],     'l': ['EH','L'],
    'm': ['EH','M'],      'n': ['EH','N'],     'o': ['OW'],
    'p': ['P','IY'],      'q': ['K','Y','UW'], 'r': ['AA','R'],
    's': ['EH','S'],      't': ['T','IY'],     'u': ['Y','UW'],
    'v': ['V','IY'],      'w': ['D','AH','B','AH','L','Y','UW'],
    'x': ['EH','K','S'],  'y': ['W','AY'],     'z': ['Z','IY'],
}


def _is_acronym(original_word):
    """대문자 짧은 약어 또는 모음 없는 토큰 감지."""
    w = original_word
    # 1) 원래 입력이 대문자 (≤5자) — USA, FBI, AI, LSTM
    if 2 <= len(w) <= 5 and w.isalpha() and w.isupper():
        return True
    # 2) lowercase여도 모음이 전혀 없는 토큰 — lstm, fbi, kpop은 X (kpop has vowels actually)
    wl = w.lower()
    if 2 <= len(wl) <= 5 and wl.isalpha() and not any(c in 'aeiouy' for c in wl):
        return True
    return False


def _acronym_phonemes(word):
    """letter-by-letter ARPABET (alphabet 이름)."""
    out = []
    for ch in word.lower():
        if ch in _LETTER_ARPABET:
            out.extend(_LETTER_ARPABET[ch])
    return out


# === Compound word decomposer ===
# 합성어 (firebase, smartphone, typescript, instagram) → 부분 lookup
# greedy: 가능한 가장 긴 prefix가 CMU에 있으면 split
def _compound_split(word):
    """word → [w1, w2, ...] where each part is in CMU. None if no split found."""
    w = word.lower()
    if len(w) < 6:
        return None  # 너무 짧으면 split 안 함
    # Try splitting at each position from longest prefix
    n = len(w)
    for split_at in range(n - 2, 2, -1):
        prefix = w[:split_at]
        suffix = w[split_at:]
        # Both must be in CMU and at least 3 chars
        if len(prefix) >= 3 and len(suffix) >= 3:
            if get_phonemes(prefix) and get_phonemes(suffix):
                return [prefix, suffix]
    # 3-way split (instagram = insta + gram, but also try i + n + s + t...)
    for s1 in range(n - 4, 2, -1):
        for s2 in range(s1 + 3, n - 2):
            p1, p2, p3 = w[:s1], w[s1:s2], w[s2:]
            if (len(p1) >= 3 and len(p2) >= 3 and len(p3) >= 3
                    and get_phonemes(p1) and get_phonemes(p2) and get_phonemes(p3)):
                return [p1, p2, p3]
    return None


def _compound_phonemes(word):
    """word → ARPABET via compound split. None if can't split."""
    parts = _compound_split(word)
    if not parts:
        return None
    out = []
    for p in parts:
        phs = get_phonemes(p)
        if not phs:
            return None
        out.extend(phs)
    return out


# === Phonics fallback (letter-cluster → ARPABET 근사) ===
# CMU lookup 실패 시 사용. "rough but mostly right" 정책.
# 다자모 패턴 우선 (longest-match), 단일 자모 default.
_PHONICS_CLUSTERS = [
    # 4-char
    ('tion', ['SH','AH','N']),
    ('sion', ['ZH','AH','N']),
    ('ough', ['AO']),
    ('augh', ['AO']),
    # 3-char
    ('eau',  ['OW']),
    ('igh',  ['AY']),
    ('tch',  ['CH']),
    ('dge',  ['JH']),
    ('air',  ['EH','R']),
    ('ear',  ['IH','R']),
    ('eer',  ['IH','R']),
    ('our',  ['AW','R']),
    # 2-char vowels
    ('ee',   ['IY']),
    ('ea',   ['IY']),
    ('ai',   ['EY']),
    ('ay',   ['EY']),
    ('ie',   ['AY']),
    ('ei',   ['EY']),
    ('ey',   ['EY']),
    ('oo',   ['UW']),
    ('oa',   ['OW']),
    ('oi',   ['OY']),
    ('oy',   ['OY']),
    ('ou',   ['AW']),
    ('ow',   ['OW']),
    ('au',   ['AO']),
    ('aw',   ['AO']),
    ('eu',   ['Y','UW']),
    ('ew',   ['Y','UW']),
    ('ue',   ['Y','UW']),
    ('ui',   ['UW']),
    # r-controlled
    ('ar',   ['AA','R']),
    ('er',   ['ER']),
    ('ir',   ['ER']),
    ('or',   ['AO','R']),
    ('ur',   ['ER']),
    # 2-char consonants
    ('ph',   ['F']),
    ('ck',   ['K']),
    ('sh',   ['SH']),
    ('ch',   ['CH']),
    ('th',   ['TH']),
    ('ng',   ['NG']),
    ('qu',   ['K','W']),
    ('wh',   ['W']),
    ('gh',   []),       # silent
    ('kn',   ['N']),    # silent k
    ('wr',   ['R']),    # silent w
    ('ps',   ['S']),    # silent p (psychology)
    ('mb',   ['M']),    # silent b at end
]
# soft c/g before i,e,y
_SOFT_C = {'i', 'e', 'y'}
_SINGLE = {
    'a': ['AE'], 'e': ['EH'], 'i': ['IH'], 'o': ['AA'], 'u': ['AH'],
    'b': ['B'], 'c': ['K'], 'd': ['D'], 'f': ['F'], 'g': ['G'],
    'h': ['HH'], 'j': ['JH'], 'k': ['K'], 'l': ['L'], 'm': ['M'],
    'n': ['N'], 'p': ['P'], 'r': ['R'], 's': ['S'], 't': ['T'],
    'v': ['V'], 'w': ['W'], 'x': ['K','S'], 'y': ['IH'], 'z': ['Z'],
}
_VOWEL_LETTERS = set('aeiouy')


def _phonics_fallback(word):
    """word → ARPABET 근사 (greedy longest-match)."""
    w = word.lower()
    # silent-e: 어말 e가 단어 끝에 있고 그 앞이 자음+모음+자음 패턴이면 drop
    # (긴-모음 효과는 단순화: 그냥 마지막 e만 drop)
    if len(w) >= 4 and w.endswith('e') and w[-2] not in _VOWEL_LETTERS and w[-3] in _VOWEL_LETTERS:
        # keep last e in 'ee', 'oe', 'ie' patterns — handled by clusters above
        # also drop only when not part of a digraph
        if w[-2:] not in {'le','re','ne','se','te','de','ke','ve','me','pe','be','ge','ce','fe','ze'} or len(w) > 3:
            # heuristic: most CVCe patterns silent-e (name, like, hope)
            # but keep for "le" since often syllabic (apple, table)
            if w[-2:] != 'le':
                w = w[:-1]
    out = []
    i = 0
    n = len(w)
    while i < n:
        # cluster match (longest first since list is ordered)
        matched = False
        for pat, phs in _PHONICS_CLUSTERS:
            if w.startswith(pat, i):
                out.extend(phs)
                i += len(pat)
                matched = True
                break
        if matched:
            continue
        ch = w[i]
        nxt = w[i+1] if i+1 < n else ''
        # soft c (before i/e/y)
        if ch == 'c' and nxt in _SOFT_C:
            out.append('S')
            i += 1; continue
        # soft g (before i/e/y) - 'JH' (gentle, gym)
        if ch == 'g' and nxt in _SOFT_C:
            out.append('JH')
            i += 1; continue
        # y as initial consonant
        if ch == 'y' and i == 0 and nxt in _VOWEL_LETTERS:
            out.append('Y')
            i += 1; continue
        # final y after consonant → IY (happy, baby)
        if ch == 'y' and i == n-1 and i > 0 and w[i-1] not in _VOWEL_LETTERS:
            out.append('IY')
            i += 1; continue
        # double consonant collapse
        if ch == nxt and ch not in _VOWEL_LETTERS and ch in _SINGLE:
            out.extend(_SINGLE[ch])
            i += 2; continue
        # default
        if ch in _SINGLE:
            out.extend(_SINGLE[ch])
        i += 1
    return out


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


# === Letter-aligned phonemes (spelling-aware vowel disambiguation) ===
# 각 ARPABET phoneme이 spelling의 어느 letter cluster에서 왔는지 추적
# → AH/ER/AA 같은 모호한 모음을 source letter로 분기
_PHONEME_LETTER_PATTERNS = {
    # consonants
    'HH': ['h'],
    'B': ['bb', 'b'],
    'D': ['dd', 'd'],
    'F': ['ph', 'gh', 'ff', 'f'],
    'G': ['gg', 'gh', 'g'],
    'JH': ['dge', 'dg', 'j', 'g'],
    'K': ['ck', 'que', 'cqu', 'cc', 'cq', 'ke', 'ch', 'k', 'c', 'q'],
    'L': ['ll', 'l'],
    'M': ['mb', 'mm', 'm'],
    'N': ['nn', 'kn', 'gn', 'pn', 'n'],
    'NG': ['ng', 'n'],
    'P': ['pp', 'p'],
    'R': ['rr', 'wr', 'r'],
    'S': ['ss', 'ce', 'ci', 'cy', 'sc', 'ps', 's', 'c'],
    'SH': ['ssi', 'ss', 'ti', 'ci', 'sh', 'ch', 's'],
    'T': ['tt', 'ed', 'pt', 't'],
    'TH': ['th'],
    'V': ['vv', 'v', 'f'],
    'W': ['wh', 'w', 'u'],
    'Y': ['y', 'j', 'i'],
    'Z': ['zz', 'z', 'ss', 's', 'x'],
    'ZH': ['si', 'ssi', 'ge', 's', 'z'],
    'CH': ['tch', 'ch', 't', 'c'],
    # vowels
    'AA': ['a', 'o', 'au', 'aa', 'ah'],
    'AE': ['a', 'aa'],
    'AH': ['ou', 'ea', 'a', 'e', 'i', 'o', 'u', 'y'],
    'AO': ['augh', 'ough', 'aw', 'au', 'oa', 'a', 'o'],
    'AW': ['ough', 'ow', 'ou'],
    'AY': ['eye', 'igh', 'uy', 'ai', 'ie', 'ye', 'i', 'y'],
    'EH': ['ea', 'ai', 'a', 'e'],
    'ER': ['ear', 'eur', 'er', 'ir', 'or', 'ur', 'yr', 'ar'],
    'EY': ['eigh', 'ai', 'ay', 'ei', 'ey', 'a', 'e'],
    'IH': ['e', 'ee', 'i', 'y', 'u', 'o'],
    'IY': ['ee', 'ea', 'ei', 'ey', 'ie', 'i', 'e', 'y'],
    'OW': ['eau', 'ough', 'oa', 'oe', 'ow', 'o'],
    'OY': ['oi', 'oy'],
    'UH': ['oo', 'ou', 'u', 'o'],
    'UW': ['iew', 'eu', 'ew', 'ou', 'ue', 'oo', 'u', 'o'],
}

_VOWEL_LETTER_SET = set('aeiouy')


def _align_phonemes(word, phs):
    """phoneme[i] → source letter cluster (또는 '')."""
    word = word.lower()
    aligned = [''] * len(phs)
    si = 0
    n = len(word)
    for pi, p in enumerate(phs):
        patterns = _PHONEME_LETTER_PATTERNS.get(p, [])
        # try with up to 2 silent letters skipped
        matched = False
        for skip in range(0, 3):
            for pat in patterns:
                if word[si + skip:si + skip + len(pat)] == pat:
                    aligned[pi] = pat
                    si = si + skip + len(pat)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            # heuristic: advance si by 1 to keep moving
            if si < n:
                si += 1
    return aligned


# === Yod insertion (Korean 외래어 표기 convention) ===
# T/D/N + UW → T/D/N + Y + UW (영국식 yod 살림 — 미국식 CMU에서 떨어진 /j/ 복원)
# 표기 일람표: tube → 튜브, duty → 듀티, news → 뉴스, student → 스튜던트
_YOD_TARGETS = {'T', 'D', 'N'}
# 예외: 어원적으로 yod 없는 단어 (외래어 표기법도 yod 없이 적음)
_YOD_LESS_WORDS = {
    'two', 'to', 'too',
    'do', 'doom', 'doodle',
    'noon', 'noodle',
    'tomb', 'womb',
    # S+UW는 yod 대상 아님 (default ㅜ). suit/super 같은 yod 단어는 사전에 Y 명시
}


def _spelling_resolve_er(phs, aligned):
    """ER + 특정 spelling → V + R 분리.
    'or' → AO + R (history → 히스토리)
    'ar' → AA + R (rare, e.g., 'liar')
    'er'/'ir'/'ur'/'ear' → ER 그대로 (ㅓ default)
    """
    out_phs, out_aln = [], []
    for p, src in zip(phs, aligned):
        if p == 'ER' and src == 'or':
            out_phs.extend(['AO', 'R']); out_aln.extend(['o', 'r'])
        elif p == 'ER' and src == 'ar':
            out_phs.extend(['AA', 'R']); out_aln.extend(['a', 'r'])
        else:
            out_phs.append(p); out_aln.append(src)
    return out_phs, out_aln


def _yod_insert(phs, aligned, word):
    """치경음(T/D/N) + UW 사이에 Y 삽입. 단, 예외 단어 제외."""
    if word.lower() in _YOD_LESS_WORDS:
        return phs, aligned
    out_phs = []
    out_aln = []
    i = 0
    while i < len(phs):
        out_phs.append(phs[i])
        out_aln.append(aligned[i])
        nxt = phs[i+1] if i+1 < len(phs) else ''
        if phs[i] in _YOD_TARGETS and nxt == 'UW':
            out_phs.append('Y'); out_aln.append('')
        i += 1
    return out_phs, out_aln


# Postvocalic R drop (Korean Loanword 표기법):
#   vowel + R + (consonant|end) → vowel + ... (R 미실현)
#   예: car → 카, hard → 하드, sister → 시스터
# 유지: 어두 R (red), 모음+R+모음 (very), 자음+R 클러스터 (three)
_VOWEL_PHS = {'AA','AE','AH','AO','AW','AY','EH','ER','EY','IH','IY','OW','OY','UH','UW'}


def _drop_postvocalic_r(phs, aligned):
    out_phs, out_aln = [], []
    i = 0
    n = len(phs)
    while i < n:
        p = phs[i]
        prev = phs[i-1] if i > 0 else ''
        nxt = phs[i+1] if i+1 < n else ''
        if p == 'R' and prev in _VOWEL_PHS and nxt not in _VOWEL_PHS:
            i += 1
            continue
        out_phs.append(p); out_aln.append(aligned[i])
        i += 1
    return out_phs, out_aln


def _expand_er_before_vowel(phs, aligned):
    """ER + 모음 → ER + R + 모음. (ER 안의 /ɚ/는 다음 모음 앞에서 ㄹ로 살아남음.)
    예: gallery /ˈɡæl.ər.i/ → 갤러리 — 'ery' 패턴.
    """
    out_phs, out_aln = [], []
    n = len(phs)
    for i, p in enumerate(phs):
        out_phs.append(p); out_aln.append(aligned[i])
        if p == 'ER' and i+1 < n and phs[i+1] in _VOWEL_PHS:
            out_phs.append('R'); out_aln.append('')
    return out_phs, out_aln


_SONORANT_BLOCK = {'N', 'M', 'NG', 'R', 'L', 'Y', 'W'}  # 이미 jong이 되는 자음들


def _double_intervocalic_l(phs, aligned):
    """L 중복 (Korean Loanword 'ㄹㄹ'):
    - V + L + V (hello → 헬로, silly → 실리)
    - 자음 + L + V (어두 cluster: blue → 블루, block → 블록)
    단, 앞이 sonorant이면 (N/M/R/L) 이미 받침이 되므로 doubling 안 함:
    - online (N+L+V) → 온라인 (NOT 온르라인)
    """
    out_phs, out_aln = [], []
    i = 0
    n = len(phs)
    while i < n:
        p = phs[i]
        out_phs.append(p); out_aln.append(aligned[i])
        if p == 'L' and i > 0 and i+1 < n:
            nxt = phs[i+1]
            prev = phs[i-1]
            if nxt in _VOWEL_PHS and prev not in _SONORANT_BLOCK:
                out_phs.append('L'); out_aln.append('')
        i += 1
    return out_phs, out_aln


# Spelling-aware vowel override: (phoneme, source_letter_cluster) → 자모
# 보수적 — AH 같은 schwa는 word마다 conventionally 다르므로 override list로
_VOWEL_SPELLING = {
    ('AA', 'o'): 'ㅗ',         # rock → 록, top → 톱, drop → 드롭
    ('AO', 'a'): 'ㅗ',         # call → 콜
}

# 어말 위치에서만 적용되는 spelling-aware override
# (위치 기반이므로 phonemize에서 별도 처리)
_VOWEL_SPELLING_FINAL = {
    ('AH', 'a'): 'ㅏ',  # banana → 바나나, china → 차이나, korea → 코리아
    # 'AH' from 'o' final는 충돌 (echo→에코 vs come→컴) — override list로 처리
}


# === Phonemize: ARPABET list → phoneme tuple list (UHPS) ===
def _phonemize_arpabet(phs, precise, aligned=None):
    """ARPABET list → UHPS phoneme tuple list. aligned: 각 phoneme의 source letter."""
    cmap = CONSONANTS if precise else CONSONANTS_BASIC
    if aligned is None:
        aligned = [''] * len(phs)
    out = []
    i = 0
    n = len(phs)
    while i < n:
        p = phs[i]
        nxt = phs[i+1] if i+1 < n else ''
        aln = aligned[i] if i < len(aligned) else ''
        # Y + V → palatal
        # 앞에 자음이 free로 떠 있으면 ㅇ 더미 생략 (자음이 ㅠ 흡수 → 퓨, 뮤, 듀)
        if p == 'Y' and nxt in Y_VOWEL:
            if out and out[-1][0] == 'C' and out[-1][1] != 'ㅇ':
                out.append(('SV', Y_VOWEL[nxt]))
            else:
                out.append(('C', 'ㅇ', 'y'))
                out.append(('SV', Y_VOWEL[nxt]))
            i += 2; continue
        # W + V → W vowel
        # K+W만 merge (퀸, 퀵). 다른 자음 뒤 W는 분리 (twin → 트윈, software → 소프트웨어).
        if p == 'W' and nxt in W_VOWEL:
            if out and out[-1][0] == 'C' and len(out[-1]) > 2 and out[-1][2] in ('k', 'g'):
                out.append(('SV', W_VOWEL[nxt]))
            else:
                out.append(('C', 'ㅇ', 'w'))
                out.append(('SV', W_VOWEL[nxt]))
            i += 2; continue
        # SH + V → 팔라탈화 (Korean: shoe→슈, show→쇼, shop→숍, sugar→슈거)
        # CH/JH/ZH는 modern Korean에서 챠/쟈 안 씀 → 그냥 ㅊ/ㅈ + base 모음 사용
        if p == 'SH' and (nxt in Y_VOWEL or nxt == 'ER'):
            jamo = cmap.get('SH', 'ㅅ')
            out.append(('C', jamo, 'sh'))
            if nxt == 'ER':
                out.append(('SV', 'ㅕ'))
            else:
                out.append(('SV', Y_VOWEL[nxt]))
            i += 2; continue
        # Vowel
        if p in VOWELS:
            v = VOWELS[p]
            is_long = p in _LONG_VOWELS
            # spelling-aware 단모음 override (diphthong 제외)
            if not isinstance(v, tuple):
                override = _VOWEL_SPELLING.get((p, aln))
                if override is not None:
                    v = override
                # 어말 위치 (이후 더 이상 모음 없음) — 추가 override
                # banana/china/korea 등의 final-a 케이스
                else:
                    is_final_vowel = not any(
                        phs[k] in _VOWEL_PHS for k in range(i+1, n)
                    )
                    if is_final_vowel:
                        f_override = _VOWEL_SPELLING_FINAL.get((p, aln))
                        if f_override is not None:
                            v = f_override
            if isinstance(v, tuple):
                # 이중모음: 첫 V는 long. 두 번째 V는 phoneme별로 다름.
                # AW (ㅏㅜ) — 두 번째 ㅜ는 short (about → 어바웃, out → 아웃 — T 코다)
                # AY/EY/OY (-ㅣ로 끝) — 두 번째 ㅣ는 long (light → 라이트, no coda)
                second_long = p != 'AW'
                out.append(('V', v[0], True))
                out.append(('V', v[1], True) if second_long else ('V', v[1]))
            else:
                out.append(('V', v, is_long) if is_long else ('V', v))
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


def _is_long(ph):
    """V/SV tuple이 long 마킹인지."""
    return len(ph) > 2 and ph[-1] is True


# K/T/P 코다 가능한 jung — ㅡ(충전)와 long-marked만 차단.
# 합성모음 (ㅘ ㅙ ㅚ ㅝ ㅞ ㅟ ㅢ)도 받침 가능 (퀵, 윈, 워드 등)
_REAL_SHORT_JUNG = {
    'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ',
    'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ',
    'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅣ', 'ㅢ',
}  # ㅡ 제외


def _last_jung(syllables):
    """마지막 음절의 중성 자모. 없으면 None."""
    if not syllables: return None
    s = syllables[-1]
    if len(s) != 1: return None
    c = ord(s)
    if not (0xAC00 <= c <= 0xD7A3): return None
    base = c - HANGUL_BASE
    return VOWELS_J[(base % 588) // 28]


def _assemble(phonemes, precise):
    syllables = []
    syll_long = []   # parallel: 각 syllable이 long-vowel 기반인지
    i = 0
    n = len(phonemes)
    while i < n:
        ph = phonemes[i]
        kind = ph[0]
        if kind in ('V', 'SV'):
            syllables.append(_compose('ㅇ', ph[1]))
            syll_long.append(_is_long(ph))
            i += 1; continue
        if kind == 'OLD':
            old = ph[1]
            if _next_is_vowel(phonemes, i):
                syllables.append(old)
                syll_long.append(False)  # OLD jamo (sole)
                syllables.append(_compose('ㅇ', phonemes[i+1][1]))
                syll_long.append(_is_long(phonemes[i+1]))
                i += 2
            else:
                syllables.append(old); syll_long.append(False); i += 1
            continue
        if kind == 'C':
            cho = ph[1]; src = ph[2] if len(ph) > 2 else ''
            if _next_is_vowel(phonemes, i):
                syllables.append(_compose(cho, phonemes[i+1][1]))
                syll_long.append(_is_long(phonemes[i+1]))
                i += 2
                continue
            # 어말/자음 앞
            last_is_long = bool(syll_long and syll_long[-1])
            last_jung = _last_jung(syllables)
            real_short = (last_jung in _REAL_SHORT_JUNG) and not last_is_long
            if cho in ALLOW_AS_FINAL and not (syllables and _has_jong(syllables[-1])):
                if _add_jong_to_last(syllables, cho):
                    i += 1; continue
            # k/t/p/g/b 어말 받침: 진짜 짧은 모음 뒤에서만
            # Korean Loanword: k/g→ㄱ (back, big), t→ㅅ (cat), p/b→ㅂ (cap, cab).
            # D는 보통 으-suffix (bed→베드), 그래서 d 제외.
            if real_short and syllables and not _has_jong(syllables[-1]):
                if src in ('k', 'g'):
                    if _add_jong_to_last(syllables, 'ㄱ'): i += 1; continue
                if src == 't':
                    if _add_jong_to_last(syllables, 'ㅅ'): i += 1; continue
                if src in ('p', 'b'):
                    if _add_jong_to_last(syllables, 'ㅂ'): i += 1; continue
            # 그 외 → 으-syll
            syllables.append(_compose(cho, 'ㅡ'))
            syll_long.append(False)
            i += 1
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
        # 0a. Hangul direct override (NIKL conventions; hangul mode only)
        if mode == 'hangul' and part.lower() in _HANGUL_OVERRIDES:
            out.append(_HANGUL_OVERRIDES[part.lower()])
            continue
        # 0b. acronym 감지 (letter-by-letter, 각 letter 독립 변환)
        if _is_acronym(part):
            if mode == 'hangul':
                out.append(''.join(_LETTER_NAMES[c] for c in part.lower() if c in _LETTER_NAMES))
                continue
            else:
                # jamo/spaced 모드: letter별 독립 phonemize 후 합침
                pieces = []
                for c in part.lower():
                    if c not in _LETTER_ARPABET:
                        continue
                    lphs = _LETTER_ARPABET[c]
                    lphs = _drop_postvocalic_r(lphs)
                    lt = _phonemize_arpabet(lphs, precise)
                    pieces.append(_to_jamo_seq(lt))
                joined = ''.join(pieces)
                out.append(' '.join(joined) if mode == 'spaced' else joined)
                continue
        phs = get_phonemes(part)
        if phs is None:
            # 1. compound decomposer (firebase → fire+base)
            phs = _compound_phonemes(part)
        if phs is None:
            # 2. phonics fallback
            phs = _phonics_fallback(part)
            if not phs:
                out.append(f'[?{part}]')
                continue
        # Letter alignment (CMU phs vs spelling)
        aligned = _align_phonemes(part, phs)
        phs, aligned = _spelling_resolve_er(phs, aligned)
        phs, aligned = _yod_insert(phs, aligned, part)
        phs, aligned = _expand_er_before_vowel(phs, aligned)
        phs, aligned = _drop_postvocalic_r(phs, aligned)
        phs, aligned = _double_intervocalic_l(phs, aligned)
        ph_tuples = _phonemize_arpabet(phs, precise, aligned)
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
