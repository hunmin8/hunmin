# Hunmin API Reference

전체 공개 API 명세. 자세한 음운 변환 규칙은 [UHPS_SPEC.md](UHPS_SPEC.md) 참고.

## Quick Reference

```python
from hunmin import transcribe, views

# 기본 사용
transcribe('Mozart', 'de')                      # → '모차르트'
transcribe('Bonjour', 'fr', mode='uhps_full')   # → 'ㅂㆎᄶ우ᄛ' (음소 보존)
transcribe('rabbit', 'ipa')                     # → IPA 직접 입력 가능
views('Mozart', 'de')                           # → dict (모든 mode 한 번에)
```

## Function: `transcribe()`

### Signature

```python
transcribe(
    text: str,
    lang: str,
    level: int = 1,
    return_tokens: bool = False,
    mode: str | None = None,
    phonetic: bool = False,
) -> str
```

### Parameters

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `text` | `str` | 변환할 입력 텍스트. NFC 정규화됨 자동. |
| `lang` | `str` | 언어 코드 (아래 표 참고) 또는 `'ipa'` |
| `mode` | `str` | 5개 explicit mode 중 하나 (권장) |
| `level` | `int` | Legacy mode 지정 (1~5). `mode` 사용 권장 |
| `phonetic` | `bool` | NIKL adapter OFF — 음운 룰만 적용 |
| `return_tokens` | `bool` | 토큰 시퀀스 반환 (UHPS-spec 토큰) |

### Modes (UHPS_SPEC §1.0)

| Mode 상수 | 출력 | 용도 |
|----------|------|------|
| `HUNMIN_NIKL` | NIKL 외래어 표기 컨벤션 (default) | 사람이 읽기 |
| `HUNMIN_PHONETIC` | 음운적 정확도 우선 | 학습/언어학 |
| `UHPS_CORE` | 옛한글 음소 코드 (자모 분리) | IPA 1:1 |
| `UHPS_JAMO` | 분해된 자모 시퀀스 | ML 입력용 |
| `UHPS_FULL` | UHPS-core + 운율 (장단/강세/성조) | 음성 합성 |

```python
from hunmin import transcribe, HUNMIN_NIKL, UHPS_FULL

transcribe('Mozart', 'de', mode=HUNMIN_NIKL)   # → '모차르트'
transcribe('Mozart', 'de', mode=UHPS_FULL)     # → '모·ː차ㄹ트' (장음/강세 보존)
```

### Return Value

`str` — 변환된 한글. 입력이 이미 한글이거나 인식 안 되는 문자는 그대로 전달.

### Errors

| 예외 | 발생 조건 |
|------|----------|
| `TypeError` | `text`/`lang`이 `str`이 아닌 경우 (None, int 등) |
| `ValueError` | 지원하지 않는 `lang` 또는 `mode` |
| `ImportError` | CJK lang에 deps 미설치 (pykakasi/pypinyin/hanja) |

## Function: `views()`

```python
views(text: str, lang: str) -> dict
```

5개 mode 출력을 한 번에 반환. 각 mode 실패 시 해당 키 누락.

```python
views('Mozart', 'de')
# → {
#     'ipa': 'ˈmɔt͡saʁt',
#     'hunmin': '모차르트',
#     'uhps_core': '모·차ㄹ트',
#     'uhps_full': '모·ː차ㄹ트',
#     ...
# }
```

## Class: `Hunmin`

내부 인스턴스. 직접 사용 비권장 — `transcribe()` 사용.

```python
from hunmin import Hunmin
h = Hunmin()
h.transcribe('hello', 'en')
```

## Constants

| 상수 | 값 |
|------|-----|
| `HUNMIN_NIKL` | `'hunmin_nikl'` |
| `HUNMIN_PHONETIC` | `'hunmin_phonetic'` |
| `UHPS_CORE` | `'uhps_core'` |
| `UHPS_JAMO` | `'uhps_jamo'` |
| `UHPS_FULL` | `'uhps_full'` |
| `__version__` | 현재 버전 |

## Supported Languages

### Hardcoded rule modules (NIKL 외래어 표기 strict)

| Code | 언어 | Script | Notes |
|------|------|--------|-------|
| `en` | English | Latin | CMU dict 기반 |
| `es` | Spanish | Latin | NIKL phonetic |
| `it` | Italian | Latin | |
| `de` | German | Latin | sch/ch 등 처리 |
| `fr` | French | Latin | 비음/silent letter |
| `pt` | Portuguese | Latin | Brazilian/European 통합 |
| `nl` | Dutch | Latin | -en/-er schwa |
| `pl` | Polish | Latin | sz/cz/rz 등 |
| `tr` | Turkish | Latin | ğ silent |
| `id` | Indonesian | Latin | 1:1 phonetic |
| `hu` | Hungarian | Latin | gy/ny digraph |
| `cs` | Czech | Latin | ě palatal |
| `sk` | Slovak | Latin | |
| `ro` | Romanian | Latin | ș/ț |
| `hr` | Croatian | Latin | lj/nj |
| `bs` | Bosnian | Latin | (= hr 룰) |
| `sr` | Serbian | Cyrillic | |
| `mk` | Macedonian | Cyrillic | |
| `vi` | Vietnamese | Latin | tone-stripped |
| `fa` | Persian/Farsi | Arabic | dict 기반 |
| `ru` | Russian | Cyrillic | |

### Dict-based (CJK)
| Code | 언어 | 의존성 |
|------|------|-------|
| `ja` | Japanese | `pykakasi` |
| `zh` | Mandarin | `pypinyin` |
| `ko` | Korean | `hanja` (Hanja → Hangul) |

### Universal IPA (epitran 의존성)
- 100+ 언어 — `pip install hunmin[universal]` 필요
- 또는 `lang='ipa'`로 IPA 직접 입력

## Override Mechanism

### Priority order (hangul mode)

1. **`_LANG_OVERRIDES[lang]`** (`api.py`) — lang별 word-specific 매핑
2. **`_COMMON_OVERRIDES`** (`api.py`) — cross-lang 도시/국가/loanword
3. **Wrong-script auto-route** — `transcribe('москва','en')` → ru 룰 사용
4. **CJK dict** (`ja`/`zh`/`ko`) 또는 **rule 모듈** (`_PRECISE`)
5. **Universal IPA fallback** (epitran)

### Module-level overrides

각 lang 모듈에 `_HANGUL_OVERRIDES` 또는 `_PHRASE_OVERRIDES` dict 존재:
- `hunmin/core/english.py`: `_HANGUL_OVERRIDES` (~600 entries)
- `hunmin/core/persian.py`: `_HANGUL_OVERRIDES` (30+ entries)
- `hunmin/core/cjk.py`: `_JA_PHRASE_OVERRIDES` (~200 entries), `_ZH_PHRASE_OVERRIDES` (40+)

## Examples

### 일반 사용

```python
from hunmin import transcribe

# 기본 NIKL 표기
transcribe('hello', 'en')        # → '헬로'
transcribe('familia', 'es')      # → '파밀리아'
transcribe('東京', 'ja')          # → '도쿄'
transcribe('北京', 'zh')          # → '베이징'

# 도시명 — lang 무관 일관됨
transcribe('paris', 'en')        # → '파리'
transcribe('paris', 'fr')        # → '파리'
transcribe('paris', 'ru')        # → '파리'

# Latin 입력 + 비-Latin lang → 자동 영어 룰 fallback
transcribe('Tokyo', 'ja')        # → '도쿄'

# 비-Latin 입력 + Latin lang → 자동 라우팅
transcribe('москва', 'en')       # → '모스크바' (ru로 라우팅)
transcribe('東京', 'fr')          # → '둥징' (zh kanji-only)
```

### IPA 직접 입력

```python
transcribe('ˈfɑːðɚ', 'ipa', mode='uhps_full')  # → 'ㆄㆍː ㅽ어'
```

### 음운적 정확도 우선

```python
# NIKL 컨벤션 OFF, 룰만으로 음운 정확
transcribe('vier', 'de', phonetic=True)        # /f/ → ㅍ (NIKL 컨벤션 비적용)
```

### ML 입력용 jamo 시퀀스

```python
transcribe('hello', 'en', mode='uhps_jamo')    # → 'ㅎㅔㄹㄹㅗ'
transcribe('NASA', 'en', mode='uhps_jamo')     # → 'ㅔㄴㅔㅣㅔㅅㅔㅣ' (acronym)
```

## Performance

- 표준 단어: ~100µs/call (rule 모듈)
- CJK: ~1ms/call (pykakasi/pypinyin overhead)
- 캐싱 권장 (반복 호출 시 `functools.lru_cache`)

## Versioning

[Semantic Versioning](https://semver.org/):
- MAJOR: API 호환성 깨짐
- MINOR: 새 lang/feature 추가
- PATCH: bug fix / accuracy 개선

## See Also

- [UHPS_SPEC.md](UHPS_SPEC.md) — 음운 변환 spec
- [UHPS_FULL_SHOWCASE.md](UHPS_FULL_SHOWCASE.md) — UHPS-full 예시 모음
- [CHANGELOG.md](../CHANGELOG.md) — 버전별 변화
- [tests/gold/](../tests/gold/) — gold corpus
