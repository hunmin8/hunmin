# UHPS Specification — Universal Hangul Phoneme Set

**Version**: 3.32 (extended with showcase §9.4)
**Status**: Frozen core (v3.0) + ongoing nasal/palatalization refinements
**Reference implementation**: `hunmin/core/universal.py`
**Regression lock-in**: `tests/gold/uhps_external.jsonl` (143) + `tests/gold/uhps_showcase.jsonl` (40)

---

## 1. 개요

UHPS (Universal Hangul Phoneme Set)는 IPA 음소를 한글 자모(현대 + 옛한글)에 **1:1 매핑하는 음소 코드**다. 본 문서가 표준이며, 코드는 표준의 구현체다. 두 사이에 차이가 있으면 본 문서가 우선한다.

### 1.0 핵심 구분 — UHPS는 코드, HUNMIN은 읽기

> **UHPS는 "한글로 보이는 음소 코드"이지 "한국어 문장"이 아니다.**

같은 단어를 두 layer로 분리한다:

| Layer | 무엇 | 예 (Bonjour) | 용도 |
|-------|------|-------------|------|
| TEXT | 원문 | `Bonjour` | 의미 입력 |
| IPA | IPA 표준 | `bɔ̃ʒuʁ` | 원 기준 |
| **UHPS-code** | 정밀 음소 코드, 음절 합성 보장 안 함 | `ㅂㆎᄶ우ᄛ` | ML 학습/임베더 |
| **HUNMIN** | 사람이 읽는 한글 (NIKL 외래어 표기법) | `봉주르` | UI/문서/음역 |
| MEANING | 의미 anchor | `안녕하세요` | 의미 정렬 |

**왜 UHPS는 음절로 안 합쳐지는가**: 현대 한글 완성형은 `19 초성 × 21 중성 × 28 종성 = 11172`로 미리 정의된 집합. 이 21 중성에 ㆎ·ㆍ가 없고 28 종성에 ㅥ·ㆁ가 없다. 따라서 `ㅂ+ㆎ`, `제+ㅥ`은 유니코드상 precomposed syllable이 존재하지 않아 영구히 분리 표시된다. **이것은 폰트/렌더링 문제가 아니라 한글 완성형의 경계**이며, UHPS가 옛한글/확장자모를 들이는 순간 본질적으로 발생하는 trade-off다.

따라서:
- 사람에게 보여줄 때는 항상 **HUNMIN과 함께** 표시한다.
- ML 학습/임베더에는 UHPS-code가 오히려 안정적이다 (자모 분리가 모델에는 명확한 신호).
- 표/UI에는 5-view 포맷 권장: `TEXT / IPA / UHPS-code / HUNMIN / MEANING`.

### 1.1 설계 목표

1. **무손실(가능한 한)**: IPA로 변별 가능한 음소는 UHPS에서도 변별
2. **결정론적**: 같은 IPA 입력은 항상 같은 UHPS 출력
3. **ML 친화**: 토큰 시퀀스로 노출 가능, 임의 언어 → 동일 음소 공간 투영
4. **층화**: 분절(자음/모음) ↔ 초분절(장단/강세/성조)을 layer 분리
5. **HUNMIN 분리**: 사람 읽기는 별도 layer (level=1, NIKL 친화)

### 1.2 비목표

- IPA의 모든 변별 자질을 1:1 보존 (자모 수 부족으로 본질적으로 lossy)
- 정자법(orthography) — UHPS는 음소 코드일 뿐 한국어 정자법이 아님
- **음절 합성 보장** — UHPS-code는 자모 시퀀스이지 합성형 한글 문장이 아님
- 운율(prosody) 완전 표현 — v3.0은 분절 중심, 초분절은 v3.1 renderer

---

## 2. 레벨 정의

| Level | 이름 | 자모 | 옛한글 | 초분절 | 용도 |
|-------|------|------|--------|--------|------|
| 1 | Children | 현대 | × | × | 외래어 표기 (대중) |
| 2 | Natural | 현대 | × | × | (예약, 1과 동일) |
| 3 | UHPS-core | 현대 + 옛한글 | ✓ | × | 음소 정밀 |
| 4 | Jamo sequence | 분리 자모 | ✓ | × | ML 입력 |
| 5 | UHPS-full | 현대 + 옛한글 | ✓ | ✓ | 운율 보존 |

레벨 3·5만이 UHPS proper다. 1·2는 외래어 표기법 친화 단순화, 4는 4번 시퀀스 형태.

---

## 3. IPA → UHPS 매핑표

### 3.1 자음 — 폐쇄음 (plosives)

| IPA | UHPS | 비고 |
|-----|------|------|
| p | ㅍ | |
| b | ㅂ | |
| t | ㅌ | |
| d | ㄷ | |
| k | ㅋ | |
| ɡ / g | ㄱ | |
| q | ㅋ | uvular k → k 머지 (※ 머지 #1) |
| ʔ | ㆆ | 옛한글 여린히읗 |
| ɓ ɗ ɠ | ㅂ ㄷ ㄱ | implosive → plain (※ 머지 #2) |

### 3.2 자음 — 비음 (nasals)

| IPA | UHPS | 비고 |
|-----|------|------|
| m | ㅁ | |
| n | ㄴ | |
| ɲ | ㅥ | 옛한글 쌍니은 (palatalize next vowel) |
| ŋ | ㆁ | 옛한글 옛이응 |
| ɴ | ㆁ | uvular n → ŋ 머지 (※ 머지 #3) |
| ɱ | ㅱ | 옛한글 미음+이응 |

### 3.3 자음 — 마찰음 (fricatives)

| IPA | UHPS | 비고 |
|-----|------|------|
| f | ㆄ | 옛한글 피읖+이응 |
| v | ㅸ | 옛한글 비읍+이응 |
| ɸ β | ㆄ ㅸ | bilabial → labiodental 머지 (※ 머지 #4) |
| s | ㅅ | |
| z | ㅿ | 옛한글 반시옷 |
| θ | ㅼ | 옛한글 시옷+디귿 (영어 think) |
| ð | ㅽ | 옛한글 시옷+비읍 (영어 this) |
| ʃ | ᄾ | 치두음 시옷 |
| ʒ | ᄶ | 치두음 지읒 |
| ɕ | ᄾ | alveolo-palatal s → ʃ 머지 (※ 머지 #5) |
| ʑ | ᄶ | alveolo-palatal z → ʒ 머지 |
| ʂ | ᄾ | retroflex s → ʃ 머지 |
| ʐ | ᄶ | retroflex z → ʒ 머지 |
| h ɦ | ㅎ | |
| x | ㆅ | 옛한글 쌍히읗 |
| ɣ | ㆅ | voiced velar → x 머지 |
| ç | ㆅ | German ich → x 머지 (※ 머지 #6) |
| χ | ㆅ | uvular x → x 머지 |
| ħ | ㆅ | Arabic pharyngeal → x 머지 (※ 머지 #6) |
| ʁ | ᄛ | 옛한글 가벼운 ㄹ (French R) |
| ʀ | ᄛ | uvular trill → ʁ 머지 |
| ʕ | ㆆ | Arabic 'ayn → ʔ 머지 (※ 머지 #7) |

### 3.4 자음 — 파찰음 (affricates)

| IPA | UHPS | 비고 |
|-----|------|------|
| ʧ / tʃ / t͡ʃ | ㅊ | |
| ʤ / dʒ / d͡ʒ | ㅈ | |
| ʦ / ts / t͡s | ㅊ | (※ 머지 #8) |
| ʣ / dz / d͡z | ㅈ | |
| tɕ / t͡ɕ | ㅊ | alveolo-palatal → ㅊ 머지 (Mandarin j/q, Vietnamese ch) |
| dʑ / d͡ʑ | ㅈ | |
| tʂ / t͡ʂ / ʈʂ / ʈ͡ʂ | ㅊ | retroflex → ㅊ 머지 (Mandarin zh) |
| dʐ / d͡ʐ / ɖʐ / ɖ͡ʐ | ㅈ | |

### 3.5 자음 — 유음·접근음

| IPA | UHPS | 비고 |
|-----|------|------|
| l ɭ ɮ ʎ | ㄹ | (※ 머지 #9) |
| r ɾ ɹ ɽ | ㄹ | (※ 머지 #9) |
| j | y-glide | 다음 모음과 결합 (ㅏ→ㅑ) |
| w | w-glide | 다음 모음과 결합 (ㅏ→ㅘ) |
| ɥ | y-glide | rounded j → j 머지 |
| ʋ | ㅸ | labiodental approximant → v 머지 |

### 3.6 모음 — 평순

| IPA | UHPS | 비고 |
|-----|------|------|
| i ɪ | ㅣ | (※ 머지 #10) |
| e ɛ | ㅔ | |
| æ | ㅐ | |
| a ɐ | ㅏ | |
| ə ɵ ʌ | ㅓ | |
| ɨ ʉ ɯ | ㅡ | |
| u ʊ | ㅜ | |
| o | ㅗ | |
| ɔ | ㆎ | 옛한글 아래아+이 |
| ɑ ɒ | ㆍ | 옛한글 아래아 |
| ɤ | ㅓ | back unrounded → ə 머지 |

### 3.7 모음 — 원순(전설)

| IPA | UHPS | 비고 |
|-----|------|------|
| y ʏ | ㅟ | |
| ø | ㅚ | |
| œ | ㅙ | |

### 3.8 모음 — R-colored / Nasal

| IPA | UHPS | 비고 |
|-----|------|------|
| ɚ ɝ | ㅓ + r | 영어 butter, bird |
| ã | ㅏ + ㆁ | 비음 모음 → 모음 + ŋ |
| ɛ̃ | ㅔ + ㆁ | |
| ɔ̃ | ㆎ + ㆁ | |
| œ̃ | ㅙ + ㆁ | |

---

## 4. 의도된 머지 (Intentional Mergers)

UHPS는 IPA보다 자모 수가 적어 일부 변별을 머지한다. 다음 머지는 **의도된 것이며 v3.x 동안 유지**한다.

| # | 머지 | 이유 |
|---|------|------|
| 1 | q → k | uvular vs velar: 한국어 화자에게 변별 어려움. NIKL 외래어법 동일. |
| 2 | implosive → plain | ɓ ɗ ɠ는 일부 아프리카 언어에만 출현, 한글 자모에 대응 없음. |
| 3 | ɴ → ŋ | uvular n은 매우 드묾, 한글에 대응 없음. |
| 4 | bilabial f/v → labiodental | 일본어/스페인어 변이음 수준, 한글 자모에 대응 없음. |
| 5 | ɕ ʂ ʃ → ᄾ (그리고 ʑ ʐ ʒ → ᄶ) | 알베올로팔라탈/리트로플렉스/포스트앨비올라 마찰음. 변별 자모 부족. |
| 6 | ç ħ χ x → ㆅ | palatal/pharyngeal/uvular/velar 무성 마찰음 모두 ㆅ. 한글 화자에겐 모두 "강한 ㅎ". |
| 7 | ʕ → ㆆ | Arabic 인두음 유성, 한글에 적절한 자모 없음. ʔ로 근사. |
| 8 | ʦ ts → ㅊ | 한국어에는 ts가 ㅊ로 흡수됨. NIKL 외래어법 동일. |
| 9 | l/r/ɾ/ɹ → ㄹ | 한국어는 l/r 변별 없음. 어두/어말 변이음 처리만 있음. |
| 10 | i ɪ → ㅣ, ʊ u → ㅜ | tense/lax 모음 변별 없음. NIKL 동일. |

이 머지들은 spec freeze이며 변경 시 major version (4.0) 필요.

---

## 5. 초분절 (Suprasegmental) — v3.0 정책

v3.0에서는 초분절을 **별도 layer로 보존만** 하고, 본 자모 기호와 머지하지 않는다.

### 5.1 Tone categories — 5-way (v3.1)

UHPS-full은 IPA 톤 정보를 5 abstract category로 압축한 뒤 tone_style에 따라 시각화한다.

| Category | 명 | IPA 예 | 만다린 |
|----------|-----|--------|--------|
| H | high level (高平) | ˥, ˦, ́ acute | 1성 |
| R | rising (上昇) | ˧˥, ̌ caron | 2성 |
| D | dipping (低降昇) | ˨˩˦ | 3성 |
| F | falling (去聲) | ˥˩, ̂ circumflex | 4성 |
| L | low (低) | ˨, ˩, ̀ grave | — |
| (M) | mid (level-3) | ˧, ̄ macron | — (표시 없음) |
| (N) | neutral / 경성 | (없음) | 5성 |

Vietnamese 6 tones는 NFD-decomposed combining marks로 인식:
- á (sắc) → H, à (huyền) → L, ả (hỏi) → D, ạ (nặng) → F, ã (ngã) → nasal (별도)

### 5.2 시각 표기 — tone_style 옵션

| Style | H | R | D | F | L | 비고 |
|-------|---|---|---|---|---|------|
| `panjeom` | 〮 | 〯 | 〯〮 | 〮〯 | — | 옛 훈민정음 정통 |
| `middledot` (기본) | · | ·· | ·· | · | — | 한글 친화·폰트 무관 (D/F 머지) |
| `arrow` | ¯ | ↗ | ↘↗ | ↘ | ↓ | **시각적으로 가장 명확** |
| `numeric` | ¹ | ² | ³ | ⁴ | ₁ | Mandarin 4성 디지트 |
| `ipa` | ˥ | ˧˥ | ˨˩˦ | ˥˩ | ˩ | IPA 그대로 |
| `ascii` | `'` | `^` | `^^` | `'` | `_` | 평문 안전 |

### 5.3 기타 보존 정보

| 종류 | IPA | UHPS Layer | 표시 |
|------|-----|-----------|------|
| 강세 (1차) | ˈ | STRESS | tone_stress (style 별) |
| 강세 (2차) | ˌ | STRESS | (생략) |
| 장음 | ː | LENGTH | ː (style 별 — `ascii`은 `:`) |
| 반장음 | ˑ | LENGTH | ˑ |

### 5.4 v3.1 정책

> **Tone is preserved as a separate prosodic layer.**  
> v3.1: 5-way tone category 시스템 정식화. Mandarin 4성 distinct 보장.  
> 다음 버전(v3.2)에서 Vietnamese spec-level NIKL 매핑·태국어 5성 추가 예정.

즉:
- 토큰 레이어 (level=4, return_tokens=True)에선 SUPRA 토큰으로 분리되어 있음
- 표면 표기 (level=5)에선 위 표대로 시각화
- v3.1에서 만다린 4성/베트남 6성 등을 음소와 분리해 별도 시각 layer로 정식화

### 5.3 Tone style 옵션

표면 표기 시 시각 스타일 4종:

| Style | 거성 | 상성 | 장음 | 비고 |
|-------|------|------|------|------|
| panjeom | 〮 | 〯 | ː | 옛 훈민정음 정통, 폰트 의존 |
| ipa | ˈ | ˇ | ː | IPA식 |
| middledot | · | ·· | ː | **default** — 한글 친화·폰트 무관 |
| ascii | ' | ^ | : | 평문 안전 |

### 5.4 강세 위치 컨벤션

IPA는 강세를 **다음 음절 앞**에 표기 (`ˈloʊ`).  
UHPS는 옛 훈민정음 방점 컨벤션을 따라 **해당 음절 뒤**에 표기 (`로·`).

```
hello   IPA: hɛˈloʊ
        UHPS-full: 헤로·우      ← 로 뒤에 점 = 로 가 강세
```

---

## 6. Token 레이어 (ML 입력)

`return_tokens=True`로 노출되는 추상 토큰. 표면 표기에 의존하지 않는다.

### 6.1 토큰 형식

각 토큰은 `(KIND, VALUE, [EXTRA])` tuple.

| KIND | VALUE | 의미 |
|------|-------|------|
| C | 자모 (현대) | 일반 자음 (예: `('C', 'ㅍ')`) |
| OLD | 자모 (옛한글) | 옛한글 자음/모음 (예: `('OLD', 'ㆄ')`) |
| V | 자모 (모음) | 일반 모음 |
| V_NASAL | 자모 (모음) | 비음 모음 (모음 + ŋ 코다) |
| V_R | 자모 (모음) | R-colored 모음 |
| C_PALATAL_N | ㅥ | 다음 모음을 palatalize |
| SV_MARKER | 'y' / 'w' | 다음 모음과 결합 (glide) |
| SUPRA | 마크 | 강세/성조/장음 마크 |
| SPACE | ' ' | 단어 경계 |
| PUNCT | 구두점 | 원문 구두점 보존 |
| V_STRESS | 자모 | (V + 강세) 단축형 (V_NASAL_STRESS, V_R_STRESS, OLD_STRESS도 동일) |

### 6.2 사용 예

```python
>>> from hunmin import transcribe
>>> transcribe("hello", "ipa", return_tokens=True)
[
  ('C', 'ㅎ'),
  ('V', 'ㅔ'),
  ('C', 'ㄹ'),
  ('V', 'ㅗ'),
  ('SUPRA', '·'),
  ('V', 'ㅜ'),
]
```

### 6.3 ML 학습용 JSONL

```jsonl
{"text": "hello", "lang": "en", "tokens": [["C","ㅎ"],["V","ㅔ"],["C","ㄹ"],["V","ㅗ"],["SUPRA","·"],["V","ㅜ"]]}
{"text": "中国", "lang": "zh", "tokens": [["C","ㅈ"],["V","ㅜ"],["C","ㆁ"],["SUPRA","·"],["C","ㄱ"],["OLD","ㆎ"],["SUPRA","·"]]}
```

---

## 7. 버전 정책

UHPS spec은 SemVer를 따른다.

| 변경 종류 | 버전 | 예 |
|----------|------|-----|
| Patch | 3.0.x | 새 IPA 음소 추가 (기존 매핑 영향 없음) |
| Minor | 3.x.0 | 새 layer/feature (toke layer, tone renderer 등). 기존 매핑은 호환 유지. |
| Major | 4.0.0 | 기존 음소 매핑 변경, 의도된 머지 변경/추가 |

코드 패키지(`hunmin`) 버전과 spec 버전은 별도로 관리한다. 코드 v3.0.0~3.x.x은 spec v3.0을 구현한다.

---

## 8. 참조 구현

### 8.1 매핑 데이터

`hunmin/core/universal.py`:
- `_IPA_PHONEMES` — 단일 IPA → 토큰 (§3.1-3.8)
- `_IPA_DIGRAPHS` — 다중자 IPA → 단일 토큰 (§3.4)
- `_NASAL_MAP` — 비음 모음 처리 (§3.8)
- `_TONE_DIACRITICS` — 모음 위 톤 결합 마크 (§5.1)
- `_MANDARIN_TONE` — 만다린 1-5 톤 디지트 (§5.1)
- `TONE_STYLES` — 표면 시각 스타일 (§5.3)

### 8.2 처리 단계

```
1. _normalize_ipa(ipa)         IPA 입력 정규화 (NFC, digraph 합성, diacritic 필터)
2. _tokenize_ipa(ipa)          IPA → 추상 토큰 시퀀스
3. _expand_stress_tokens(...)  V_X_STRESS → V_X + SUPRA 분리
4. _assemble(tokens)           토큰 → Hangul 음절 합성
```

`return_tokens=True`는 단계 2까지의 결과(또는 3까지 expand한 결과)를 노출한다.

---

## 9. 예시

### 9.1 영어

| 단어 | IPA | level=1 | level=3 (core) | level=5 (full) |
|------|-----|---------|----------------|----------------|
| hello | həˈloʊ | 헬로 | 허로우 | 허로·우 |
| think | θɪŋk | 싱크 | ㅼ이ㆁ크 | ㅼ이ㆁ크 |
| father | ˈfɑːðɚ | 파더 | ㆄ아ㅽ어r | ㆄ아·ːㅽ어r |
| love | lʌv | 러브 | 러ㅸ | 러ㅸ |

### 9.2 프랑스어

| 단어 | IPA | level=1 | level=3 (core) | level=5 (full) |
|------|-----|---------|----------------|----------------|
| bonjour | bɔ̃ʒuʁ | 봉주르 | ㅂㆎᄶ우ᄛ | ㅂㆎᄶ우ᄛ |
| merci | mɛʁsi | 메르시 | 메ᄛ시 | 메ᄛ시 |

### 9.3 만다린

| 단어 | IPA | level=1 | level=3 (core) | level=5 (full) |
|------|-----|---------|----------------|----------------|
| 你好 | ni˨˩˦ xau˨˩˦ | 니하오 | 니 ㆅ아우 | 니〯 ㆅ아우〯 |
| 中国 | ʈʂʊŋ˥ kwo˧˥ | 중궈 | ㅊ우ㆁ ㄱ워 | ㅊ우ㆁ〮 ㄱ워〯 |

### 9.4 Hand-curated showcase (v3.31, tone_style='middledot')

각 entry는 `tests/gold/uhps_showcase.jsonl` + `tests/test_uhps_showcase.py`에서 회귀 lock-in.

#### 9.4.1 옛한글 음소 (13종)

| ID | Feature | IPA | UHPS-full | Note |
|----|---------|-----|-----------|------|
| S01 | /f/ → ㆄ | `fɪʃ` | `ㆄ이ᄾ` | NIKL은 ㅍ |
| S02 | /v/ → ㅸ | `ˈvɛri` | `ㅸ에·리` | NIKL은 ㅂ |
| S03 | /θ/ → ㅼ | `θɪŋk` | `ㅼ잉크` | think; /ŋ/=ㆁ받침 |
| S04 | /ð/ → ㅽ | `ðɪs` | `ㅽ잇` | this; /s/ → ㅅ받침 |
| S05 | /z/ → ㅿ | `ziːroʊ` | `ㅿ이ː로우` | NIKL은 ㅈ |
| S06 | /ʒ/ → ᄶ | `ʒɑːnrə` | `ᄶㆍː느러` | /ɑː/=ㆍ |
| S07 | /ʃ/ → ᄾ | `ʃoʊ` | `ᄾ오우` | NIKL은 시오 |
| S08 | /x/ → ㆅ | `bax` | `바ㆅ` | German Bach |
| S09 | /ʁ/ → ᄛ | `paʁi` | `파ᄛ이` | French Paris |
| S10 | /ɲ/ → ㅥ | `maˈɲana` | `마ㅥ야·나` | Spanish mañana |
| S11 | /ɔ/ → ㆎ | `kɔːt` | `ㅋㆎː트` | caught |
| S12 | /ɑ/ → ㆍ | `ˈfɑːðər` | `ㆄㆍ·ːㅽ얼` | father (master case) |
| S13 | /ŋ/ → ㆁ받침 | `sɪŋ` | `싱` | NFC collapses to ㅇ받침 |

#### 9.4.2 Prosody (운율)

| ID | Feature | IPA | UHPS-full |
|----|---------|-----|-----------|
| S14 | Length /ː/ | `siː` | `시ː` |
| S15 | Primary stress ˈ → · | `ˈrɛkərd` | `레·컬드` |
| S16 | Secondary stress ˌ → ˗ | `ˌɪnfərˈmeɪʃən` | `이˗느ㆄ얼메·이ᄾ언` |
| S17 | Mandarin tone1 (high) | `ma˥` | `마¯` (arrow) |
| S18 | Mandarin tone2 (rising) | `ma˧˥` | `마↗` |
| S19 | Mandarin tone3 (dipping) | `ma˨˩˦` | `마↘↗` |
| S20 | Mandarin tone4 (falling) | `ma˥˩` | `마↘` |

#### 9.4.3 Diphthongs · Clusters · Affricates

| ID | Feature | IPA | UHPS-full |
|----|---------|-----|-----------|
| S21 | /aɪ/ | `haɪ` | `하이` |
| S22 | /eɪ/ | `deɪ` | `데이` |
| S23 | /oʊ/ | `ɡoʊ` | `고우` |
| S24 | /aʊ/ | `haʊ` | `하우` |
| S25 | /ɔɪ/ | `bɔɪ` | `ㅂㆎ이` |
| S27 | Cluster /θr/ | `θriː` | `ㅼ리ː` |
| S28 | Cluster /str/ | `striːt` | `슽리ː트` |
| S33 | /ts/ affricate | `tsuˈnami` | `추나·미` |
| S34 | /dʒ/ affricate | `ˈdʒɑːz` | `ㅈㆍ·ːㅿ` |
| S35 | /tʃ/ affricate | `tʃiːz` | `치ːㅿ` |

#### 9.4.4 Schwa · Rhotic · Nasals

| ID | Feature | IPA | UHPS-full | Note |
|----|---------|-----|-----------|------|
| S29 | Schwa /ə/ | `əˈbʌv` | `어버·ㅸ` | |
| S30 | Rhotic /ɚ/ | `ˈfɑːðɚ` | `ㆄㆍ·ːㅽ어` | /ɚ/ ≅ /ə/ in UHPS-full |
| S31 | French /ɛ̃/ | `vɛ̃` | `ㅸ엥` | v3.32 fix; ㆁ→ㅇ NFC |
| S32 | French /ɑ̃/ | `blɑ̃` | `브ㄹㆍ` | KNOWN GAP: OLD vowel + nasal |
| S40 | Russian /tʲ/ | `ʐɨtʲ` | `ᄶ읕` | KNOWN GAP: palatalization vs ㄷ |

#### 9.4.5 Multi-feature 케이스

| ID | Feature | IPA | UHPS-full |
|----|---------|-----|-----------|
| S26 | /f/ + /v/ + /z/ + 강세 + /ʃ/ | `ˈfɪzəkəl ˈvɛrɪfɪˌkeɪʃən` | `ㆄ이·ㅿ어컬 ㅸ에·리ㆄ이˗케·이ᄾ언` |
| S37 | breathe (cluster + length + /ð/) | `briːð` | `브리ːㅽ` |
| S38 | garage (schwa + /ɑː/ + /ʒ/) | `ɡəˈrɑːʒ` | `거ㄹㆍ·ːᄶ` |
| S39 | Greek θεός | `θeˈos` | `ㅼ에오·스` |

---

## 10. 변경 이력

- **v3.32** (2026-05) — `_compose_with_jong` ㆁ→ㅇ remap. French nasals (vɛ̃ → ㅸ엥, œ̃ → 왱).
- **v3.31** (2026-05) — Hand-curated UHPS-full showcase 40 entries (§9.4) — primary product spec lock-in.
- **v3.27** (2026-05) — UHPS-full external eval 35→143 entries.
- **v3.16** (2026-05) — Assembler cleanup: ㅇㆍ literal 제거, ㆁ→ㅇ받침 자동, 어말 OLD 마찰음 ㅡ-syll.
- **v3.1** (2026-04) — Tone renderer 5-way (H/R/D/F/L), Mandarin 4성 distinct, arrow/numeric/panjeom styles.
- **v3.0** (2026-04-30) — Spec freeze. 매핑 v2.4.4 기준 동결. Token layer 정의.
- v2.x (2026-04-29~30) — 코드 진화기 (이 문서 이전 — 코드가 사실상 spec)

---

## 부록 A — 사용된 옛한글 자모 (Unicode)

| 자모 | Unicode | 이름 | UHPS 용도 |
|------|---------|------|-----------|
| ㆄ | U+3184 | 피읖+이응 | /f/ |
| ㅸ | U+3178 | 비읍+이응 | /v/ |
| ㅿ | U+317F | 반시옷 | /z/ |
| ㆁ | U+3181 | 옛이응 | /ŋ/ |
| ㆆ | U+3186 | 여린히읗 | /ʔ/ |
| ㆅ | U+3185 | 쌍히읗 | /x ç ħ χ/ |
| ㅱ | U+3171 | 미음+이응 | /ɱ/ |
| ㅥ | U+3165 | 쌍니은 | /ɲ/ |
| ㅼ | U+317C | 시옷+디귿 | /θ/ |
| ㅽ | U+317D | 시옷+비읍 | /ð/ |
| ᄾ | U+113E | 치두음 시옷 | /ʃ ɕ ʂ/ |
| ᄶ | U+1136 | 치두음 지읒 | /ʒ ʑ ʐ/ |
| ᄛ | U+111B | 가벼운 ㄹ | /ʁ ʀ/ |
| ㆍ | U+318D | 아래아 | /ɑ ɒ/ |
| ㆎ | U+318E | 아래아+이 | /ɔ/ |
| ㅙ | U+3159 | 와+이 | /œ/ (재활용) |
| 〮 | U+302E | 방점 (거성) | high stress/tone |
| 〯 | U+302F | 방점 (상성) | rising tone |

## 부록 B — 폰트 호환 fallback

`safe_fonts=True` (기본값)에서 Hangul Jamo 블록(U+1100-U+11FF) 자모는 Compat 블록(U+3131-U+318F) 또는 modern jamo로 대체:

| 원본 | Fallback | 손실 |
|------|----------|------|
| ᄾ | ㅅ | ʃ vs s 변별 손실 |
| ᄶ | ㅈ | ʒ vs ʤ 변별 손실 |
| ᄛ | ㄹ | ʁ vs r 변별 손실 |

`safe_fonts=False`로 명시하면 진짜 옛 자모 그대로 출력. ML 학습·언어학 분석엔 `safe_fonts=False` 권장.
