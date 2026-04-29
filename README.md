# 🎼 Hunmin

[![PyPI](https://img.shields.io/pypi/v/hunmin)](https://pypi.org/project/hunmin/)
[![Python](https://img.shields.io/pypi/pyversions/hunmin)](https://pypi.org/project/hunmin/)
[![License](https://img.shields.io/pypi/l/hunmin)](https://github.com/meshpop/hunmin/blob/main/LICENSE)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/foolsai/hunmin)

> **외국어를 한글로 — 아이도 읽을 수 있는 발음 악보**
> *Convert any language into a readable phonetic Hangul score.*

**[🎼 온라인 데모 사용해보기](https://huggingface.co/spaces/foolsai/hunmin)**

```python
from hunmin import transcribe

transcribe("student", "en")        # 스튜던트
transcribe("hello",   "en")        # 헬로
transcribe("中国",     "zh")        # 중구어
transcribe("東京",     "ja")        # 토우쿄우
transcribe("familia", "es", level=3)   # ㆄ아밀리아  (옛한글 ㆄ = /f/)
transcribe("Москва",  "ru", level=4)   # ㅁㅗㅅㅋㅸㅏ  (UHPS jamo)
transcribe("LSTM",    "en")        # 엘에스티엠 (약어 자동 인식)
transcribe("firebase","en")        # 파이어베이스 (합성어 분해)
```

**14개 언어**. **순수 룰 기반**. **의존성 0** (CJK는 선택적).
**영어 98.5%** (265단어), **다른 10개 언어 100%** (116단어) — NIKL 외래어 표기 벤치.

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
pip install hunmin              # 11개 (Latin/Cyrillic 언어)
pip install hunmin[cjk]         # + 일본어 / 중국어 / 한국어
pip install hunmin[all]         # 모두 + 웹 데모
```

---

## 🚀 빠른 시작

### Python

```python
from hunmin import transcribe

# 기본 — 아이용 한글
transcribe("student", "en")           # 스튜던트
transcribe("hello",   "en")           # 헬로
transcribe("Paris",   "fr")           # 파리
transcribe("中国",     "zh")           # 중구어
transcribe("こんにちは",   "ja")           # 콘니치하

# 영어 고급 — CMU 사전 + phonics + 합성어 + 약어 자동
transcribe("anthropic","en")          # 앤스라픽 (CMU 미수록 → phonics)
transcribe("typescript","en")         # 타이프스크립트 (합성어 분해)
transcribe("USA",      "en")          # 유에스에이 (대문자 약어 letter-by-letter)
transcribe("LSTM",     "en")          # 엘에스티엠 (모음 없는 토큰)

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

| 코드 | 언어 | 방식 | 벤치 정확도 |
|---|---|---|---|
| `en` | 영어 | CMU(135K) + phonics + 합성어 + 약어 + 형태소 + NIKL 표기 | **98.5%** (265 단어) |
| `es` | 스페인어 | 글자 룰 + NIKL 표기 | **100%** (20 단어) |
| `fr` | 프랑스어 | 글자 룰 + NIKL 표기 | **100%** (20 단어) |
| `de` | 독일어 | 글자 룰 + NIKL 표기 | **100%** (16 단어) |
| `it` | 이탈리아어 | 글자 룰 + NIKL 표기 | **100%** (18 단어) |
| `ru` | 러시아어 (Cyrillic) | 글자 룰 + NIKL 표기 | **100%** (12 단어) |
| `pt` | 포르투갈어 | 글자 룰 + NIKL 표기 | **100%** (9 단어) |
| `nl` | 네덜란드어 | 글자 룰 + NIKL 표기 | **100%** (6 단어) |
| `pl` | 폴란드어 | 글자 룰 + NIKL 표기 | **100%** (4 단어) |
| `tr` | 터키어 | 글자 룰 + NIKL 표기 | **100%** (6 단어) |
| `id` | 인도네시아어 | 글자 룰 + NIKL 표기 | **100%** (5 단어) |
| `ja` | 일본어 | pykakasi 가나 + 결정적 룰 | 결정적 |
| `zh` | 중국어 (북경어) | pypinyin 병음 + 결정적 룰 | 결정적 |
| `ko` | 한국어 (한글+한자) | hanja 사전 + native | 결정적 |

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

## 📈 변경 이력 (CHANGELOG)

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
