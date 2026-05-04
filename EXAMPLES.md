# Hunmin — Examples Gallery

다양한 실용 사용 예시. API 명세는 [docs/API_REFERENCE.md](docs/API_REFERENCE.md) 참고.

## Quick Start

```python
from hunmin import transcribe

transcribe('Mozart', 'de')          # → '모차르트'
transcribe('Bonjour', 'fr')          # → '봉주르'
transcribe('familia', 'es')          # → '파밀리아'
transcribe('東京', 'ja')              # → '도쿄'
transcribe('北京', 'zh')              # → '베이징'
transcribe('학교', 'ko')              # → '학교'
```

## Modes — 5가지 표기 방식

```python
from hunmin import transcribe, HUNMIN_NIKL, HUNMIN_PHONETIC, UHPS_FULL, UHPS_CORE, UHPS_JAMO

# 1. NIKL (default) — 사람이 읽기 편한 표기
transcribe('Mozart', 'de', mode=HUNMIN_NIKL)
# → '모차르트'

# 2. PHONETIC — 음운적 정확도 우선 (학습/언어학)
transcribe('vier', 'de', mode=HUNMIN_PHONETIC)
# → '피어' (NIKL 컨벤션 미적용)

# 3. UHPS-CORE — 옛한글 음소 코드 (자모 분리)
transcribe('Mozart', 'de', mode=UHPS_CORE)
# → '모ː차ㄹ트' (장음 보존)

# 4. UHPS-JAMO — ML 입력용 자모 시퀀스
transcribe('hello', 'en', mode=UHPS_JAMO)
# → 'ㅎㅔㄹㄹㅗ'

# 5. UHPS-FULL — UHPS-core + 운율 (장단/강세/성조)
transcribe('Mozart', 'de', mode=UHPS_FULL)
# → '모·ː차ㄹ트'
```

## CLI 사용

```bash
# 단일 단어
hunmin "Mozart" --lang de              # 모차르트
hunmin "Bonjour" --lang fr             # 봉주르

# stdin pipe
echo "hello" | hunmin --lang en        # 헬로
cat words.txt | hunmin --lang en       # 줄별 변환

# 모드 지정
hunmin "Mozart" -l de --mode uhps_full # 모·ː차ㄹ트

# Multi-view (모든 mode 한 번에)
hunmin "Mozart" -l de --views

# Demo
hunmin --demo

# 지원 언어 목록
hunmin --list-langs
```

## Cross-language proper noun 일관성

```python
# 도시 이름 — 어느 lang으로 호출해도 동일
transcribe('paris', 'en')              # → '파리'
transcribe('paris', 'fr')              # → '파리'
transcribe('paris', 'ru')              # → '파리'  (Latin → ru auto fallback)

# Wrong-script 자동 라우팅
transcribe('москва', 'en')             # → '모스크바' (Cyrillic 감지 → ru 룰)
transcribe('東京', 'fr')                # → '둥징' (CJK kanji → zh)
transcribe('شکر', 'en')                # → '사칼' (Arabic → fa)
transcribe('안녕', 'en')                # → '안녕' (이미 한국어)
```

## 정착 외래어

```python
transcribe('pizza', 'en')              # → '피자' (정착 외래어)
transcribe('pizza', 'it')              # → '피차' (이탈리아어 발음 strict)
transcribe('hotel', 'en')              # → '호텔'
transcribe('cafe', 'fr')               # → '카페'
```

## IPA 직접 입력

```python
transcribe('ˈfɑːðɚ', 'ipa', mode=UHPS_FULL)
# → 'ㆄ아ː ㅽ어' (옛한글 음소 보존)
```

## Multi-view (한 번에 여러 표기)

```python
from hunmin import views

views('Mozart', 'de')
# {
#     'text': 'Mozart',
#     'lang': 'de',
#     'ipa': 'ˈmɔt͡saʁt',
#     'hunmin': '모차르트',
#     'uhps_core': '모·차ㄹ트',
#     'uhps_full': '모·ː차ㄹ트',
# }
```

## ML 학습용 jamo 시퀀스

```python
# 영어 약어 → letter-by-letter
transcribe('NASA', 'en', mode=UHPS_JAMO)   # → 'ㅔㄴㅔㅣㅔㅅㅔㅣ'
transcribe('IBM', 'en', mode=UHPS_JAMO)    # → 'ㅏㅣㅂㅣㅔㅁ'

# 일반 단어
transcribe('hello', 'en', mode=UHPS_JAMO)  # → 'ㅎㅔㄹㄹㅗ'
transcribe('東京', 'ja', mode=UHPS_JAMO)    # → 'ㄷㅗㅋㅛ'
```

## 캐시 활용

```python
from hunmin import transcribe, transcribe_cache_info, transcribe_cache_clear

# 반복 호출 — LRU cache가 자동 적용 (2048 entries)
for word in word_list:
    transcribe(word, 'en')

# 캐시 상태 확인
print(transcribe_cache_info())
# CacheInfo(hits=...)

# 캐시 클리어
transcribe_cache_clear()

# 캐시 끄기
transcribe('hello', 'en', cache=False)
```

## 다국어 batch

```python
from hunmin import transcribe

batch = [
    ('Mozart', 'de'),
    ('Москва', 'ru'),
    ('東京', 'ja'),
    ('familia', 'es'),
]
results = [transcribe(w, l) for w, l in batch]
# ['모차르트', '모스크바', '도쿄', '파밀리아']
```

## 에러 처리

```python
try:
    transcribe(None, 'en')
except TypeError as e:
    print(e)  # "transcribe(): text must be str, got NoneType"

try:
    transcribe('hello', 'xxx')
except ValueError as e:
    print(e)  # "Unsupported lang: 'xxx'..."
```

## Universal IPA fallback (epitran 의존성)

```bash
pip install hunmin[universal]
```

```python
# 100+ 언어 자동 IPA 변환 → 한글
transcribe('สวัสดี', 'tha')      # Thai
transcribe('नमस्ते', 'hin')        # Hindi
transcribe('مرحبا', 'arb')        # Arabic
```

## Web UI (Gradio)

```bash
pip install hunmin[demo]
hunmin --web
```

또는 [HuggingFace Space](https://huggingface.co/spaces/foolsai/hunmin)에서 바로 사용.

## Common Pitfalls

### 한국어 입력은 변환되지 않음
```python
transcribe('안녕', 'en')   # → '안녕' (이미 Hangul, no-op)
```

### Mixed-script는 lang 우선
```python
transcribe('Mozart 東京', 'de')  # → 'Mozart 東京' 부분만 변환되지 않을 수 있음
# 권장: 분리해서 처리
```

### 차용어 vs 룰 strict
```python
transcribe('pizza', 'en')   # 피자 (정착)
transcribe('pizza', 'it')   # 피차 (이탈리아어 룰)
```

## Performance

- 캐시 hit: 0.1µs/call (7.6M calls/s)
- 룰 모듈: 5µs/call
- CJK: 10-15µs/call (pykakasi/pypinyin overhead)

## See Also

- [README.md](README.md)
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- [docs/UHPS_SPEC.md](docs/UHPS_SPEC.md)
- [HuggingFace Space](https://huggingface.co/spaces/foolsai/hunmin)
