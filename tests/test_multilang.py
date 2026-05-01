"""Multi-language regression tests."""
import pytest
from hunmin import transcribe


# === Spanish ===
@pytest.mark.parametrize('word,expected', [
    ('Madrid', '마드리드'),
    ('Barcelona', '바르셀로나'),
    ('paella', '파에야'),
    ('hola', '올라'),
    ('amigo', '아미고'),
    ('familia', '파밀리아'),
])
def test_spanish(word, expected):
    assert transcribe(word, 'es') == expected


# === French ===
@pytest.mark.parametrize('word,expected', [
    ('Paris', '파리'),
    ('Versailles', '베르사유'),
    ('croissant', '크루아상'),
    ('champagne', '샹파뉴'),
    ('café', '카페'),
    ('merci', '메르시'),
    ('bonjour', '봉주르'),
])
def test_french(word, expected):
    assert transcribe(word, 'fr') == expected


# === German ===
@pytest.mark.parametrize('word,expected', [
    ('Berlin', '베를린'),
    ('München', '뮌헨'),
    ('Mozart', '모차르트'),
    ('Bach', '바흐'),
    ('autobahn', '아우토반'),
    ('Volkswagen', '폭스바겐'),
])
def test_german(word, expected):
    assert transcribe(word, 'de') == expected


# === Italian ===
@pytest.mark.parametrize('word,expected', [
    ('Roma', '로마'),
    ('Milano', '밀라노'),
    ('pizza', '피자'),
    ('lasagna', '라자냐'),
    ('mozzarella', '모차렐라'),
    ('cappuccino', '카푸치노'),
    ('gelato', '젤라토'),
])
def test_italian(word, expected):
    assert transcribe(word, 'it') == expected


# === Russian ===
@pytest.mark.parametrize('word,expected', [
    ('Москва', '모스크바'),
    ('Путин', '푸틴'),
    ('Толстой', '톨스토이'),
    ('водка', '보드카'),
])
def test_russian(word, expected):
    assert transcribe(word, 'ru') == expected


# === Other Latin/Cyrillic langs ===
@pytest.mark.parametrize('word,lang,expected', [
    ('Lisboa', 'pt', '리스보아'),
    ('Brasil', 'pt', '브라질'),
    ('Amsterdam', 'nl', '암스테르담'),
    ('Warszawa', 'pl', '바르샤바'),
    ('Kraków', 'pl', '크라쿠프'),
    ('İstanbul', 'tr', '이스탄불'),
    ('kebab', 'tr', '케밥'),
    ('Jakarta', 'id', '자카르타'),
])
def test_other_latin(word, lang, expected):
    assert transcribe(word, lang) == expected


# === CJK regression ===
@pytest.mark.parametrize('word,lang,expected', [
    ('中国', 'zh', '중궈'),
    ('東京', 'ja', '도쿄'),
    ('大韓民國', 'ko', '대한민국'),
    ('학교', 'ko', '학교'),
])
def test_cjk(word, lang, expected):
    assert transcribe(word, lang) == expected


def test_supported_langs():
    from hunmin import supported_languages
    expected = {'en', 'es', 'it', 'de', 'ru', 'fr', 'pt',
                'nl', 'pl', 'tr', 'id', 'hu', 'sk', 'cs', 'ro',
                'hr', 'bs', 'sr', 'mk', 'vi',
                'ja', 'zh', 'ko'}
    # tier='hardcoded' returns sorted list
    h = supported_languages('hardcoded')
    assert set(h) == expected, f'Mismatch: {set(h) ^ expected}'
    # tier='all' returns dict
    info = supported_languages('all')
    assert 'hardcoded' in info and 'universal' in info and 'ipa' in info
    assert set(info['hardcoded']) == expected
    assert info['ipa'] is True
