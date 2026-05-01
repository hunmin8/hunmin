"""English transcription tests covering each pipeline stage."""
import pytest
from hunmin import transcribe


# === Stage 1: NIKL Hangul overrides ===
@pytest.mark.parametrize('word,expected', [
    ('hello', '헬로'),
    ('mother', '마더'),
    ('rock', '록'),
    ('hot', '핫'),
    ('lock', '락'),
    ('apple', '애플'),
    ('youtube', '유튜브'),
    ('google', '구글'),
    ('phone', '폰'),
    ('home', '홈'),
])
def test_overrides(word, expected):
    assert transcribe(word, 'en') == expected


# === Stage 2: Acronyms (letter-by-letter) ===
@pytest.mark.parametrize('word,expected', [
    ('USA', '유에스에이'),
    ('AI', '에이아이'),
    ('LSTM', '엘에스티엠'),
    ('GPU', '지피유'),
    ('CSS', '씨에스에스'),
    ('HTML', '에이치티엠엘'),
    ('FBI', '에프비아이'),
])
def test_acronyms(word, expected):
    assert transcribe(word, 'en') == expected


# === Stage 3: CMU dictionary lookup ===
@pytest.mark.parametrize('word,expected', [
    ('student', '스튜던트'),  # yod-inserted
    ('father', '파더'),       # ER → 파+더
    ('father_l3', 'ㆄ아더'),  # Old Hangul (level 3)
    ('history', '히스토리'),  # ER+'or' → AO+R
    ('park', '파크'),         # postvocalic R drop
    ('back', '백'),           # K coda
    ('boat', '보트'),         # OW long → no coda
    ('big', '빅'),            # G coda
    ('cap', '캡'),            # P coda
    ('cab', '캡'),            # B coda (= P)
    ('script', '스크립트'),   # KR cluster
    ('blue', '블루'),         # CL cluster doubling
    ('club', '클럽'),
    ('about', '어바웃'),      # AW second short
])
def test_cmu_pipeline(word, expected):
    if word.endswith('_l3'):
        base = word.rsplit('_', 1)[0]
        assert transcribe(base, 'en', level=3) == expected
    else:
        assert transcribe(word, 'en') == expected


# === Stage 4: Compound decomposer ===
@pytest.mark.parametrize('word,expected', [
    ('firebase', '파이어베이스'),
    ('typescript', '타이프스크립트'),
    ('youtube', '유튜브'),  # also in overrides
    ('blockchain', '블록체인'),
])
def test_compound(word, expected):
    assert transcribe(word, 'en') == expected


# === Stage 5: Morphology / compound fallback ===
@pytest.mark.parametrize('word,expected_substr', [
    ('preprocessing', '프리'),  # pre + processing
    ('multimodal', '멀티'),     # multi + modal
    ('cryptocurrency', '크립토'),
    ('postdoctoral', '포스트'),
])
def test_morphology(word, expected_substr):
    out = transcribe(word, 'en')
    assert expected_substr in out, f'{word} → {out}'


# === Stage 6: Syllabic schwa drop + cluster-coda merge ===
@pytest.mark.parametrize('word,expected', [
    ('button', '버튼'),
    ('bottle', '보틀'),
    ('middle', '미들'),
    ('table', '테이블'),
    ('rhythm', '리듬'),
    ('circle', '서클'),
    ('cattle', '캐틀'),
])
def test_syllabic_schwa(word, expected):
    assert transcribe(word, 'en') == expected


# === Regression: schwa drop must NOT fire for stressed-only-vowel words ===
@pytest.mark.parametrize('word,expected', [
    ('run', '런'),
    ('jump', '점프'),
    ('trump', '트럼프'),
    ('drum', '드럼'),
])
def test_no_schwa_drop_on_stressed(word, expected):
    assert transcribe(word, 'en') == expected


# === Levels 1-4 ===
def test_level_1_default():
    assert transcribe('student', 'en') == '스튜던트'
    assert transcribe('student', 'en', level=1) == '스튜던트'


def test_level_3_old_hangul():
    assert transcribe('vine', 'en', level=3) == 'ㅸ아인'  # /v/ → ㅸ
    assert transcribe('zoo', 'en', level=3) == 'ㅿ우'    # /z/ → ㅿ


def test_level_4_jamo():
    out = transcribe('student', 'en', level=4)
    # Should be a sequence of jamo without composed syllables
    for ch in out:
        assert 0x1100 <= ord(ch) <= 0x11FF or 0x3130 <= ord(ch) <= 0x318F or ch.isspace(), \
            f'Non-jamo char in L4: {ch}'
