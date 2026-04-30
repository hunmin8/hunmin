"""Hunmin public API — Hunmin class + transcribe() shortcut."""
from .core import (
    transcribe_es, transcribe_it, transcribe_de, transcribe_ru,
    transcribe_fr, transcribe_pt, transcribe_nl, transcribe_pl,
    transcribe_tr, transcribe_id, transcribe_en,
    transcribe_cjk,
)

# 11 Latin/Cyrillic langs use precise rule modules
_PRECISE = {
    'es': transcribe_es, 'it': transcribe_it, 'de': transcribe_de,
    'ru': transcribe_ru, 'fr': transcribe_fr, 'pt': transcribe_pt,
    'nl': transcribe_nl, 'pl': transcribe_pl, 'tr': transcribe_tr,
    'id': transcribe_id, 'en': transcribe_en,
}
# CJK uses v1 deterministic dict (requires pykakasi/pypinyin/hanja for ja/zh)
_DICT_LANGS = {'ja', 'zh', 'ko'}

# Per-language NIKL 외래어 표기 conventions (hangul mode only)
# 룰만으로 못 잡는 단어별 컨벤션 — 직접 매핑
_LANG_OVERRIDES = {
    'fr': {
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
        'travail': '트라바유',
        'paris': '파리',
    },
    'it': {
        'pizza': '피자',          # via English convention
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
        'водка': '보드카',
        'борщ': '보르시',
        'спутник': '스푸트니크',
        'привет': '프리베트',
        'спасибо': '스파시바',
    },
    'pt': {
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
        'amsterdam': '암스테르담',
        'rotterdam': '로테르담',
        'hague': '헤이그',
        'utrecht': '위트레흐트',
        'vader': '파데르',
        'moeder': '무더',
        'gezellig': '헤젤리흐',
    },
    'pl': {
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
        'jakarta': '자카르타',
        'bali': '발리',
        'sumatra': '수마트라',
        'java': '자바',
        'selamat': '슬라맛',
        'terima': '테리마',
        'kasih': '카시',
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

    def transcribe(self, text, lang, level=1):
        """Convert text to Hangul transcription.

        Args:
            text (str): Input text in the source language.
            lang (str): Language code (en, es, ja, zh, ko, ...).
            level (int): Output level (1-4).
                1: Children-friendly Hangul (default)
                2: Natural pronunciation
                3: Precise with old Hangul (ㆄ/ㅸ/ㅿ)
                4: UHPS jamo sequence

        Returns:
            str: Hangul or jamo transcription.
        """
        if level == 4:
            return self._jamo(text, lang)
        elif level == 3:
            return self._hangul(text, lang, precise=True)
        else:  # 1 or 2
            return self._hangul(text, lang, precise=False)

    def _hangul(self, text, lang, precise=False):
        # IPA 직접 입력 모드 (epitran 의존성 X)
        if lang == 'ipa':
            from .core.universal import transcribe_universal
            return transcribe_universal(text, 'ipa', mode='hangul', precise=precise)
        if lang in _DICT_LANGS:
            return transcribe_cjk(text, lang, mode='hangul')
        elif lang in _PRECISE:
            # Per-language Hangul override (단일 단어만; 공백/구두점이면 룰 사용)
            if not precise and lang in _LANG_OVERRIDES:
                key = text.lower().strip()
                if key in _LANG_OVERRIDES[lang]:
                    return _LANG_OVERRIDES[lang][key]
            return _PRECISE[lang](text, mode='hangul', precise=precise)
        else:
            # Universal IPA-based fallback (162 languages via epitran)
            try:
                from .core.universal import transcribe_universal
                return transcribe_universal(text, lang, mode='hangul', precise=precise)
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
        """Return set of supported language codes."""
        return _DICT_LANGS | set(_PRECISE.keys())


# Module-level singleton
_default = Hunmin()


def transcribe(text, lang, level=1):
    """Convert text to Hangul transcription (uses default Hunmin instance).

    See Hunmin.transcribe for full docs.
    """
    return _default.transcribe(text, lang, level)


def supported_languages():
    """Return sorted list of supported language codes."""
    return sorted(_default.supported())
