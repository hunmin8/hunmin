# Hunmin — NEXT TODO (post v3.30)

## 즉시 할 일 (host에서)

### 1. PyPI ship
```bash
cd ~/koboltmine/hunmin_pkg
python -m twine upload dist/hunmin-3.30.0-py3-none-any.whl dist/hunmin-3.30.0.tar.gz
```

### 2. 옛 dist 정리 (sandbox 권한 한계로 host에서)
```bash
cd ~/koboltmine/hunmin_pkg/dist
ls hunmin-3.2[0-9]* | grep -v 3.30 | xargs rm  # 모든 < 3.30 wheel/tar.gz 정리
```

### 3. HF Space 갱신
```bash
cd ~/koboltmine/hunmin_pkg/hf_space
# requirements.txt는 이미 hunmin[cjk]>=3.30.0
git add . && git commit -m "v3.30 — Russian ь soft-sign, accuracy 75.5%"
git push hf main  # HF Space remote
```

### 4. GitHub release tag
```bash
git tag -a v3.30.0 -m "v3.30 — Russian soft-sign + cumulative session improvements"
git push origin v3.30.0
```

## 다음 세션 우선순위

### 🎯 트랙 A: NIKL 호환층 추가 정확도 (현재 75.5%, 천장 ~85%)
- **pl (66.7%)** — Cl 클러스터 미적용, 어말 'k' 분리, 'ę/ą' nasal 처리
  - `_intervocalic_l_post`를 pl도 활성화 (regression 없이) → +5pt
- **cs (67.5%)** — Cl 클러스터 미적용
- **hr (67.6%)** — Croatian 모듈은 jamo-list 구조 → 일반 post-process 적용 어려움
  - 모듈 재구조화 필요. or 영향 큰 단어만 phonemize 단계에서 fix
- **sr (73.5%)** — hr 의존 (Cyrillic→Latin → hr 호출). hr 개선 시 자동 따라감
- **hu (73.3%)** — accent 처리 + ly/ny 등 digraph
- **ro (70.3%)** — diphthong 처리

### 🎯 트랙 B: UHPS-full primary product 강화
- **Hand-curated UHPS-full gold** — 현재 143 entries는 자동 생성 baseline
  - IPA → UHPS-full을 spec 따라 손으로 검증
  - 엔진 어색 케이스 발견 → 본질적 개선
- **UHPS spec doc 강화** — `docs/UHPS_SPEC.md`
- **HF Space UHPS-full 첫 탭** — 다양한 케이스 시연

### 🎯 트랙 C: 어려운 갭 (구조적)
- **fa (21.1%)** — Persian short vowel insertion이 진짜 문제. 현재 default 'a' 삽입.
  - 단어별 stress/vowel 패턴 학습이나 dictionary 기반 보강 필요
- **en (60.7%)** — CMU phoneme handling 어색 (-ower/-tion/-et endings)
  - High-freq override 확장이 가장 빠름
  - 또는 g2p-en optional dependency 활용

## 이번 세션 (v3.23-v3.30) 정리

### 8 patches shipped, +5.5pt 전체 정확도

| 버전 | 핵심 변경 | 정확도 변화 |
|------|----------|----|
| v3.23 | Tibetan/Khmer/Lao/Burmese letter→IPA | leak 0 보장 |
| v3.24 | Held-out 1015-row gold 신설 | 70.0% (baseline) |
| v3.25 | es/pt/it gap fixes | 70.0 → 72.6 |
| v3.26 | vi/nl polish | 72.6 → 73.9 |
| v3.27 | UHPS-full eval 35→143 entries | (primary product strengthened) |
| v3.28 | German polish (st/sp/tz/ck) | 73.9 → 74.9 |
| v3.29 | French Cl-cluster | 74.9 → 75.3 |
| v3.30 | Russian ь soft-sign | 75.3 → 75.5 |

### 언어별 진행 (v3.24 → v3.30)
- es: 84.1 → 98.6 (+14.5)
- pt: 52.1 → 70.8 (+18.7)
- it: 80.7 → 94.7 (+14.0)
- vi: 43.6 → 64.1 (+20.5)
- nl: 46.9 → 62.5 (+15.6)
- de: 60.8 → 80.4 (+19.6)
- fr: 68.8 → 75.0 (+6.2)
- ru: 69.1 → 72.7 (+3.6)

### Test count: 379 → 511 (+132)

## 알려진 제약

- **Cyrillic→Latin sr 의존성**: Serbian 모듈이 hr 룰을 재사용하므로 hr 모듈 변경은 sr에 그대로 영향. hr 모듈은 `_phonemize` 단계에서 jamo string list를 만들어 단순 post-process가 어려움.
- **fa (Persian)**: short vowel은 IPA 입력에 표기 안 되므로 default 'a' 삽입이 한계. 진짜 개선엔 신경망/dictionary 필요.
- **en**: CMU phoneme → Hangul 매핑이 깊은 구조. 천장 ~75% 정도 (override 없이).
