# Hunmin v3.37 — 세션 인계 문서

**날짜**: 2026-05-01
**현재 버전**: v3.37.0 (sandbox built, host에서 PyPI publish 대기)

---

## 1. 지금까지 한 일 (2026-05-01 세션, v3.23 → v3.37)

### 15 패치 ship됨 — sandbox dist/ 에 모두 존재

| 버전 | 트랙 | 핵심 |
|------|------|------|
| v3.23 | A | Tibetan/Khmer/Lao/Burmese letter→IPA |
| v3.24 | A | Held-out 1015-row gold 신설 — 진짜 정확도 측정 시작 |
| v3.25 | A | es/pt/it gap fixes |
| v3.26 | A | vi/nl polish |
| v3.27 | B | UHPS-full eval 35→143 entries |
| v3.28 | A | German polish (st/sp/tz/ck) |
| v3.29 | A | French Cl-cluster |
| v3.30 | A | Russian ь soft-sign |
| v3.31 | B | UHPS-full hand-curated showcase 40 entries (primary product spec) |
| v3.32 | B | French nasals fix (vɛ̃ → ㅸ엥) — `_compose_with_jong` ㆁ→ㅇ remap |
| v3.33 | B | UHPS_SPEC.md §9.4 codify (40 showcase entries doc 통합) |
| v3.34 | C+D | HF Space Feature Gallery 탭 + S32 OLD vowel + nasal fix |
| v3.35 | D | S40 Russian /tʲ/ palatalized → ㄷ받침 |
| **v3.36** | **🐛** | **Critical bug fix: `mode=UHPS_FULL` 룰 모듈 우회 안 되던 버그** |
| **v3.37** | **🐛** | **Critical bug fix: en acronym + UHPS_JAMO TypeError** |

### 정확도 결과

**NIKL 호환층 (held-out 1015 entries × 21 langs)**:
- 70.0% → **75.5%** (+5.5pt)
- 8개 언어 +6~+20pt (es/pt/it/de/fr/vi/nl/ru)

**UHPS-full primary product**:
- 35 → 143 + **40 hand-curated showcase entries** (40/40 spec compliant)
- French nasals + Russian palatalization 본질적 fix
- `docs/UHPS_SPEC.md` §9.4 codified

**Tests**: 379 → **551** (+172)

---

## 2. 발견된 버그 (이번 세션 정밀 audit)

### v3.36 — `mode=UHPS_FULL` 라우팅 버그 ⚠️
- `transcribe('Bonjour', 'fr', mode=UHPS_FULL)`이 NIKL 결과 반환했음
- 원인: `_hangul_inner`가 `lang in _PRECISE` 체크로 룰 모듈 우선
- fix: uhps in ('full','core') AND lang not in ('en','ipa') 시 universal IPA 강제

### v3.37 — en acronym + UHPS_JAMO TypeError ⚠️
- `transcribe('NASA', 'en', mode=UHPS_JAMO)` → TypeError
- 원인: `_drop_postvocalic_r(lphs)` 1-arg 호출, signature는 2-arg 필요
- fix: `aligned=None` optional 처리

**두 버그 모두 PyPI v3.35.0 사용자 영향** — v3.37 publish 빨리 권장.

---

## 3. 즉시 할 일 (host에서 5분)

```bash
cd ~/koboltmine/hunmin_pkg

# 1. PyPI publish
python -m twine upload dist/hunmin-3.37.0-py3-none-any.whl dist/hunmin-3.37.0.tar.gz

# 2. Git tag + push
git add . && git commit -m "v3.37 — Critical bugs fix + cumulative session"
git tag -a v3.37.0 -m "v3.37 — Bug fixes + 15 patches cumulative"
git push origin main v3.37.0

# 3. HF Space sync
cd hf_space
git add . && git commit -m "v3.37 — Feature Gallery + bug fixes"
git push hf main

# 4. dist/ cleanup (옵션)
cd ../dist
ls hunmin-3.{2[3-9],3[0-6]}* | xargs rm  # < 3.37 정리
```

---

## 4. 다음 세션 — 작업 큐

원래 사용자가 정한 옵션 5번부터 시작:

### 5번. NIKL 추가 polish (E 트랙)

**현 정확도 / 천장 / 갭**:

| 언어 | 현재 | 목표 | 갭 패턴 |
|------|------|------|---------|
| pl | 66.7% | 75% | 어말 'k' 분리, chl Cl 클러스터, intervocalic l (이전 시도 회귀로 revert됨) |
| cs | 67.5% | 75% | Cl 클러스터 미적용 |
| hr | 67.6% | 75% | jamo-string-list 구조 — 일반 post-process 어려움 (재구조화 필요) |
| sr | 73.5% | (hr 의존) | hr 개선 시 자동 따라감 |
| hu | 73.3% | 78% | gy/ny/ly/ty palatal digraph 정밀화, accent + cs/sz |
| ro | 70.3% | 75% | ie/iu/ia diphthong, ce/ci/ge/gi |

**예상 gain**: 75.5% → 78~80%
**Risk**: pl/hr 모듈 재구조화 careful (이전 회귀 경험)

### 6번. fa Persian short-vowel (구조적 한계)

- 현재 21.1%
- 문제: Persian short vowels는 IPA 표기 X → default 'a' 삽입의 천장
- 해결책: 단어별 dictionary 또는 신경망 G2P 필요
- **권장**: 별도 트랙으로 미루거나 dictionary 기반 보강

### 7번. en CMU phoneme cleanup (60.7%)

- -ower/-tion/-et endings 깊은 구조 변경 필요
- High-freq override 확장이 더 빠름 (이미 400+ overrides)
- 또는 g2p-en optional dependency 활용
- **권장**: override 확장 (1시간) > 룰 변경

### 8번. HF Space hero 재구성

- "40/40 ideal compliance" 메시지 강화
- README 첫 화면 재구성
- v3.36/v3.37 bug fix 자랑

### 9번. 새 언어 모듈 추가

후보: th, hi, ta, bn, sw, am, vi (이미 있음)

### 10번. CJK v_cjk_v3 training (#31, 별개 트랙)

- 오래된 task — 별개 ML 트랙
- 이번 NIKL/UHPS-full 세션과 무관

### 트랙 B 확장 (UHPS-full 더 정밀화)

- Polish ę/ą nasal (Russian처럼 ㆁ 분리 패턴 적용)
- Hungarian a → ɒ → ㆎ UHPS 매핑 검증
- Vietnamese 6 tones full coverage in showcase
- 새 옛한글 음소 후보: ㅴ /sw/, ㅱ /m̥/

---

## 5. 알려진 한계 (수정 어려움)

- **fa (21.1%)**: Persian short vowels 구조적 한계
- **en (60.7%)**: CMU phoneme 천장
- **hr (67.6%)**: 모듈 구조 재작성 필요

---

## 6. 산출물 위치

```
hunmin_pkg/
├── hunmin/                        # 코드
│   ├── core/
│   │   ├── universal.py           # IPA → UHPS-full 엔진
│   │   ├── english.py             # CMU dict 기반 영어
│   │   ├── french.py, german.py, ... # 11개 룰 모듈
│   │   └── ...
│   ├── api.py                     # mode 라우팅 (v3.36 fix)
│   ├── auto.py                    # transcribe_auto + 4개 새 script
│   └── __init__.py                # __version__ = '3.37.0'
├── tests/
│   ├── gold/
│   │   ├── heldout_1000.tsv       # 1015 entries × 21 langs
│   │   ├── uhps_external.jsonl    # 143 IPA → UHPS-full
│   │   └── uhps_showcase.jsonl    # 40 hand-curated (40/40 spec)
│   ├── test_heldout_1000.py       # 24 회귀
│   ├── test_uhps_showcase.py      # 40 spec compliance
│   └── ... (8 test files, 551 total)
├── docs/
│   ├── UHPS_SPEC.md               # §9.4 codified
│   ├── SESSION_2026-05-01.md      # 본 세션 보고서
│   └── UHPS_FULL_SHOWCASE.md
├── scripts/
│   ├── eval_heldout_1000.py
│   └── gen_uhps_external_v2.py
├── hf_space/
│   ├── app.py                     # Feature Gallery 탭 추가
│   └── requirements.txt           # >= 3.37.0
├── dist/
│   ├── hunmin-3.23.0 ~ 3.37.0     # 15 wheel + 15 sdist
│   └── ...
├── CHANGELOG.md                    # Keep-a-Changelog 표준
├── NEXT_TODO.md                    # (이 파일과 중복, 통합 가능)
├── HANDOFF.md                      # ★ 본 인계 문서
└── README.md                       # v3.37 hero
```

---

## 7. 추천 다음 세션 순서

1. **PyPI ship 확인** (이미 완료된 경우 skip)
2. **5번 시작** — pl/cs polish (가장 큰 gain, 작은 risk)
3. **8번** — README/HF Space hero 재구성 (UHPS-full 40/40 강조)
4. **트랙 B 확장** — Polish nasals, Hungarian
5. (시간 남으면) **6번 fa** dictionary 기반 시도

---

## 한 줄 요약

> **이번 세션은 NIKL +5.5pt, UHPS-full primary 40/40 spec compliant, French nasals 작동, 두 critical bug fix까지. 15 패치 모두 sandbox dist/ 준비 완료. host에서 PyPI v3.37 publish하면 끝.**
