# 🎼 Hunmin

[![PyPI](https://img.shields.io/pypi/v/hunmin)](https://pypi.org/project/hunmin/)
[![Python](https://img.shields.io/pypi/pyversions/hunmin)](https://pypi.org/project/hunmin/)
[![License](https://img.shields.io/pypi/l/hunmin)](https://github.com/meshpop/hunmin/blob/main/LICENSE)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/foolsai/hunmin)

> **모든 언어를 한국 화자가 읽을 수 있는 IPA-faithful 음소 표기로**  
> *Convert any language into Korean-readable, IPA-faithful phonetic Hangul.*

**[🎼 온라인 데모 사용해보기](https://huggingface.co/spaces/foolsai/hunmin)**

## ⭐ Primary Mode — UHPS-full

UHPS-full은 한국 화자가 읽을 수 있으면서 **IPA 정보를 거의 100% 보존**하는 모드.
NIKL 외래어 표기처럼 음소 손실 없음 — 옛한글로 /f/ /v/ /z/ /θ/ 같은 한국어 외 음소 표기 + 장단·강세·성조 보존.

```python
from hunmin import transcribe, UHPS_FULL

transcribe('father',  'ipa', mode=UHPS_FULL)  # via IPA: ˈfɑːðɚ
# → ㆄㆍː ㅽ어    (/f/ ㆄ, 장음 ː, /ð/ ㅽ, schwa 어)

transcribe('Mozart',  'de',  mode=UHPS_FULL)
# → 모·ː차ㄹ트     (강세 위치 + 장음)

transcribe('Bonjour', 'fr',  mode=UHPS_FULL)
# → ㅂㆎᄶ우ᄛ      (/ɔ̃/ ㆎ, /ʒ/ ᄶ, /ʁ/ ᄛ — 모두 보존)

transcribe('xin chào', 'ipa', mode=UHPS_FULL)  # via IPA: sin t͡ɕaːw
# → 신 차ː으       (장음 보존, 음절 분리)
```

| 단어 | NIKL (음소 손실) | **UHPS-full** (보존) |
|------|----------------|---------------------|
| `father` | 파더 | **ㆄㆍː ㅽ어** |
| `pizza` | 피자 | **피·트차** |
| `Bonjour` | 봉주르 | **ㅂㆎᄶ우ᄛ** |
| `Beijing` | 베이징 | **베이ㅈ이·ㆁ** |

**옛한글 추정 가이드** (5분만 익히면 직관적):
ㆄ=강한ㅍ(/f/) · ㅸ=약한ㅂ(/v/) · ㅿ=약한ㅈ(/z/) · ㆅ=강한ㅎ(/x/) · ᄾ=치찰ㅅ(/ʃ/) · ᄶ=치찰ㅈ(/ʒ/) · ᄛ=가벼운ㄹ(/ʁ/) · ㅼ=ㅅㄷ(/θ/) · ㅽ=ㅅㅂ(/ð/) · ㆎ=ㅗㅓ사이(/ɔ/) · ㆍ=ㅏㅓ사이(/ɑ/) · ㆁ=강조ㅇ(/ŋ/)

→ 자세한 비교: [docs/UHPS_FULL_SHOWCASE.md](docs/UHPS_FULL_SHOWCASE.md)

## 기본 사용 — 5 modes

```python
from hunmin import transcribe, HUNMIN_NIKL, HUNMIN_PHONETIC, UHPS_CORE, UHPS_JAMO, UHPS_FULL

# 1. HUNMIN_NIKL — 한국어 외래어 표기 (사람 읽기, NIKL 친화)
transcribe('hello', 'en', mode=HUNMIN_NIKL)        # 헬로
# 2. HUNMIN_PHONETIC — 음운 정확 (NIKL 사전 우회)
transcribe('hello', 'en', mode=HUNMIN_PHONETIC)    # 헐로
# 3. UHPS_CORE — 옛한글 음소 코드 (자모 분리, IPA 1:1)
transcribe('hello', 'en', mode=UHPS_CORE)          # 허로우
# 4. UHPS_JAMO — 분해된 자모 시퀀스 (ML 입력용)
transcribe('student', 'en', mode=UHPS_JAMO)        # ㅅㅌㅜㄷㅓㄴㅌ
# 5. UHPS_FULL — UHPS-core + 운율 (★ primary)
transcribe('hello', 'en', mode=UHPS_FULL)          # 허로·우
```

## Mixed-script — `transcribe_auto`

모든 입력 (라틴/키릴/한자/일본/한글/그리스/히브리/아르메니아/아랍/힌디/태국 + 숫자/기호) 100% UHPS 공간으로 인코딩:

```python
from hunmin import transcribe_auto

transcribe_auto('Hello 中国 5 apples & C++')
# → '헬로 중궈 오 애펄즈 앤드 시플러스플러스'
transcribe_auto('Καλημέρα 친구! $100 + 50%')
# → '카리메라 친구! 달러일영영 플러스 오영퍼센트'
```

## 정확도

**진짜 정확도 metric — UHPS Spec compliance: 100%** (95/95 tests, `tests/test_uhps_spec.py`).

NIKL 외래어 표기 벤치 (보조 지표 — NIKL 위원회 결정 따라가기 측정, 천장 ~25%):
- 사용자 경험 (사전+룰): 영어 98.5% / 다국어 100% / 도·현 92%
- Held-out 룰: 영어 en_heldout_diverse 64.3%
- 외부 NIKL gold (동구권 1299단어, leakage 0): **19.8%** (v3.1 9.7% → v3.14 19.8%, ~2x)

> **NIKL 정확도는 hunmin 본질의 정확도가 아님.** UHPS-full은 NIKL의 위원회 결정과 무관하게 IPA 기준으로 측정된다.

---

## ✨ 왜 Hunmin인가?

* **한글은 원래 발음 악보였습니다.** 1443년 세종이 그렇게 설계했습니다.
* **읽으면 그 언어가 됩니다.** 어린이가 읽어도 외국인이 알아듣는 발음.
* **옛한글 부활.** 한국어가 잃은 소리들 — ㆄ (/f/), ㅸ (/v/), ㅿ (/z/) — 다시 사용.
* **하나의 API, 14개 언어.** 같은 호출, 결정적 출력.
* **블랙박스 없음.** 100% 룰 기반 (default). ML 모델은 연구용 옵션.

---

## 📦 설치

```bash
pip install hunmin              # 11개 Latin/Cyrillic NIKL (en/es/fr/de/it/ru/pt/nl/pl/tr/id)
pip install hunmin[cjk]         # + ja/zh/ko (한자 처리; pykakasi/pypinyin/hanja 필요)
pip install hunmin[universal]   # + ~120 ISO 코드 (epitran 기반 IPA 자동 추출)
pip install hunmin[ml]          # + g2p-en (영어 unknown 단어 신경망 G2P)
pip install hunmin[demo]        # + Gradio 웹 데모
pip install hunmin[all]         # 모두
```

> **주의**:
> - 기본 `pip install hunmin`은 14개 중 **11개만** 동작 (ja/zh/ko는 `[cjk]` 필요).
> - Universal 모드의 ~120개 ISO 코드는 모두 epitran 매핑 검증됨, 다만 출력 정확도는 언어별 차이.
> - `lang='ipa'`는 epitran 없이도 동작 (의존성 X).

---

## 🚀 빠른 시작

### Python

```python
from hunmin import transcribe

# 기본 — 아이용 한글
transcribe("student", "en")           # 스튜던트
transcribe("hello",   "en")           # 헬로
transcribe("Paris",   "fr")           # 파리
transcribe("中国",     "zh")           # 중궈
transcribe("東京",     "ja")           # 도쿄
transcribe("こんにちは",   "ja")           # 곤니치와

# 영어 고급 — CMU 사전 + phonics + 합성어 + 약어 자동
transcribe("anthropic","en")          # 앤스라픽 (CMU 미수록 → phonics)
transcribe("typescript","en")         # 타이프스크립트 (합성어 분해)
transcribe("USA",      "en")          # 유에스에이 (대문자 약어 letter-by-letter)
transcribe("LSTM",     "en")          # 엘에스티엠 (모음 없는 토큰)
transcribe("button",   "en")          # 버튼 (syllabic schwa)

# 일본어 — NIKL 외래어 표기법 적용
transcribe("大阪",      "ja")          # 오사카
transcribe("京都府",     "ja")          # 교토부 (행정 접미사 한자 음독)
transcribe("鹿児島県",   "ja")          # 가코시마현
transcribe("ラーメン",    "ja")          # 라멘 (장음 드롭)
transcribe("カラオケ",    "ja")          # 가라오케 (어두 연음화)

# Level 3 — 옛한글 정밀 (한국어에 없는 소리 표기)
transcribe("vine",    "en", level=3)  # ㅸ아인  (ㅸ = /v/)
transcribe("zoo",     "en", level=3)  # ㅿ우    (ㅿ = /z/)
transcribe("father",  "en", level=3)  # ㆄ아더  (ㆄ = /f/)

# Level 4 — UHPS jamo 시퀀스 (ML / 연구용)
transcribe("student", "en", level=4)  # ㅅㅌㅠㄷㅓㄴㅌ
transcribe("中国",     "zh", level=4)  # ㅈㅜㅇㄱㅜㅓ
```

### CLI

```bash
$ hunmin --text "student" --lang en
스튜던트

$ hunmin --text "中国" --lang zh --level 4
ㅈㅜㅇㄱㅜㅓ

$ hunmin --web                        # Gradio 웹 UI 띄우기 (hunmin[demo] 필요)

$ hunmin --demo
lang  text                  L1 (아이용)     L3 (옛한글)     L4 (jamo)
=================================================================
en    student              스튜던트         스튜던트         ㅅㅌㅜㄷㅓㄴㅌ
en    father               파더            ㆄ아덜            ㆄㅏㄷㅓㄹ
es    familia              파밀리아         ㆄ아밀리아        ㆄㅏㅁㅣㄹㅣㅏ
ru    Москва               모스크바         모스크ㅸ아        ㅁㅗㅅㅋㅸㅏ
zh    中国                  중구어           중구어            ㅈㅜㅇㄱㅜㅓ
ja    東京                  토우쿄우         토우쿄우          ㅌㅗㅜㅋㅛㅜ
ko    大韓民國              대한민국         대한민국          ㄷㅐㅎㅏㄴㅁㅣㄴㄱㅜㄱ
...
```

---

## 🌐 지원 언어 (14개) — NIKL 외래어 표기 벤치마크

벤치는 두 가지 — **with overrides** (사용자 경험 정확도, dict+rule)와 **rule-only** (룰만의 한계, override 끄고).

| 코드 | 언어 | 방식 | with override / rule-only |
|---|---|---|---|
| `en` | 영어 | CMU(135K) + phonics + 합성어 + 약어 + 형태소 + NIKL 표기 | **98.5%** / 58.5% (265 단어) |
| `es` | 스페인어 | 글자 룰 + NIKL 표기 | **100%** / 95.0% (20 단어) |
| `fr` | 프랑스어 | 글자 룰 + NIKL 표기 | **100%** / 70.0% (20 단어) |
| `de` | 독일어 | 글자 룰 + NIKL 표기 | **100%** / 68.8% (16 단어) |
| `it` | 이탈리아어 | 글자 룰 + NIKL 표기 | **100%** / 61.1% (18 단어) |
| `ru` | 러시아어 (Cyrillic) | 글자 룰 + NIKL 표기 | **100%** / 75.0% (12 단어) |
| `pt` | 포르투갈어 | 글자 룰 + NIKL 표기 | **100%** / 55.6% (9 단어) |
| `nl` | 네덜란드어 | 글자 룰 + NIKL 표기 | **100%** / 66.7% (6 단어) |
| `pl` | 폴란드어 | 글자 룰 + NIKL 표기 | **100%** / 50.0% (4 단어) |
| `tr` | 터키어 | 글자 룰 + NIKL 표기 | 83.3% / 83.3% (6 단어) |
| `id` | 인도네시아어 | 글자 룰 + NIKL 표기 | **100%** / 80.0% (5 단어) |
| `ja` | 일본어 | pykakasi + NIKL 룰 (어두 연음/장음 드롭/접미사 한자 음독) | **92%** (도/현 71단어) |
| `zh` | 중국어 (북경어) | pypinyin + NIKL 표기 일람표 | **100%** (NIKL 표기 13단어) |
| `ko` | 한국어 (한글+한자) | hanja 사전 + native | 결정적 |

> NIKL 외래어 표기는 룰이 아니라 위원회 결정의 누적이라 100% 룰 도출이 본질적으로 불가능. `_HANGUL_OVERRIDES` 사전(529 entries en + 137 multi)이 그 갭을 메움. **UHPS Spec compliance**가 hunmin의 **진짜** 정확도이고, NIKL 벤치는 사용자 경험 보조 지표.

### 외부 평가 — Eastern European NIKL gold (leakage 0)

NIKL 외래어 표기 용례집 PDF (1299 entries, 동구권 10개 언어). 우리 패키지에 동구권 단어별 사전 없으므로 **누수 없는 진짜 외부 평가**: **11.5%** (사전+룰 전체).

| pl | ro | sl | hr | cs | sr | hu | sk | bs | mk |
|----|----|-----|-----|-----|-----|-----|-----|-----|-----|
| 16.8% | 15.6% | 18.8% | 12.1% | 8.7% | 7.7% | 2.5% | 4.3% | 9.7% | 11.8% |

낮은 게 정상 — NIKL 단어별 사전이 없는 영역에서 룰만의 한계. v3.x에서 추가 모듈로 점진적 보강 중.

---

## 🎚️ Level 1–4

| Level | 용도 | 예시: `student` |
|---|---|---|
| **1** | 어린이/일반 한글 | 스튜던트 |
| **2** | 자연스러운 발음 (연음 — 향후) | 스튜던트 |
| **3** | 정밀 (옛한글 ㆄ ㅸ ㅿ 사용) | (해당 음 없음) |
| **4** | UHPS 자모 시퀀스 (ML/오디오 연구) | ㅅㅌㅜㄷㅓㄴㅌ |

옛한글 예: `father` Level 1: 파더 vs Level 3: ㆄ아덜.
ㆄ가 /f/임을 명시 — /p/와 구별.

---

## 🧠 작동 원리

```
                ┌─────────────────────────┐
input + lang → │       Hunmin 라우터     │
                └──┬──────────────────┬───┘
                   ↓                  ↓
        Latin / Cyrillic       표의문자 (CJK)
        (en, es, it, de,       (ja, zh, ko)
         ru, fr, pt, nl,
         pl, tr, id)
                   ↓                  ↓
        언어별 룰 모듈            결정적 사전
        (글자 → 음소              (pykakasi /
         → 한글 / 자모)            pypinyin /
                                  hanja)
                   ↓                  ↓
                   └──── 출력 ────────┘
                  (한글 / 자모 / 분리)
```

**왜 하이브리드?** 표의문자(한자, 漢字)는 글자 자체에 발음 정보가 없습니다 — 사전 lookup이 정답.
표음문자(Latin, Cyrillic)는 글자→발음 규칙이 있습니다 — 알고리즘적 변환 가능.

### 영어 파이프라인 (4단계 fallback)

```
input word
   │
   ├─→ NIKL 외래어 표기 override?     ── yes ─→ 직접 매핑 (hello → 헬로)
   │
   ├─→ 약어? (대문자 또는 모음없음)    ── yes ─→ letter-by-letter (LSTM → 엘에스티엠)
   │
   ├─→ CMU 사전 (135K)                ── yes ─→ ARPABET → 한글 파이프라인
   │
   ├─→ 합성어 분해 (greedy split)     ── yes ─→ 부분 lookup 후 합침 (firebase → fire+base)
   │
   └─→ Phonics fallback (마지막)              → letter cluster pattern 매칭
```

ARPABET → 한글 파이프라인 내부:
- Letter alignment (CMU phs ↔ spelling letters)
- ER+'or' → AO+R 분리 (history → 히스토리)
- AA+'o' → ㅗ default (rock → 록, top → 톱)
- Yod 삽입 (T/D/N + UW → 튜/듀/뉴: student → 스튜던트)
- Postvocalic R drop (car → 카, hard → 하드)
- SH 팔라탈화 (shoe → 슈, shop → 숍)
- L 중복 (모음 사이 또는 어두 cluster: hello → 헬로, blue → 블루)
- K/T/P 받침 (짧은 모음 뒤만: back → 백, boat → 보트)
- 진짜 모음만 받침 허용 (ㅡ 충전모음 차단)

---

## 🔬 ML / 연구용

패턴 학습이 필요하면 Level 4 (자모 모드) 출력이 ML 파이프라인에 바로 들어갑니다.

```python
hunmin.transcribe("hello", "en", level=4)  # ㅎㅔㄹㅗㅜ
```

작은 transformer (~1.4M 파라미터) 한 개로 326K (text, jamo) 페어 학습하면
**테스트셋 97% exact / 99% char 정확도** 도달. (`docs/RESEARCH.md`).

---

## 📜 UHPS — Universal Hangul Phoneme Set (자모 45개)

| | 자음 (24) | 모음 (21) |
|---|---|---|
| 현대 | ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ | ㅏ ㅐ ㅑ ㅒ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅝ ㅞ ㅟ ㅠ ㅡ ㅢ ㅣ |
| 옛한글 | **ㆄ** /f/ · **ㅸ** /v/ · **ㅿ** /z/ · **ㆁ** /ŋ/ · **ㆆ** /ʔ/ | — |

같은 IPA → 모든 언어에서 같은 자모. *정확도보다 일관성* — ML 안정성을 위한 설계.

---

## 🏛️ 비전

> 어린이도 며칠 안에 익혀서 모든 소리를 적을 수 있게 하라.
> *Even a child should learn it in days, and use it to write any sound.*
> — 訓民正音 解例本, 1446

세종대왕이 의도했던 **"보편적 음성 표기 체계로서의 한글"** 부활.

---

## 🔖 강세 표기 컨벤션

UHPS-full(level=5)에서 강세 마크는 **점 직전 음절이 강세**:

```
허로·우  → '로' 강세 (옛 훈민정음 방점 방식)
```

이는 IPA의 `ˈ`(다음 음절 강세)와 반대 — 한국 전통 방점(傍點) 컨벤션을 따름.

## 📈 변경 이력 (CHANGELOG)

* **v3.15.0** (2026.05) — UHPS-full을 primary mode로 reframe + showcase
  * **README hero 재구성** — UHPS-full 중심, NIKL은 호환 layer로 강등
  * `docs/UHPS_FULL_SHOWCASE.md` — UHPS-full vs NIKL 비교, 옛한글 추정 가이드
  * 메시지: "NIKL 정확도는 hunmin 본질이 아니다. UHPS-full이 진짜 product."
* **v3.14.0** (2026.05) — Serbian Cyrillic rule (Vukov azbuka 트릭)
  * `hunmin/core/serbian.py` — 깔끔한 30줄: Cyrillic→Latin 1:1 변환 후 Croatian 룰 재사용
  * **Vukov azbuka principle**: Vuk Karadžić의 키릴 = Gaj의 라틴 (Љ↔Lj, Њ↔Nj, Ђ↔Đ, Ц↔C, Ч↔Č 등)
  * **EE_GOLD sr**: 7.7% → **25.6%** (+17.9pt)
  * **EE_GOLD mk**: 11.8% → **29.4%** (Macedonian Cyrillic도 sr 룰 라우팅)
  * `_PRECISE` 19 hardcoded langs (sr/mk 추가)
  * **EE_GOLD 전체: 18.5% → 19.8%**
  * 전체 테스트: **342 passed**
* **v3.13.0** (2026.05) — Croatian/Bosnian rule + Polish ły fix
  * `hunmin/core/croatian.py` — letter-by-letter NIKL 크로아티아어 룰 (Bosnian 공유)
  * 핵심: š/ž/č/ć→sibilants, lj/nj→palatal, đ/dj→ㅈ
  * **EE_GOLD bs**: 9.7% → **35.5%** (+25.8pt 최대 점프)
  * **EE_GOLD hr**: 12.1% → **19.0%** (+6.9pt)
  * Polish: ły → 위 (NIKL fix, 일부 영향)
  * `_PRECISE` 17 hardcoded langs (hr/bs 추가, bs는 hr 룰 공유)
  * **EE_GOLD 전체: 17.6% → 18.5%** (총 9.7% → 18.5%, v3.1 → v3.13)
  * 전체 테스트: **342 passed**
* **v3.12.0** (2026.05) — Romanian rule module
  * `hunmin/core/romanian.py` — letter-by-letter NIKL 루마니아어 룰
  * 핵심: ă→ㅓ, â/î→ㅡ, ș→ㅅ, **ț→ㅊ** (ts), c+e/i→ㅊ vs c→ㅋ, g+e/i→ㅈ vs g→ㄱ, ch/gh silent-h
  * **EE_GOLD ro**: 15.6% → **23.7%** (+8.1pt, 358 entries — 최대 절대 개선)
  * `_PRECISE` 15 hardcoded langs (ro 추가)
  * 전체 테스트: **342 passed**
* **v3.11.0** (2026.05) — Czech rule module
  * `hunmin/core/czech.py` — letter-by-letter NIKL 체코어 룰
  * 핵심: ch→흐, š→ㅅ, ž→주, č→ㅊ, **ř→ㅈ** (Czech 고유음), ť/ď/ň→palatal, ě→ㅖ
  * **EE_GOLD cs**: 8.7% → **15.7%** (+7.0pt)
  * `_PRECISE` 14 hardcoded langs (cs 추가)
  * 전체 테스트: **344 passed**
* **v3.10.0** (2026.05) — Slovak 룰 + Armenian/Georgian IPA + multilingual stress test
  * **`hunmin/core/slovak.py`** — letter-by-letter Slovak NIKL 룰 모듈
    * EE_GOLD sk: 4.3% → **13.0%** (+8.7pt)
    * 핵심: ch→흐, dž→주, š→ㅅ, ž→주, č→ㅊ, ť/ď/ň/ľ→palatal
  * **Armenian** letter→IPA 매핑 (43자) — `Հայաստան`, `Երևան` 등
  * **Georgian** letter→IPA 매핑 (33자) — `საქართველო`, `თბილისი` 등
  * Unicode P(unctuation) / S(ymbol) general category 자동 인식 — `¿`, `—`, `«»`, `©`, `™` 등
  * **`tests/test_stress.py`** — 80+ entries × 20+ scripts/언어 leak 0 검증
  * Symbol 감지 로직 보강: 매핑에 없는 char는 strict=True 시 leak로 추적
  * `_PRECISE` 13 hardcoded langs (sk 추가)
  * 전체 테스트: **344 passed** (+80)
* **v3.9.0** (2026.04) — `transcribe_auto` 정착: tests + Hebrew + CLI + HF tab
  * **`tests/test_auto.py`** — 34 regression tests (script routing, mixed, leak, digits, symbols, strict, mode, determinism)
  * **Hebrew letter→IPA** — `שלום`, `תודה`, `ירושלים` 등 epitran 없이 인코딩
  * **Audit ar/hi/th**: Arabic short vowel 손실 (마르하바→믈바, epitran 한계), Hindi 70%, Thai 85% 정확도 기록
  * **CLI `--auto`** — `hunmin --auto --text "Hello 中国 5"` 으로 mixed-script 처리
  * **CLI `--digits/--symbols/--strict`** flags
  * **HF Space**: 4 tabs (Auto / Multi-view / Levels / Tokens). Auto 탭에 mode, digits, symbols 옵션
  * 전체 테스트: **264 passed** (이전 230 → +34)
* **v3.8.1** (2026.04) — Greek IPA fallback (epitran 없는 언어 지원 패턴)
  * Greek (`Καλημέρα`) — letter→IPA 매핑 후 `lang='ipa'` 경로로 전사
  * **패턴 정립**: epitran 매핑 없는 언어 = letter→IPA 헬퍼만 작성하면 무한 확장
  * `Καλημέρα` → 카리메라, `Σωκράτης` → 솤라팃, `Ωμέγα` → 오메하
  * Greek strict=True 통과 (이전엔 ValueError)
* **v3.8.0** (2026.04) — Mixed-script auto-routing + digit/symbol 인코딩 — **leak 0 보장**
  * `transcribe_auto(text, primary_lang='en', mode=...)` — 모든 입력 100% UHPS 공간으로
  * **스크립트별 chunk 자동 분리** — Latin/Cyrillic/Greek/Arabic/Devanagari/Thai/CJK/Hiragana/Katakana/Hangul
  * **CJK 휴리스틱**: 텍스트에 hiragana/katakana 있으면 → ja, 아니면 → zh
  * **Vietnamese 감지**: Latin Extended Additional 진단으로 → vi 라우팅
  * **숫자 transliteration** `digits=`: `'sino'` (5→오, default), `'native'` (5→다섯), `'read'` (영어 5→파이브), `'keep'`
  * **기호 transliteration** `symbols=`: `'kor'` (default, &→앤드, $→달러), `'drop'`, `'keep'`
  * **strict=True**: 인코딩 못한 글자 발견 시 ValueError (학습 데이터 검증용)
  * 검증 (모두 leak 0):
    * `'Hello 中国 5 apples'` → `'헬로 중궈 오 애펄즈'`
    * `'A&B Corp. $100'` → `'아앤드비 콥. 달러일영영'`
    * `'COVID-19 (2024)'` → `'씨오브이아이디-일구 (이영이사)'`
    * `'I love 한국 & Japan'` → `'아이 러브 한국 앤드 재팬'`
  * 전체 테스트: **230 passed**
* **v3.7.0** (2026.04) — 모든 룰 모듈 phonetic= 인자 통일
  * 11개 룰 모듈 (en/es/fr/de/it/ru/pt/nl/pl/tr/id) 모두 `phonetic=False` 기본값 추가
  * **English `_HANGUL_OVERRIDES` skip 활성화** — phonetic=True면 NIKL 사전 우회
  * 검증: `pizza` 피자(NIKL) vs **피트사**(phonetic), `mozart` 모차르트 vs **모잣**, `einstein` 아인슈타인 vs **아인스타인**
  * 11 모듈 + hu(prototype) = 12개 모듈 모두 5-mode API와 호환
  * 전체 테스트: **230 passed**
* **v3.6.0** (2026.04) — 5 explicit modes: HUNMIN/UHPS layer 분리
  * **5개 mode 상수 도입** — `HUNMIN_NIKL`, `HUNMIN_PHONETIC`, `UHPS_CORE`, `UHPS_JAMO`, `UHPS_FULL`
  * `transcribe(text, lang, mode=HUNMIN_PHONETIC)` — 음운 정확도 우선 (NIKL adapter OFF)
  * `transcribe(text, lang, mode=HUNMIN_NIKL)` — NIKL 외래어 표기법 (default)
  * **Hungarian prototype**: `Buda` → 부**더** (NIKL) vs 부**다** (phonetic), `Baranya` → **버러녀** vs **바라냐**
  * `_LANG_OVERRIDES` 사전 skip when phonetic=True (NIKL 단어별 굳어진 표기 미적용)
  * 모듈 옵트인 (hu 완료, en/es/fr 등 차후)
  * `level=` 인자 backward compat 유지
  * 전체 테스트: **230 passed**

```python
# 5 modes, explicit
from hunmin import transcribe, HUNMIN_NIKL, HUNMIN_PHONETIC, UHPS_CORE, UHPS_JAMO, UHPS_FULL
transcribe('Baranya', 'hu', mode=HUNMIN_NIKL)      # → 버러녀 (NIKL)
transcribe('Baranya', 'hu', mode=HUNMIN_PHONETIC)  # → 바라냐 (음운)
transcribe('Buda', 'hu', mode=UHPS_CORE)           # → 부더 (옛한글 코드)
transcribe('Buda', 'hu', mode=UHPS_FULL)           # → 부더 (+운율)
```

* **v3.5.0** (2026.04) — Hungarian rule module
  * `hunmin/core/hungarian.py` — letter-by-letter NIKL 헝가리어 룰
  * 핵심: a → ㅓ (Hu /ɒ/), á → ㅏ, cs → ㅊ, gy → 죠/져, ny → 녀/뇨, sz → ㅅ, zs → 주, ly → 야/요
  * Geminate 자음 흡수 (tt/nn/ll → 받침 또는 단일)
  * Palatalization: ny+a → 녀, gy+a → 쟈, ty+a → 탸 등
  * **EE_GOLD hu**: 2.5% → **19.1%** (v3.4 → v3.5, +16.6pt — Hungarian 룰 모듈)
  * `_PRECISE` 라우팅에 hu 추가 (12 hardcoded langs)
  * 전체 테스트: **230 passed**
* **v3.4.0** (2026.04) — 만다린 ze fix + Vietnamese/Hu/Sk overrides + held-out 확장
  * **만다린 ze→쩌 NIKL 정정** — 毛泽东 마오저둥 → **마오쩌둥** (NIKL 외래어 표기 표준)
    * 전체 매핑: ze 쩌, zei 쩨이, zen 쩐, zeng 쩡 (z-front-vowel rule)
  * **Vietnamese (vi)** override 추가 — 38개 (Hà Nội, Hồ Chí Minh, xin chào, Nguyễn 등)
  * **Hungarian (hu)** override 추가 — Budapest, Debrecen, Kossuth 등
  * **Slovak (sk)** override 추가 — Bratislava, Košice, Tatry 등
  * `_LANG_OVERRIDES` 라우팅 — `_PRECISE` 룰 모듈 없는 언어도 override 적용
  * **en_heldout_diverse.tsv** — 92 다양한 외래어 (42 진짜 held-out): **64.3%** (vs en_gold 97.8%)
  * 전체 테스트: **230 passed** (xfail 0)
* **v3.3.0** (2026.04) — Held-out 정확도 + UHPS 자모 확장 + CJK regression
  * **Held-out gold** (override-free): 영어 97.8% (45) / 다국어 100% (15) — 진짜 룰 정확도
  * IPA 자모 매핑 16개 추가: retroflex (ʈ ɖ ɳ), palatal (c ɟ ʝ), uvular (ɢ ʙ), 중설모음 (ɘ ɜ ɞ), 등
  * **UHPS Spec compliance**: 95/95 tests (100%)
  * **CJK regression test**: 31 passed + 1 xfailed (毛泽东 ze→쩌 known gap)
  * 전체 테스트: **229 passed**
  * README 정확도 정정: 사용자 경험 vs 룰만 vs 외부 평가 분리
* **v3.2.0** (2026.04) — 동구권 fallback + 약어 사전
  * `_ISO_TO_EPITRAN`에 linguistic-neighbor fallback 추가 — sk→cs, bs→hr, mk→sr, me→sr, be→ru, bg→ru
  * `_GEO_ABBREV` 지명 약어 사전: R.→강, Mts.→산맥, Is.→섬, L.→호, Cape→곶, Bay→만 등
  * EE_GOLD 1299-entry 벤치: 9.7% → 11.5% (+23 correct)
  * 가장 큰 개선: bs 0→9.7%, mk 0→11.8%, sk 0→4.3%, sl 6.2→18.8%, hr 6.9→12.1%
* **v3.1.0** (2026.04) — Tone renderer 정식화 (UHPS_SPEC §5)
  * 5-way tone category: H (high), R (rising), D (dipping), F (falling), L (low)
  * **Mandarin 4성 distinct 보장** — 이전엔 1=4=H, 2=3=R로 머지되던 것 → 4개 모두 분리
  * 새 tone_style: **`arrow`** (¯ ↗ ↘↗ ↘ ↓), **`numeric`** (¹ ² ³ ⁴ ₁)
  * Vietnamese 6 tones — NFD 분해로 결합 마크(́ ̀ ̉ ̣) 인식
    * á(sắc)→H, à(huyền)→L, ả(hỏi)→D, ạ(nặng)→F
  * IPA tone bar pattern 매칭: `˨˩˦` → D (long-first 우선)
  * 검증: `ma˨˩˦` → arrow `마↘↗` / numeric `마³` / panjeom `마〯〮`
* **v3.0.1** (2026.04) — UHPS-code vs HUNMIN-readable 명시 + 6-view API
  * UHPS_SPEC §1.0: "UHPS는 코드, HUNMIN은 사람 읽기" 핵심 구분 박음
  * 한글 완성형 본질적 제약 명시 (ㅂ+ㆎ는 영구히 분리 표시)
  * `views(text, lang, meaning=...)` API 추가 — 6-view dict 반환
    * keys: text, lang, ipa, uhps_core, uhps_full, hunmin, meaning
    * UHPS-code는 강제로 epitran/IPA 경로로 라우팅 (옛한글/방점 보존)
  * CLI: `--views` 플래그 + `--meaning` 옵션
* **v3.0.0** (2026.04) — Spec freeze + ML token layer
  * `docs/UHPS_SPEC.md` — 정식 spec 문서. IPA → UHPS 매핑이 코드 밖에서 동결됨
  * **Token-layer API 노출** — `transcribe(..., return_tokens=True)` (UHPS_SPEC §6)
    * 추상 토큰 시퀀스 `[(KIND, value, ...), ...]` 반환
    * KIND: C / OLD / V / V_NASAL / V_R / SV_MARKER / SUPRA / SPACE / PUNCT
    * 임의 언어 → 동일 음소 공간 투영 (ML 학습용)
  * **CLI**: `--tokens` + `--format text/json/jsonl` 추가
  * `'en'` ISO 코드를 universal map에 추가 (`return_tokens=True` 시 epitran 경로)
  * Tone system v3.0 정책: prosodic layer로 보존만, 본 자모와 머지 안 함. 정식 renderer는 v3.1
* **v2.4.4** (2026.04) — affricate digraph 보강
  * `tɕ`/`dʑ` (alveolo-palatal, 베트남어 ch / 만다린 j·q) → ㅊ/ㅈ로 정규화
  * `tʂ`/`dʐ` 및 `ʈʂ`/`ɖʐ` (retroflex, 만다린 zh·ch / 폴란드어 cz) → ㅊ/ㅈ
  * tie bar (U+0361) 유무 모두 인식: `t͡ɕ`, `d͡ʑ`, `ʈ͡ʂ`, `ɖ͡ʐ`, `t͡s`, `d͡z`
  * 예: 베트남어 `xin chào` `/sin tɕaːw/` → `신 차ː으` (이전: `신 트사으`)
* **v2.4.3** (2026.04) — 강세 attach bug fix
  * 강세는 자음(ㆄㅸㅿ 등)이 아닌 **모음**에만 attach
  * default tone_style을 `middledot` (·)로 — 한글 시각 호환
  * 폰트 호환 fallback (safe_fonts 기본 True): ᄛ→ㄹ, ᄾ→ㅅ, ᄶ→ㅈ
* **v2.4** (2026.04) — UHPS-core / UHPS-full 분리
  * `level=3` (UHPS-core): 자음/모음 1:1 (옛한글 13개 추가 jamo)
  * `level=5` (UHPS-full): + 장단/성조/강세/방점 모두 보존
    * 거성 (high stress) → 〮 (U+302E)
    * 상성 (rising tone) → 〯 (U+302F)
    * 장음 → ː
  * 예: `niːd` → core `닏`, full `니ː드`
* **v2.3** (2026.04) — API 정리 + 톤 다운
  * `supported_languages('hardcoded'|'universal'|'all')` 계층화
  * Universal 121 epitran code 모두 smoke test 통과 검증
  * README 정확화 (`lang='ipa'`는 IPA로 표기 가능한 모든 언어 지원으로 표현)
* **v2.2** (2026.04) — UHPS v2 + IPA 직접 입력 모드
  * 옛한글 + 한글자모확장으로 IPA → 한글 1:1 매핑
  * `lang='ipa'`로 IPA 문자열 직접 입력 (의존성 0)
  * /θ/→ㅼ, /ð/→ㅽ, /ʃ/→ᄾ, /ʒ/→ᄶ, /x/→ㆅ, /ʁ/→ᄛ, /ɲ/→ㅥ, /ɑ/→ㆍ, /ɔ/→ㆎ
* **v2.1** (2026.04) — Universal IPA transcriber via epitran
  * **100+ 언어 추가**: 132 ISO 코드 → 121 unique epitran 매핑
  * 카탈루냐/웨일스/아일랜드/바스크/몰타/그리스 등 유럽 추가 언어
  * 베트남/태국/힌디/타밀/텔루구/말라얄람/벵골/펀자비 등 아시아
  * 아랍/페르시아/우르두/암하라/티그리야 등 셈/에티오피아
  * 줄루/요루바/이그보/스와힐리/르완다/하우사 등 아프리카
  * 카자흐/키르기스/우즈벡/위구르/투르크멘 등 튀르크
  * 광둥어/민난어/우어/객가어 등 중국 방언
  * 마오리/케추아/하이티 크리올 등 토착어
  * 설치: `pip install hunmin[universal]` (epitran 옵션)
* **v1.10** (2026.04) — CJK NIKL 외래어 표기법 본격 적용
  * **일본어**: 어두 t/k/p → ㄷ/ㄱ/ㅂ (도쿄, 교토, 고베, 가라오케)
  * **일본어**: 장음 드롭 (ou/oo/uu/aa/ii/ee → 단모음). 토우쿄우 → 도쿄
  * **일본어**: 행정 접미사 한자 음독 (県→현, 府→부, 区→구)
  * **일본어**: tsu → 쓰 (NIKL 표준), 인명 名 첫자 어두 연음화
  * **일본어**: 자주 쓰이는 표현 직접 매핑 (こんにちは→곤니치와, 東京都→도쿄도)
  * **중국어**: NIKL pinyin → 한글 표 410 음절 재작성 (uo→ㅝ, sh-→상/성, xue→쉐, you→유)
  * 中国 → 중궈, 上海 → 상하이, 习近平 → 시진핑 (이전 중구어/샹하이는 깨진 출력)
* **v1.8** (2026.04) — 다국어 폴리싱 + 데모 + Syllabic schwa
  * **영어 syllabic /n/, /m/, /l/** — button → 버튼, bottle → 보틀, table → 테이블, rhythm → 리듬
  * **다른 10개 언어 NIKL override** — 100% 다국어 벤치 (116 단어, fr/de/it/es/ru/pt/nl/pl/tr/id)
  * **Gradio 웹 데모** — `hunmin --web` 또는 `pip install hunmin[demo]`
  * **README 정비** — CHANGELOG, 배지, 다국어 벤치 결과
* **v1.6** — ML fallback (옵션) + 형태소 분해
  * 형태소 fallback — reproducible → re+produce+ible, preprocessing → pre+processing
  * `pip install hunmin[ml]` → g2p-en 신경망 G2P 활성화 (옵션)
* **v1.5** — 다국어 폴리싱 (fr/it/de/es/ru/pt/nl/pl/tr/id NIKL 표기)
* **v1.4** — Override 사전 150 → 515 단어 확장
* **v1.3** — 영어 파이프라인 대폭 강화 (97.3% NIKL 벤치)
  * 풀 CMU 사전 번들 (135K)
  * Phonics fallback / 합성어 분해 / 약어 letter-by-letter
  * Letter alignment 기반 spelling-aware 모음 (history → 히스토리)
  * Yod 삽입 (student → 스튜던트), SH 팔라탈화 (sugar → 슈거)
* **v1.0** — 14개 언어, 하이브리드 파이프라인, UHPS freeze.

---

## 📝 라이선스

MIT.

---

## 🙏 사용 도구

* `pykakasi` — 일본어 가나 변환
* `pypinyin` — 중국어 병음
* `hanja` — 한국어 한자음
* CMU Pronouncing Dictionary — 영어 G2P
* hermitdave/FrequencyWords — corpus seed (OpenSubtitles)
