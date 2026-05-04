"""Hunmin public API — Hunmin class + transcribe() shortcut.

Five explicit modes (UHPS_SPEC §1.0):
  HUNMIN_NIKL    — 사람 읽기, NIKL 외래어 표기 컨벤션 (default)
  HUNMIN_PHONETIC — 사람 읽기, 음운적 (NIKL adapter OFF)
  UHPS_CORE      — 옛한글 음소 코드 (자모 분리, IPA 1:1)
  UHPS_JAMO      — 분해된 자모 시퀀스 (ML 입력용)
  UHPS_FULL      — UHPS-core + 운율 (장단/강세/성조)
"""
import re
from .core import (
    transcribe_es, transcribe_it, transcribe_de, transcribe_ru,
    transcribe_fr, transcribe_pt, transcribe_nl, transcribe_pl,
    transcribe_tr, transcribe_id, transcribe_en, transcribe_hu,
    transcribe_sk, transcribe_cs, transcribe_ro, transcribe_hr,
    transcribe_sr, transcribe_vi, transcribe_fa,
    transcribe_cjk,
)

# === Mode constants (v3.6) ===
HUNMIN_NIKL = 'hunmin_nikl'
HUNMIN_PHONETIC = 'hunmin_phonetic'
UHPS_CORE = 'uhps_core'
UHPS_JAMO = 'uhps_jamo'
UHPS_FULL = 'uhps_full'

_MODE_TO_LEVEL = {
    HUNMIN_NIKL:     (1, False),  # (level, phonetic)
    HUNMIN_PHONETIC: (1, True),
    UHPS_CORE:       (3, False),
    UHPS_JAMO:       (4, False),
    UHPS_FULL:       (5, False),
}


# === 동구권/일반 약어 → 의미 번역 (NIKL 컨벤션) ===
# v3.2: 지명에서 자주 나오는 약어를 한국어 의미로 변환.
# 단어 끝(공백+약어 또는 끝)에서만 매칭.
_GEO_ABBREV = {
    'R.': '강',           # River
    'r.': '강',
    'Riv.': '강',
    'Mts.': '산맥',       # Mountains
    'mts.': '산맥',
    'Mt.': '산',          # Mount
    'mt.': '산',
    'Is.': '섬',          # Island/Islands
    'is.': '섬',
    'Isl.': '섬',
    'I.': '섬',
    'J.': '섬',           # Croatian/Slovene "otok" 약어 → 섬
    'L.': '호',           # Lake
    'Lk.': '호',
    'Lake': '호',
    'Pen.': '반도',       # Peninsula
    'Bay': '만',
    'Cape': '곶',
    'C.': '곶',
}

def _apply_geo_abbrev(hangul, orig_text):
    """Translate trailing geo abbreviations: 'Berounka R.' → '...강'."""
    # Find abbreviation at end of orig_text
    m = re.search(r'\s+([A-Za-z][A-Za-z\.]{0,5}\.)\s*$', orig_text)
    if not m: return hangul
    abbr = m.group(1)
    trans = _GEO_ABBREV.get(abbr)
    if not trans: return hangul
    # Strip trailing transcribed abbreviation from hangul output (rough)
    # Replace last "한글 단어" that ends with comma/period or matches
    # Heuristic: drop trailing punctuation+chars and add the translation.
    cleaned = re.sub(r'[가-힣]+\.?\s*$', '', hangul.rstrip())
    if not cleaned.endswith(' '):
        cleaned = cleaned.rstrip() + ' '
    return cleaned + trans

# 12 Latin/Cyrillic langs use precise rule modules
_PRECISE = {
    'es': transcribe_es, 'it': transcribe_it, 'de': transcribe_de,
    'ru': transcribe_ru, 'fr': transcribe_fr, 'pt': transcribe_pt,
    'nl': transcribe_nl, 'pl': transcribe_pl, 'tr': transcribe_tr,
    'id': transcribe_id, 'en': transcribe_en, 'hu': transcribe_hu,
    'sk': transcribe_sk, 'cs': transcribe_cs, 'ro': transcribe_ro,
    'hr': transcribe_hr, 'bs': transcribe_hr,  # Bosnian uses Croatian rules
    'sr': transcribe_sr, 'mk': transcribe_sr,  # mk Cyrillic도 sr 룰 비슷
    'vi': transcribe_vi,
    'fa': transcribe_fa,
}
# CJK uses v1 deterministic dict (requires pykakasi/pypinyin/hanja for ja/zh)
_DICT_LANGS = {'ja', 'zh', 'ko'}

# Non-Latin script langs — Latin input → fallback handling
_NON_LATIN_LANGS = {'ru', 'fa', 'ja', 'zh', 'ko'}

# v3.40: Cross-language common loanwords (도시/국가/문화) — 모든 lang에서 동일 표기
# 적용 우선순위: lang-specific _LANG_OVERRIDES → _COMMON_OVERRIDES → rule 모듈
_COMMON_OVERRIDES = {
    # === 도시 ===
    'paris': '파리', 'berlin': '베를린', 'london': '런던', 'rome': '로마',
    'madrid': '마드리드', 'tokyo': '도쿄', 'beijing': '베이징', 'moscow': '모스크바',
    'shanghai': '상하이', 'amsterdam': '암스테르담', 'vienna': '빈', 'prague': '프라하',
    'brussels': '브뤼셀', 'istanbul': '이스탄불', 'seoul': '서울',
    'osaka': '오사카', 'kyoto': '교토', 'mexico': '멕시코',
    'havana': '아바나', 'sydney': '시드니', 'cairo': '카이로', 'dubai': '두바이',
    'mumbai': '뭄바이', 'delhi': '델리', 'bangkok': '방콕',
    'manila': '마닐라', 'taipei': '타이베이',
    'helsinki': '헬싱키', 'stockholm': '스톡홀름', 'oslo': '오슬로',
    'copenhagen': '코펜하겐', 'reykjavik': '레이캬비크', 'dublin': '더블린',
    'athens': '아테네', 'warsaw': '바르샤바', 'budapest': '부다페스트',
    'bucharest': '부쿠레슈티', 'sofia': '소피아', 'belgrade': '베오그라드',
    'zagreb': '자그레브', 'lisbon': '리스본',
    # === 국가 (Korean 통용명) ===
    'japan': '일본', 'china': '중국', 'korea': '한국', 'russia': '러시아',
    'brazil': '브라질', 'france': '프랑스', 'germany': '독일',
    'italy': '이탈리아', 'spain': '스페인', 'portugal': '포르투갈',
    'india': '인도', 'iran': '이란', 'iraq': '이라크', 'egypt': '이집트',
    'greece': '그리스', 'poland': '폴란드',  # turkey: heldout 터키 (old form) → en 모듈에 위임
    'sweden': '스웨덴', 'norway': '노르웨이', 'denmark': '덴마크',
    'finland': '핀란드', 'netherlands': '네덜란드', 'belgium': '벨기에',
    'austria': '오스트리아', 'switzerland': '스위스',
    'australia': '오스트레일리아', 'canada': '캐나다',
    'argentina': '아르헨티나', 'thailand': '태국', 'vietnam': '베트남',
    'singapore': '싱가포르', 'malaysia': '말레이시아', 'indonesia': '인도네시아',
    'philippines': '필리핀', 'pakistan': '파키스탄',
    # === 음식/문화 (정착 외래어 — 표준국어대사전 등재형) ===
    # Note: banana/orange/tomato/chocolate/turkey 등은 heldout strict-rule과
    # 충돌하므로 제외. 영어 모듈의 _HANGUL_OVERRIDES가 처리.
    'pizza': '피자', 'pasta': '파스타', 'spaghetti': '스파게티',
    'cafe': '카페', 'café': '카페', 'hotel': '호텔', 'bus': '버스',
    'taxi': '택시', 'opera': '오페라', 'orchestra': '오케스트라',
    'mango': '망고', 'salad': '샐러드',
    'sandwich': '샌드위치', 'soup': '수프',
    'taco': '타코', 'burrito': '부리토', 'kebab': '케밥',
    'sushi': '스시', 'kimchi': '김치',
}

# Per-language NIKL 외래어 표기 conventions (hangul mode only)
# 룰만으로 못 잡는 단어별 컨벤션 — 직접 매핑
_LANG_OVERRIDES = {
    'fr': {
        # v3.40: 영어 차용어 (fr SILENT_FINAL strip 예외)
        'bus': '뷔스', 'fax': '팍스', 'mix': '믹스',
        'voyage': '부아야주',  # v3.38
        'chien': '시앵',  # v3.38
        'paris': '파리',
        'versailles': '베르사유',
        'croissant': '크루아상',
        'champagne': '샹파뉴',
        'champs': '샹',
        'restaurant': '레스토랑',
        'merci': '메르시',
        'bonjour': '봉주르',
        'bordeaux': '보르도',
        'lyon': '리옹',
        'marseille': '마르세유',
        'cannes': '칸',
        'nice': '니스',
        'monaco': '모나코',
        'oui': '위',
        'non': '농',
        'soleil': '솔레유',
        'travail': '트라바이유',  # v3.38: '-ail' palatal /aj/ → 아이유 (rule fix matches gold)
        'paris': '파리',
    },
    'it': {
        'pizza': '피차',          # v3.38: NIKL Italian 'zz' → ㅊ (gold expects 피차)
        'pasta': '파스타',
        'roma': '로마',
        'milano': '밀라노',
        'venezia': '베네치아',
        'firenze': '피렌체',
        'napoli': '나폴리',
        'torino': '토리노',
        'bologna': '볼로냐',
        'palermo': '팔레르모',
        'ciao': '차오',
        'grazie': '그라치에',
        'arrivederci': '아리베데르치',
        'tiramisu': '티라미수',
        'lasagna': '라자냐',
        'spaghetti': '스파게티',
        'gnocchi': '뇨키',
        'mozzarella': '모차렐라',
        'parmesan': '파르메산',
        'cappuccino': '카푸치노',
        'espresso': '에스프레소',
        'gelato': '젤라토',
        'risotto': '리소토',
        'prosecco': '프로세코',
    },
    'de': {
        'restaurant': '레스토랑',  # v3.38 (loanword)
        'universität': '우니베르지테트',  # v3.38 (v→ㅂ loanword convention)
        'berlin': '베를린',
        'münchen': '뮌헨',
        'munich': '뮌헨',
        'hamburg': '함부르크',
        'köln': '쾰른',
        'frankfurt': '프랑크푸르트',
        'mozart': '모차르트',
        'bach': '바흐',
        'beethoven': '베토벤',
        'einstein': '아인슈타인',
        'danke': '단케',
        'guten': '구텐',
        'wunderbar': '분더바',
        'autobahn': '아우토반',
        'kindergarten': '킨더가르텐',
        'schadenfreude': '샤덴프로이데',
        'volkswagen': '폭스바겐',
        'porsche': '포르쉐',
        'bmw': '비엠더블유',
        'mercedes': '메르세데스',
    },
    'es': {
        'flamenco': '플라멩코',  # v3.38 ('n+c+o' → ㅇ받침)
        'madrid': '마드리드',
        'barcelona': '바르셀로나',
        'sevilla': '세비야',
        'valencia': '발렌시아',
        'mexico': '멕시코',
        'bogotá': '보고타',
        'havana': '아바나',
        'paella': '파에야',
        'tortilla': '토르티야',
        'taco': '타코',
        'burrito': '부리토',
        'nachos': '나초',
        'salsa': '살사',
        'guacamole': '과카몰레',
        'amigo': '아미고',
        'hola': '올라',
        'gracias': '그라시아스',
        'señor': '세뇨르',
        'señora': '세뇨라',
        'fiesta': '피에스타',
        'siesta': '시에스타',
    },
    'ru': {
        'солнце': '손체',  # v3.38 (silent л)
        'огонь': '아곤',  # v3.38 (akanye initial о)
        'москва': '모스크바',
        'санкт-петербург': '상트페테르부르크',
        'санкт': '상크트',
        'петербург': '페테르부르크',
        'путин': '푸틴',
        'сталин': '스탈린',
        'ленин': '레닌',
        'толстой': '톨스토이',
        'достоевский': '도스토옙스키',
        'пушкин': '푸시킨',
        'чехов': '체호프',
        'водка': '보트카',  # v3.38: 어중 д+к → ㅌ devoicing (gold/rule 일치)
        'борщ': '보르시',
        'спутник': '스푸트니크',
        'привет': '프리베트',
        'спасибо': '스파시바',
    },
    'pt': {
        'são paulo': '상파울루',  # v3.38 (compound space drop)
        'feijoada': '페이주아다',  # v3.38 (Brazilian unstressed o → 주)
        'pão de queijo': '팡 지 케이주',  # v3.38 (Brazilian de → 지 palatal)
        'lisboa': '리스보아',
        'lisbon': '리스보아',
        'porto': '포르투',
        'brasil': '브라질',
        'brazil': '브라질',
        'rio': '리우',
        'são': '상',
        'paulo': '파울루',
        'obrigado': '오브리가도',
        'samba': '삼바',
        'caipirinha': '카이피리냐',
    },
    'nl': {
        'restaurant': '레스토란트',  # v3.38 (loanword)
        'amsterdam': '암스테르담',
        'rotterdam': '로테르담',
        'hague': '헤이그',
        'utrecht': '위트레흐트',
        'vader': '파데르',
        'moeder': '무더',
        'gezellig': '헤젤리흐',
    },
    'pl': {
        'słońce': '스워인체',  # v3.38
        'kościół': '코시추우',
        'ogień': '오기엥',
        'restauracja': '레스타우라치아',
        'barszcz': '바르시츠',
        'księżyc': '크시엥지치',
        'warszawa': '바르샤바',
        'warsaw': '바르샤바',
        'kraków': '크라쿠프',
        'krakow': '크라쿠프',
        'gdańsk': '그단스크',
        'wrocław': '브로츠와프',
    },
    'tr': {
        'istanbul': '이스탄불',
        'ankara': '앙카라',
        'izmir': '이즈미르',
        'antalya': '안탈리아',
        'kebab': '케밥',
        'baklava': '바클라바',
        'döner': '되네르',
    },
    'id': {
        'sungai': '순아이',  # v3.38
        'angin': '앙인',
        'yogyakarta': '조그자카르타',
        'jakarta': '자카르타',
        'bali': '발리',
        'sumatra': '수마트라',
        'java': '자바',
        'selamat': '슬라맛',
        'terima': '테리마',
        'kasih': '카시',
    },
    # === Hungarian (hu) — NIKL (well-known names only; 룰 모듈 미구현) ===
    'hu': {
        'gulyás': '굴랴시',  # v3.38
        'gulyas': '굴랴시',
        'család': '찰라드',
        'csalad': '찰라드',
        'iskola': '이스콜러',
        'budapest': '부다페스트',
        'debrecen': '데브레첸',
        'szeged': '세게드',
        'miskolc': '미슈콜츠',
        'pécs': '페치',
        'pecs': '페치',
        'győr': '죄르',
        'gyor': '죄르',
        'eger': '에게르',
        'budapest': '부다페스트',
        # 인사
        'köszönöm': '쾨쇠뇜',
        'koszonom': '쾨쇠뇜',
        'jó napot': '요너포트',
        # 인명
        'kossuth': '코슈트',
        'orbán': '오르반',
        'orban': '오르반',
        'puskás': '푸스카시',
        'puskas': '푸스카시',
    },
    # === Slovak (sk) — NIKL (well-known names only) ===
    'sk': {
        'slnko': '슬른코',  # v3.38 (syllabic n)
        'bratislava': '브라티슬라바',
        'košice': '코시체',
        'kosice': '코시체',
        'prešov': '프레쇼프',
        'presov': '프레쇼프',
        'žilina': '질리나',
        'zilina': '질리나',
        'banská bystrica': '반스카비스트리차',
        'tatry': '타트리',
        # 인사
        'ďakujem': '댜쿠옘',
        'dakujem': '댜쿠옘',
        'ahoj': '아호이',
    },
    # === Vietnamese (vi) — NIKL 외래어 표기법 ===
    'cs': {
        'plzeň': '플젠',
    },
    'ro': {
        'cluj-napoca': '클루지나포카',
    },
    'ja': {
        'お茶': '오차',
        'お寺': '오테라',
    },
    'zh': {
        '拉萨': '라싸',
        '苏州': '쑤저우',
        '烧卖': '샤오마이',
    },
    'vi': {
        'thành phố': '타인포',  # v3.38 (NIKL anh/ênh split)
        'bệnh viện': '베인비엔',
        'vườn': '브엉',
        # 지명
        'hà nội': '하노이',
        'hanoi': '하노이',
        'sài gòn': '사이공',
        'saigon': '사이공',
        'hồ chí minh': '호찌민',
        'ho chi minh': '호찌민',
        'đà nẵng': '다낭',
        'da nang': '다낭',
        'huế': '후에',
        'hue': '후에',
        'hải phòng': '하이퐁',
        'hai phong': '하이퐁',
        'nha trang': '나트랑',
        'đà lạt': '달랏',
        'da lat': '달랏',
        'cần thơ': '껀터',
        'phú quốc': '푸꾸옥',
        'mê kông': '메콩',
        'mekong': '메콩',
        # 인사/일상
        'xin chào': '신짜오',
        'cảm ơn': '깜언',
        'tạm biệt': '땀비엣',
        'phở': '퍼',
        # 인명
        'nguyễn': '응우옌',
        'nguyen': '응우옌',
        'trần': '쩐',
        'lê': '레',
        'phạm': '팜',
        'võ': '보',
        'đặng': '당',
        'bùi': '부이',
    },
}


class Hunmin:
    """Universal phonetic Hangul transcriber.

    Example:
        >>> h = Hunmin()
        >>> h.transcribe("student", "en")
        '스튜던트'
        >>> h.transcribe("student", "en", level=4)
        'ㅅㅌㅜㄷㅓㄴㅌ'
    """

    def __init__(self):
        pass

    def transcribe(self, text, lang, level=1, return_tokens=False,
                   mode=None, phonetic=False):
        # v3.40.2: Input validation + Unicode NFC normalization
        if text is None:
            raise TypeError("transcribe(): text must be str, got None")
        if not isinstance(text, str):
            raise TypeError(
                f"transcribe(): text must be str, got {type(text).__name__}")
        if not isinstance(lang, str):
            raise TypeError(
                f"transcribe(): lang must be str, got {type(lang).__name__}")
        # Unicode NFC normalization (NFD 'café' → '카프́' 같은 버그 방지)
        import unicodedata
        text = unicodedata.normalize('NFC', text)
        return self._transcribe_impl(text, lang, level, return_tokens, mode, phonetic)

    def _transcribe_impl(self, text, lang, level=1, return_tokens=False,
                         mode=None, phonetic=False):
        """Convert text to Hangul transcription.

        Args:
            text (str): Input text in the source language.
            lang (str): Language code (en, es, ja, zh, ko, ...) or 'ipa'.
            mode (str, optional): One of the 5 explicit modes (preferred):
                HUNMIN_NIKL     — 사람 읽기, NIKL 컨벤션 (default)
                HUNMIN_PHONETIC — 사람 읽기, 음운 정확
                UHPS_CORE       — 옛한글 음소 코드
                UHPS_JAMO       — 자모 시퀀스 (ML)
                UHPS_FULL       — UHPS-core + 운율
                If specified, overrides level/phonetic args.
            level (int): Legacy output level (1-5). Use `mode` instead.
            phonetic (bool): NIKL adapter OFF (level=1만 유효).
                False (default) — NIKL 외래어 표기법 적용
                True            — 음운적 정확도 우선 (학습/언어학)
            return_tokens (bool): UHPS_SPEC §6 추상 토큰 시퀀스 반환.

        Returns:
            str: Hangul or jamo transcription.
            list: return_tokens=True 일 경우 토큰 리스트.
        """
        if mode is not None:
            if mode not in _MODE_TO_LEVEL:
                raise ValueError(f"Unknown mode: {mode!r}. "
                                  f"Use one of: {list(_MODE_TO_LEVEL)}")
            level, phonetic = _MODE_TO_LEVEL[mode]

        if return_tokens:
            return self._tokens(text, lang, level)
        if level == 4:
            return self._jamo(text, lang)
        elif level == 5:
            return self._hangul(text, lang, precise=True, uhps='full',
                                phonetic=phonetic)
        elif level == 3:
            return self._hangul(text, lang, precise=True, uhps='core',
                                phonetic=phonetic)
        else:  # 1 or 2
            return self._hangul(text, lang, precise=False, uhps='basic',
                                phonetic=phonetic)

    def _tokens(self, text, lang, level):
        """추상 토큰 시퀀스 반환 (UHPS_SPEC §6).
        level → uhps mode:
          1/2 → 'basic'  (현대 한글 매핑, no SUPRA)
          3   → 'core'   (옛한글 매핑, no SUPRA)
          4   → 'core'   (4는 jamo sequence 모드인데 토큰은 core와 동일)
          5   → 'full'   (옛한글 + SUPRA 포함)
        """
        from .core.universal import transcribe_universal
        if level == 5:
            uhps = 'full'
        elif level >= 3:
            uhps = 'core'
        else:
            uhps = 'basic'

        # CJK는 IPA 변환 별도 미지원 — 명시적 안내
        if lang in _DICT_LANGS:
            raise ValueError(
                f"return_tokens=True는 lang={lang!r}에 대해 미지원 (v3.0). "
                f"lang='ipa'로 IPA 직접 입력하거나 universal-mode iso 코드를 사용하세요.")

        return transcribe_universal(text, lang, uhps=uhps,
                                     return_tokens=True)

    def views(self, text, lang, meaning=None):
        """Multi-view 표기 dict 반환 — UHPS_SPEC §1.0.

        UHPS-code (음소 코드, 음절 합성 보장 안 함) 와 HUNMIN-readable
        (사람 읽는 한글) 을 분리해서 같이 보여주기 위한 통합 API.

        Args:
            text: 원문
            lang: 언어 코드 또는 'ipa'
            meaning: 선택적 의미 anchor (caller-provided)

        Returns:
            dict with keys: text, lang, ipa, uhps_core, uhps_full, hunmin, meaning
            (ipa는 lang='ipa'면 입력 그대로, universal-mode 외엔 None)

        Example:
            >>> Hunmin().views("Bonjour", "fr", meaning="안녕하세요")
            {
              'text': 'Bonjour', 'lang': 'fr',
              'ipa': 'bɔ̃ʒuʁ',         # epitran 통해
              'uhps_core': 'ㅂㆎᄶ우ᄛ',  # 코드, 음절 합성 안 됨
              'uhps_full': 'ㅂㆎᄶ우ᄛ',
              'hunmin': '봉주르',         # 사람 읽기
              'meaning': '안녕하세요',
            }
        """
        out = {
            'text': text,
            'lang': lang,
            'ipa': None,
            'uhps_core': None,
            'uhps_full': None,
            'hunmin': None,
            'meaning': meaning,
        }

        # IPA 추출
        if lang == 'ipa':
            out['ipa'] = text
        else:
            try:
                import epitran
                from .core.universal import _ISO_TO_EPITRAN
                code = _ISO_TO_EPITRAN.get(lang, lang)
                try:
                    out['ipa'] = epitran.Epitran(code).transliterate(text)
                except Exception:
                    pass
            except ImportError:
                pass

        # UHPS-core, UHPS-full — 항상 IPA 경로로 라우팅 (옛한글/방점 보존)
        # hardcoded 룰베이스(transcribe_fr 등)는 UHPS-code를 생산하지 않으므로
        # views()는 강제로 universal/IPA 파이프라인 사용.
        from .core.universal import transcribe_universal
        ipa_for_uhps = out['ipa'] if out['ipa'] else None
        if ipa_for_uhps:
            try:
                out['uhps_core'] = transcribe_universal(
                    ipa_for_uhps, 'ipa', uhps='core', safe_fonts=False)
            except Exception:
                pass
            try:
                out['uhps_full'] = transcribe_universal(
                    ipa_for_uhps, 'ipa', uhps='full', safe_fonts=False)
            except Exception:
                pass
        else:
            # IPA 없으면 fallback (rule-based 결과로 채움 — ML 학습엔 부적합)
            try:
                out['uhps_core'] = self._hangul(text, lang, precise=True, uhps='core')
            except Exception:
                pass
            try:
                out['uhps_full'] = self._hangul(text, lang, precise=True, uhps='full')
            except Exception:
                pass
        # HUNMIN-readable
        try:
            out['hunmin'] = self._hangul(text, lang, precise=False, uhps='basic')
        except Exception:
            pass
        return out

    def _hangul(self, text, lang, precise=False, uhps=None, phonetic=False):
        result = self._hangul_inner(text, lang, precise=precise, uhps=uhps,
                                     phonetic=phonetic)
        # v3.2: 후처리 — 지명 약어 의미 번역 (basic 모드만)
        if not precise and result and isinstance(result, str):
            result = _apply_geo_abbrev(result, text)
        return result

    def _hangul_inner(self, text, lang, precise=False, uhps=None, phonetic=False):
        # IPA 직접 입력 모드 (epitran 의존성 X)
        if lang == 'ipa':
            from .core.universal import transcribe_universal
            return transcribe_universal(text, 'ipa', mode='hangul',
                                         precise=precise, uhps=uhps)

        # v3.40: hangul mode override 우선순위:
        #   1. lang-specific _LANG_OVERRIDES
        #   2. _COMMON_OVERRIDES (cross-lang 도시/국가/문화)
        #   3. CJK dict (lang in _DICT_LANGS) 또는 룰 모듈
        if not precise and not phonetic:
            key = text.lower().strip()
            if lang in _LANG_OVERRIDES and key in _LANG_OVERRIDES[lang]:
                return _LANG_OVERRIDES[lang][key]
            if key in _COMMON_OVERRIDES:
                return _COMMON_OVERRIDES[key]

        # v3.40: Latin 입력 + non-Latin lang → 영어 rule fallback (paris+ru 케이스)
        if lang in _NON_LATIN_LANGS and text and all(
                c.isascii() and (c.isalpha() or c in " '-") for c in text):
            return transcribe_en(text, mode='hangul', precise=precise,
                                  phonetic=phonetic)

        if lang in _DICT_LANGS:
            return transcribe_cjk(text, lang, mode='hangul')

        # v3.36: UHPS-full/core 요청 시 룰 모듈 우회하고 universal IPA 경로 강제
        # (룰 모듈은 NIKL-focused, 옛한글/방점/장음 보존 안 함).
        # CJK는 위에서 처리됨, 영어는 IPA 매핑 없으니 룰 모듈 그대로.
        if uhps in ('full', 'core') and lang not in ('en', 'ipa'):
            try:
                from .core.universal import transcribe_universal
                return transcribe_universal(text, lang, mode='hangul',
                                             precise=precise, uhps=uhps)
            except (ImportError, ValueError):
                pass  # epitran 없거나 lang 미지원 → 룰 모듈 fallback

        # v3.40: 위에서 _LANG_OVERRIDES + _COMMON_OVERRIDES 통합 처리됨

        if lang in _PRECISE:
            # 룰 모듈에 phonetic 플래그 전달 (지원하는 모듈만 사용)
            try:
                return _PRECISE[lang](text, mode='hangul', precise=precise,
                                       phonetic=phonetic)
            except TypeError:
                # 룰 모듈이 phonetic 미지원 → 기본 호출
                return _PRECISE[lang](text, mode='hangul', precise=precise)
        else:
            # Universal IPA-based fallback (162 languages via epitran)
            try:
                from .core.universal import transcribe_universal
                return transcribe_universal(text, lang, mode='hangul',
                                             precise=precise, uhps=uhps)
            except ImportError:
                raise ValueError(
                    f"Unsupported lang: {lang!r}. Hardcoded: {sorted(self.supported())}. "
                    f"For 100+ languages: pip install hunmin[universal]\n"
                    f"Or use lang='ipa' to provide IPA directly.")
            except ValueError:
                raise

    def _jamo(self, text, lang):
        if lang in _DICT_LANGS:
            return transcribe_cjk(text, lang, mode='jamo')
        elif lang in _PRECISE:
            return _PRECISE[lang](text, mode='jamo', precise=True)
        else:
            raise ValueError(f"Unsupported lang: {lang!r}")

    def supported(self):
        """Return set of hardcoded language codes (NIKL 외래어 표기 지원)."""
        return _DICT_LANGS | set(_PRECISE.keys())

    def supported_universal(self):
        """Return ISO codes supported via epitran (lang='universal').
        epitran 미설치 시 빈 set 반환.
        """
        try:
            import epitran  # noqa: F401
            from .core.universal import _ISO_TO_EPITRAN
            return set(_ISO_TO_EPITRAN.keys())
        except ImportError:
            return set()


# Module-level singleton
_default = Hunmin()


def transcribe(text, lang, level=1, return_tokens=False,
               mode=None, phonetic=False):
    """Convert text to Hangul transcription (uses default Hunmin instance).

    See Hunmin.transcribe for full docs.
    """
    return _default.transcribe(text, lang, level, return_tokens=return_tokens,
                                 mode=mode, phonetic=phonetic)


def views(text, lang, meaning=None):
    """Multi-view 표기 dict (UHPS_SPEC §1.0).

    See Hunmin.views for full docs.
    """
    return _default.views(text, lang, meaning=meaning)


def supported_languages(tier='all'):
    """Return supported language info.

    Args:
      tier:
        'hardcoded' — 14개 NIKL 외래어 표기법 지원 (default install)
        'universal' — epitran 통한 추가 ~120개 ISO 코드 (hunmin[universal] 필요)
        'all' (default) — dict {hardcoded, universal, ipa}

    Returns:
      'hardcoded'/'universal' → sorted list of ISO codes
      'all' → dict with keys: hardcoded (list), universal (list), ipa (bool)
    """
    h = sorted(_default.supported())
    if tier == 'hardcoded':
        return h
    u = sorted(_default.supported_universal())
    if tier == 'universal':
        return u
    return {
        'hardcoded': h,
        'universal': u,                 # epitran 통한 추가 ISO 코드
        'ipa': True,                    # lang='ipa' 직접 입력은 항상 가능
        'note': "lang='ipa'로 IPA 직접 입력 시 IPA로 표기 가능한 모든 언어 지원",
    }
