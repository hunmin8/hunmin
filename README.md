# 🎼 Hunmin

> **외국어를 한글로 — 아이도 읽을 수 있는 발음 악보**
> *Convert any language into a readable phonetic Hangul score.*

```python
from hunmin import transcribe

transcribe("student", "en")        # 스투던트
transcribe("中国",     "zh")        # 중구어
transcribe("東京",     "ja")        # 토우쿄우
transcribe("familia", "es", level=3)   # ㆄ아밀리아  (옛한글 ㆄ = /f/)
transcribe("Москва",  "ru", level=4)   # ㅁㅗㅅㅋㅸㅏ  (UHPS jamo)
```

**14개 언어**. **순수 룰 기반**. **의존성 0** (CJK는 선택적).

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
transcribe("student", "en")           # 스투던트
transcribe("Paris",   "fr")           # 파리
transcribe("中国",     "zh")           # 중구어
transcribe("こんにちは",   "ja")           # 콘니치하

# Level 3 — 옛한글 정밀 (한국어에 없는 소리 표기)
transcribe("vine",    "en", level=3)  # ㅸ아인  (ㅸ = /v/)
transcribe("zoo",     "en", level=3)  # ㅿ우    (ㅿ = /z/)
transcribe("father",  "en", level=3)  # ㆄ아덜  (ㆄ = /f/)

# Level 4 — UHPS jamo 시퀀스 (ML / 연구용)
transcribe("student", "en", level=4)  # ㅅㅌㅜㄷㅓㄴㅌ
transcribe("中国",     "zh", level=4)  # ㅈㅜㅇㄱㅜㅓ
```

### CLI

```bash
$ hunmin --text "student" --lang en
스튜던트

$ hunmin --text "中国" --lang zh --level 4
ㅈㅜㅇㄱㅜㅓ

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

## 🌐 지원 언어 (14개)

| 코드 | 언어 | 방식 | 정확도 |
|---|---|---|---|
| `en` | 영어 | CMU 사전 + 룰 | 100% (사전 내) |
| `es` | 스페인어 | 글자 룰 | 99.9% |
| `it` | 이탈리아어 | 글자 룰 | 99.8% |
| `de` | 독일어 | 글자 룰 | 99.0% |
| `ru` | 러시아어 (Cyrillic) | 글자 룰 | 100.0% |
| `fr` | 프랑스어 | 글자 룰 | 99.8% |
| `pt` | 포르투갈어 | 글자 룰 | 99.8% |
| `nl` | 네덜란드어 | 글자 룰 | 99.6% |
| `pl` | 폴란드어 | 글자 룰 | 99.4% |
| `tr` | 터키어 | 글자 룰 | 100.0% |
| `id` | 인도네시아어 | 글자 룰 | 99.4% |
| `ja` | 일본어 | pykakasi + 룰 | 100% |
| `zh` | 중국어 (북경어) | pypinyin + 룰 | 100% |
| `ko` | 한국어 (한글+한자) | hanja + native | 100% |

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

## 📈 현재 상태

* **v1.0** — 14개 언어, 하이브리드 파이프라인, 테스트 정확도 98.4%, UHPS freeze.

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
