# Hunmin — NEXT TODO (post v3.35)

## 즉시 할 일 (host에서 실행)

### 1. PyPI publish
```bash
cd ~/koboltmine/hunmin_pkg
python -m twine upload dist/hunmin-3.35.0-py3-none-any.whl dist/hunmin-3.35.0.tar.gz
```

### 2. Git tag + push
```bash
git add . && git commit -m "v3.35 — 40/40 UHPS-full showcase, NIKL 75.5%, French nasals + Russian palatalization"
git tag -a v3.35.0 -m "v3.35 — All UHPS-full primary product gaps closed"
git push origin main v3.35.0
```

### 3. HF Space sync
```bash
cd ~/koboltmine/hunmin_pkg/hf_space
git add . && git commit -m "v3.35 — Feature Gallery tab"
git push hf main
```

### 4. dist/ cleanup (옛 wheel 정리)
```bash
cd ~/koboltmine/hunmin_pkg/dist
ls hunmin-3.{2[0-9],3[0-4]}* | xargs rm  # < 3.35 정리
```

## 다음 세션 (E 트랙 — NIKL polish)

가능하지만 모듈 구조 careful change 필요:

### pl (66.7%, 16 mismatches)
- 어말 'k' 받침 흡수 → separate 크 (rynek 리네크)
- chl Cl 클러스터 (chleb 흘레프)
- intervocalic l 받침 (ulica 울리차) — 이전 시도 회귀로 revert됨
- ą/ę nasal 처리

### cs (67.5%, 13 mismatches)
- 비슷한 패턴 (cs 모듈은 hr보다 모듈식 — Cl 클러스터 추가 가능)

### hu (73.3%, 8 mismatches)
- 'gy/ny/ly/ty' palatal digraph 정밀화
- accent + cs/sz 추가 case

### ro (70.3%, 11 mismatches)
- 'ie/iu/ia' diphthong 처리
- ce/ci/ge/gi 정확도

### hr (67.6%, 12 mismatches) — 가장 어려움
- 모듈이 jamo string list 출력 → 일반 post-process 어려움
- 모듈 재구조화 필요 또는 _phonemize 단계에서 직접 fix

### sr (73.5%) — hr 의존
- hr 개선 시 자동 따라감

### Estimated gain: +3pt 전체 (75.5 → 78.5%)

## UHPS-full 더 정밀화 (트랙 B 확장)

이번 세션에 40/40 showcase 다 작동. 다음 단계:
- Polish ę/ą nasal (Russian과 비슷한 ㆁ 분리 패턴 적용 가능)
- Hungarian a → ɒ → ㆎ (open-o variant) UHPS 매핑 검증
- Vietnamese 6 tones full coverage in showcase
- 새 옛한글 음소 후보: ㅴ /sw/, ㅱ /m̥/?

## 이번 세션 (v3.23 → v3.35) 결산

**13 패치 ship, 본질적 두 트랙 모두 발전**

| 트랙 | v3.24 시작 | v3.35 현재 |
|------|----------|----------|
| NIKL 호환층 | 70.0% | **75.5%** (+5.5pt) |
| UHPS-full primary | 35 entries | **143 + 40 showcase, 40/40 정상** |
| Tests | 379 | **551** (+172) |

**언어별 NIKL 진행 (v3.24 → v3.35)**:
- es: 84.1 → 98.6 (+14.5)
- pt: 52.1 → 70.8 (+18.7)
- it: 80.7 → 94.7 (+14.0)
- vi: 43.6 → 64.1 (+20.5)
- nl: 46.9 → 62.5 (+15.6)
- de: 60.8 → 80.4 (+19.6)
- fr: 68.8 → 75.0 (+6.2)
- ru: 69.1 → 72.7 (+3.6)

**UHPS-full primary product fixes**:
- French nasals (ɛ̃, ɑ̃, ɔ̃, œ̃) → ㆁ받침 보존 (vingt 빙→ㅸ엥, blanc 브랑→브ㄹㆍㆁ)
- Russian palatalization (tʲ → ㄷ받침)
- OLD vowel + nasal 분리 (Bonjour → ㅂㆎㆁᄶ우ᄛ)

**Spec/docs codified**:
- `docs/UHPS_SPEC.md` §9.4 — 40 showcase entries 모두 spec doc 안에 박음
- `tests/gold/uhps_showcase.jsonl` + `tests/test_uhps_showcase.py` — primary product 회귀 lock-in
- `CHANGELOG.md` — Keep-a-Changelog 표준 포맷

**Cleanup**:
- `dist/` v3.34, v3.35 두 가지만 (옛 버전 host에서 정리 필요)
- `.gitignore` 갱신 (eval_results/, benchmark_*.json)

## 알려진 한계

- **fa (21.1%)**: Persian short vowels는 IPA 표기 안 됨 → default 'a' 삽입의 천장
- **en (60.7%)**: CMU phoneme의 -ower/-tion/-et endings 처리는 깊은 구조 변경 필요. Override 확장이 더 빠름
- **hr (67.6%)**: 모듈이 jamo-string-list 구조 → 다른 모듈과 다른 post-process 패턴 필요
