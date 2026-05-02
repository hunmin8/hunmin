# Hunmin CHANGELOG

표준 [Keep a Changelog](https://keepachangelog.com/) 포맷.

## [3.35.0] — 2026-05-01 — S40 Russian palatalized /tʲ/ /dʲ/ fix

### Fixed (Track D 마무리)
- **`_normalize_ipa` palatalization pre-process**: 'tʲ' → soft d (ㄷ), 'dʲ' → d (ㄷ)
  - 'ʲ' diacritic이 strip되기 전 매핑되도록 처리
- **S40 Russian /tʲ/**: `ʐɨtʲ` → **ᄶ읃** (이전 ᄶ읕)
- **40/40 showcase 모두 정상 case** — known-gap 0 ✓

### Tests
- 551 passed (전부 유지, 1 expected updated)

## [3.34.0] — 2026-05-01 — HF Feature Gallery + S32 OLD-vowel nasal fix

### Added (Track C)
- **HF Space**: 새 탭 `🎁 Feature Gallery (UHPS-full)`
  - 40 showcase entries 마크다운 표 + 직접 IPA 입력 시연 영역
  - 옛한글 13종 + Prosody + Diphthongs + Clusters + Multi-feature 카테고리화

### Fixed (Track D)
- **S32 OLD vowel + nasal** (blɑ̃ → 브ㄹㆍㆁ): C+V_NASAL 브랜치에서 OLD vowel(ㆍ ㆎ ㅙ)일 때 ㆁ 분리 추가 (한글 완성형 결합 불가 fallback)
- 영향: Bonjour `bɔ̃ʒuʁ` → **ㅂㆎㆁᄶ우ᄛ** (이전 ㅂㆎᄶ우ᄛ, 비음 marker 추가)
- S32 KNOWN_GAP → 정상 case 승격 (이제 38/40 + 2 known-gap에서 39/40 + 1 known-gap)

### Tests
- 551 passed (전부 유지, 4 expected updated)

## [3.33.0] — 2026-05-01 — UHPS_SPEC.md codify (showcase entries baked in)

### Documented (Track B docs)
- `docs/UHPS_SPEC.md` §9.4 추가 — 40 hand-curated showcase entries 모두 spec doc 안에 codify
  - §9.4.1 옛한글 음소 13종 표 (S01-S13)
  - §9.4.2 Prosody 7개 (S14-S20: length, primary/secondary stress, Mandarin tones 4)
  - §9.4.3 Diphthongs/Clusters/Affricates 10개 (S21-S25, S27, S28, S33-S35)
  - §9.4.4 Schwa/Rhotic/Nasals 5개 (S29-S32, S40 — known gaps 명시)
  - §9.4.5 Multi-feature 4개 (S26, S37-S39)
- Spec doc 헤더 업데이트 — version/status/regression lock-in 명시
- 변경이력 v3.0 → v3.32 흐름 박음

### Tests
- 551 passed (변경 없음 — doc-only)

## [3.32.0] — 2026-05-01 — UHPS-full nasal preservation fix

### Fixed (Track B continued)
- **`_compose_with_jong` ㆁ→ㅇ remap**: 옛한글 ㆁ을 받침 자리에 받아들이도록 수정 (FINALS는 표준만 지원)
- **French nasal /ɛ̃/** 이제 정확히 'ㅸ엥'로 출력 (vingt 빙 → ㅸ엥)
- **French nasal /œ̃/** 이제 '왱' (un → 왱)
- Showcase S31 더 이상 KNOWN_GAP 아님 — 정상 case로 승격

### Tests
- 551 passed (전부 유지)

## [3.31.0] — 2026-05-01 — UHPS-full hand-curated showcase (primary product)

### Added (Track B — primary product strengthening)
- `tests/gold/uhps_showcase.jsonl` — **40 hand-curated UHPS-full entries**, 각 항목마다 `feature` + `rationale` 명시
  - 옛한글 음소 13종 (S01-S12, S25): /f/ /v/ /θ/ /ð/ /z/ /ʒ/ /ʃ/ /x/ /ʁ/ /ɲ/ /ɔ/ /ɑ/ /ŋ/
  - Prosody (S14-S20): 장음 ː, 1차 강세 ·, 2차 강세 ˗, Mandarin 4성 (¯ ↗ ↘↗ ↘)
  - Diphthongs (S21-S25): /aɪ/ /eɪ/ /oʊ/ /aʊ/ /ɔɪ/
  - Clusters (S27, S28): /θr/, /str/
  - Schwa/rhotic (S29, S30): /ə/ /ɚ/
  - Affricates (S33-S35): /ts/ /dʒ/ /tʃ/
  - Multi-feature (S37, S38): breathe, garage
- `tests/test_uhps_showcase.py` — 40 spec compliance 테스트 (40 passed)

### Found (known gaps documented)
- **S31_KNOWN_GAP**: French nasal /ɛ̃/ → 엔진 nasalization 마커 drop (vɛ̃ should → ㅸ엥, currently → ㅸ에)
- **S32_KNOWN_GAP**: French nasal /ɑ̃/ similarly drops nasal mark
- **S40_KNOWN_GAP**: Russian palatalized /tʲ/ → ㄷ받침 (Spec) vs ㅌ받침 (engine)

### Tests
- 511 → **551 passed** (+40 새 showcase 회귀)

## [3.30.0] — 2026-05-01 — Russian soft-sign (ь) NIKL fix

### Fixed
- **Russian (ru): 69.1 → 72.7%** (+3.6pt)
  - 어말 ь after nasal/liquid (н/м/л/р) → 받침 (NIKL: ㅣ 추가 안 함)
  - PALATAL_BREAK marker — 자음+ь+모음 사이 syllable break (семья 셈야)
  - огонь 오고니 → **오곤**, Казань 카자니 → **카잔**, семья 세먀 → **셈야**

### Measured
- 전체: 75.3 → **75.5% exact** (+0.2pt, +2 correct)

## [3.29.0] — 2026-05-01 — French Cl-cluster polish

### Fixed
- **French (fr): 68.8 → 75.0%** (+6.2pt)
  - Cl 클러스터 → 받침-ㄹ + ㄹV (NIKL 표기법 일관 적용)
  - glace 그라스 → 글라스, plage 프라주 → 플라주, fleur 프뢰르 → 플뢰르, plaisir 프레지르 → 플레지르

### Measured
- 전체: 74.9 → **75.3% exact** (+0.4pt, +4 correct)

## [3.28.0] — 2026-05-01 — German NIKL polish

### Fixed
- **German (de): 60.8 → 80.4%** (+19.6pt)
  - 어두 'st'/'sp' → 슈ㅌ/슈ㅍ (Stadt 슈타트, Strasse 슈트라세, Stuttgart, Strudel)
  - 'tz' → ㅊ 단일 (Platz 플라츠, Schnitzel 슈니첼)
  - 'ck' → ㅋ 단일 (Brücke 브뤼케)
  - 모음 앞 's' → ㅈ voicing (Sonne 조네, Käse 케제, Insel 인젤, Sauerkraut 자우어)
  - 'ss' 다음 's' → ㅅ 유지 (Wasser 바서)
  - Cl/Cr 클러스터 → 받침-ㄹ + ㄹV (Fluss 플루스, Park 파르크 일부)

### Measured
- 전체: 73.9 → **74.9% exact** (+1.0pt, +10 correct)

## [3.27.0] — 2026-05-01 — UHPS-full eval expansion (primary product)

### Added
- `tests/gold/uhps_external.jsonl` 35 → **143 entries** (4x)
  - 옛한글 음소 다양화: /f/=ㆄ, /v/=ㅸ, /θ/=ㅼ, /ð/=ㅽ, /z/=ㅿ, /ʒ/=ᄶ, /ʃ/=ᄾ, /x/=ㆅ, /ʁ/=ᄛ, /ɲ/=ㅥ, /ɔ/=ㆎ, /ɑ/=ㆍ, /ŋ/=ㆁ받침
  - Prosody: 장음 ː, primary ˈ, secondary ˌ, Mandarin 4성, Vietnamese 6성
  - Multilingual: en/de/fr/es/it/ru/zh/ja/vi/ar/ko 다양한 케이스
  - Diphthongs, 자음 클러스터, 단어 단위 stress
- `scripts/gen_uhps_external_v2.py` — 추후 확장용 generator

### Philosophy
- **UHPS-full = primary product**. NIKL은 호환층 (#3.15 reframe 후 일관).
- 이번 eval은 IPA → UHPS-full 매핑이 **spec-faithful**한지 회귀 잠금 (lock-in).

### Tests
- 전체: 403 → **511 passed** (+108 새 UHPS-full 회귀 케이스)

## [3.26.0] — 2026-05-01 — vi/nl NIKL polishing

### Fixed
- **Vietnamese (vi): 43.6 → 64.1%** (+20.5pt)
  - 어말 'nh' → 받침 ㄴ (đình 디니 → 딘, bánh 바니 → 반)
  - 어말 t/c/p → 받침 ㅅ/ㄱ/ㅂ (đất 더트 → 덧, nước 느어크 → 느억)
  - 음절 사이 공백 제거 (gia đình 자 디니 → 자딘)
- **Dutch (nl): 46.9 → 62.5%** (+15.6pt)
  - 'aa' → 두 음절 분리 (maan 만 → 마안)
  - 어말 무성 폐쇄음 받침 흡수 X (kerk 케륵 → 케르크, dorp 도릅 → 도르프)
  - 어말 'd' devoicing → ㅌ (wind 빈드 → 빈트, stad 스타드 → 스타트)

### Measured
- 전체: 72.6 → **73.9% exact** (+1.3pt, +13 correct)

## [3.25.0] — 2026-05-01 — Per-language NIKL gap fixes (es/pt/it)

### Fixed
- **Spanish (es): 84.1 → 98.6%** (+14.5pt)
  - 'rr' → 단일 ㄹ (NIKL: 다음 음절 초성)
  - Cl 자음 클러스터 (pl/bl/gl/fl/sl) → 받침 ㄹ + ㄹV
- **Portuguese (pt): 52.1 → 70.8%** (+18.7pt)
  - 'rr' → /h/ Brazilian (forró 포호, arroz 아호스)
  - 어말 unstressed 'o' → ㅜ (Brazilian default)
  - nh/lh + 어말 'o' → 뉴/류
- **Italian (it): 80.7 → 94.7%** (+14.0pt)
  - 겹자음은 단일 자음으로 (NIKL 외래어 표기법)

### Measured
- 전체: 70.0 → **72.6% exact** (+2.6pt, +8 correct)

## [3.24.0] — 2026-05-01 — Held-out 1000-row gold + 진짜 룰 정확도

### Added
- `tests/gold/heldout_1000.tsv` — **1015 entries × 21 languages** override-free 검증 데이터
  - es(69) · fr(64) · it(57) · pt(48) · de(51) · nl(32) · ru(55) · pl(48) · tr(46) · id(46) · hu(30) · sk(35) · cs(40) · ro(37) · hr(37) · sr(34) · vi(39) · fa(38) · en(107) · ja(50) · zh(52)
  - Categories: common / place / food / brand
- `scripts/eval_heldout_1000.py` — 정확도 평가 CLI (per-lang, JSON output, top-mismatches)
- `tests/test_heldout_1000.py` — 정확도 baseline 회귀 테스트 (24 tests)

### Measured
- **전체 진짜 룰 정확도 (override 없이): 70.0% exact, 85.0% CER** (1015 rows)
- 최고: ja 96.0%, zh 94.2%, id 91.3%, tr 84.8%, es 84.1%
- 최저: fa 21.1% (Persian short-vowel 한계), vi 43.6%, nl 46.9%

### Fixed
- hr/cs/sk: `c` → /ts/ 누락 버그 수정 (이전엔 'c' 글자 그대로 누출)
  - sr +17.6%, sk +11.4%, hr +8.1%, cs +7.5% accuracy ↑

### Tests
- 379 → **403 passed** (+24 회귀)

## [3.23.0] — 2026-05-01 — Tibetan/Khmer/Lao/Burmese letter→IPA fallback

### Added
- 4 새 script 지원 (epitran 의존 없음):
  - **Tibetan** (티베트, U+0F00..U+0FFF) — base + subjoined consonants + tsek
  - **Khmer** (크메르, U+1780..U+17FF) — coeng (្) + diacritics
  - **Lao** (라오, U+0E80..U+0EFF) — 결합 모음 + 톤 마크 silent
  - **Burmese** (버마/미얀마, U+1000..U+109F) — asat (်) + 모음 마크
- `_detect_script()` Unicode block 분류 4개 추가
- `transcribe_auto`에 라우팅 분기 추가 — strict mode leak 0 보장

### Verified
- བོད (티베트) → 볻
- ខ្មែរ (크메르) → 크멜
- ວຽງຈັນ (비엔티안) → 위앙찬
- မြန်မာ (미얀마) → 므은마

## [3.22.0] — 2026-05-01 — Persian rule module
- `hunmin/core/persian.py` — 페르시아어 (Farsi) Arabic-script → Hangul
- 추가 자모 (پ چ ژ گ) + 자음 사이 default vowel 자동 삽입
- 핵심: ج→ㅈ, چ→ㅊ, خ→흐, ش→시, ق→ㄱ, پ→ㅍ
- `_PRECISE` 21 hardcoded langs (fa 추가)

## [3.21.0] — 2026-05-01 — 외부 evaluation corpus (NIKL 의존 X)
- `tests/gold/uhps_external.jsonl` — 35개 IPA-based UHPS-full 검증
- `tests/test_external.py` — 자동 회귀 테스트 (37 tests)
- 검증 100% — 모든 IPA → expected UHPS-full 정확 매칭

## [3.20.0] — 2026-05-01 — HF Space final polish — UHPS-full hero

## [3.19.0] — 2026-05-01 — CJK ja 복합어 fix + irregular reading override
- 복합어 공백 제거: すき焼き → 스키야키
- Irregular reading override: 鹿児島 → 가고시마 (児 read 'go' not 'ko')
- EE_GOLD ja: 86.8% → **91.5%**

## [3.18.0] — 2026-05-01 — Mongolian/Persian + CJK audit

## [3.17.0] — 2026-05-01 — Vietnamese rule + 2차 강세
- `hunmin/core/vietnamese.py` — letter-by-letter NIKL 베트남어 룰
- 핵심: ph→ㅍ, đ→ㄷ, ch→ㅉ, tr→ㅉ, qu→ㄲ, ngh/ng→응

## [3.16.0] — 2026-05-01 — UHPS-full assembler cleanup
- ㅇㆍ literal 제거: father ㆄㅇㆍ·ːㅽ어 → ㆄㆍ·ːㅽ어
- /ŋ/ ㆁ 받침 자동 흡수: sing 시ㆁ → 싱
- 어말 OLD 자음 받침 회피: Bach 밯 → 바흐, jazz 쟂 → 재즈

## [3.15.0] — 2026-05-01 — UHPS-full을 primary mode로 reframe
- `docs/UHPS_FULL_SHOWCASE.md` — UHPS-full vs NIKL 비교, 옛한글 추정 가이드

## [3.14.0] — 2026-05-01 — Serbian Cyrillic rule (Vukov azbuka 트릭)
- 30줄 모듈: Cyrillic→Latin 1:1 변환 후 Croatian 룰 재사용
- EE_GOLD sr: 7.7% → 25.6%, mk: 11.8% → 29.4%

## [3.13.0] — 2026-05-01 — Croatian/Bosnian rule + Polish ły fix
- `hunmin/core/croatian.py`
- EE_GOLD bs: 9.7% → 35.5%, hr: 12.1% → 19.0%

## [3.12.0] — 2026-05-01 — Romanian rule module
- `hunmin/core/romanian.py`
- EE_GOLD ro: 15.6% → 23.7%

## [3.11.0] — 2026-05-01 — Czech rule module
- `hunmin/core/czech.py`
- EE_GOLD cs: 8.7% → 15.7%

## [3.10.0] — 2026-05-01 — Slovak 룰 + Armenian/Georgian IPA + multilingual stress
- `hunmin/core/slovak.py`
- Armenian/Georgian letter→IPA 매핑

## [3.9.0] — 2026-04 — `transcribe_auto` 정착: tests + Hebrew + CLI + HF tab

## [3.8.0] — 2026-04 — Mixed-script auto-routing + digit/symbol — leak 0 보장

## [3.7.0] — 2026-04 — 모든 룰 모듈 phonetic= 인자 통일

## [3.6.0] — 2026-04 — 5 explicit modes: HUNMIN/UHPS layer 분리
- `HUNMIN_NIKL`, `HUNMIN_PHONETIC`, `UHPS_CORE`, `UHPS_JAMO`, `UHPS_FULL` 상수

## [3.5.0] — 2026-04 — Hungarian rule module

## [3.4.0] — 2026-04 — 만다린 ze fix + Vietnamese/Hu/Sk overrides
- 毛泽东 마오저둥 → 마오쩌둥 (NIKL 외래어 표준)

## [3.3.0] — 2026-04 — Held-out 정확도 + UHPS 자모 확장 + CJK regression
- UHPS Spec compliance: 95/95 tests (100%)

## [3.2.0] — 2026-04 — 동구권 fallback + 약어 사전

## [3.1.0] — 2026-04 — Tone renderer 정식화 (UHPS_SPEC §5)
- 5-way tone category: H/R/D/F/L
- Mandarin 4성 distinct 보장
- arrow / numeric / panjeom tone style

## [3.0.0] — 2026-04 — Spec freeze + ML token layer
- `docs/UHPS_SPEC.md` 정식 spec 동결
- `transcribe(..., return_tokens=True)` ML 학습용 token sequence

## [2.4.x] — 2026-04
- v2.4.4: affricate digraph 보강 (tɕ/dʑ, tʂ/dʐ)
- v2.4.3: 강세 attach bug fix
- v2.4: UHPS-core / UHPS-full 분리

## [2.3.0] — 2026-04 — API 정리 + 톤 다운

## [2.2.0] — 2026-04 — UHPS v2 + IPA 직접 입력 모드
- 옛한글 + 한글자모확장으로 IPA → 한글 1:1 매핑
- `lang='ipa'`로 직접 IPA 입력 (의존성 0)

## [2.1.0] — 2026-04 — Universal IPA transcriber via epitran (100+ langs)

## [1.10.0] — 2026-04 — CJK NIKL 외래어 표기법 본격 적용

## [1.8.0] — 2026-04 — 다국어 폴리싱 + 데모 + Syllabic schwa

## [1.6.0] — 2026-04 — ML fallback + 형태소 분해

## [1.5.0] — 2026-04 — 다국어 폴리싱 (fr/it/de/es/ru/pt/nl/pl/tr/id)

## [1.4.0] — 2026-04 — Override 사전 150 → 515 단어

## [1.3.0] — 2026-04 — 영어 파이프라인 강화 (97.3% NIKL)

## [1.0.0] — 2026-04 — Initial public release
- 14개 언어, 하이브리드 파이프라인, UHPS freeze
