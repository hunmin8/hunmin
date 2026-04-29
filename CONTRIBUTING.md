# Contributing to Hunmin

기여를 환영합니다.

## 개발 환경 셋업

```bash
git clone https://github.com/meshpop/hunmin.git
cd hunmin
pip install -e ".[cjk]"
pip install pytest
```

## 테스트 실행

```bash
pytest tests/                  # 단위 테스트
python tests/bench_en.py       # 영어 벤치마크 (NIKL 표기 265단어)
python tests/bench_multi.py    # 다국어 벤치마크 (10개 언어 116단어)
```

## 변경 사항 유형

### 1. NIKL 외래어 표기 단어 추가 (가장 가벼움)

`hunmin/core/english.py`의 `_HANGUL_OVERRIDES` 또는 `hunmin/api.py`의 `_LANG_OVERRIDES`에 추가:

```python
# english.py
_HANGUL_OVERRIDES = {
    'newword': '뉴워드',
    ...
}
```

가능하면 `tests/gold/en_gold.tsv` 또는 `tests/gold/multi_gold.tsv`에 케이스 추가.

### 2. 룰 변경 (영어 파이프라인)

영어는 6단계 fallback. 각 단계는 `hunmin/core/english.py`에서 함수로 분리됨:

1. `_HANGUL_OVERRIDES` — NIKL 직접 매핑
2. `_is_acronym` / `_acronym_phonemes` — 약어 letter-by-letter
3. `get_phonemes` — CMU 사전 (135K)
4. `_compound_phonemes` — 합성어 (firebase → fire+base)
5. `_morphology_phonemes` — 형태소 (re+produce+ible)
6. `_g2p_en_phonemes` — g2p-en (옵션)
7. `_phonics_fallback` — letter cluster pattern

룰 변경 시 반드시 두 벤치마크 모두 회귀 확인.

### 3. 새 언어 추가

1. `hunmin/core/<lang>.py` 모듈 생성 (transcribe_xx 함수)
2. `hunmin/core/__init__.py`에 export
3. `hunmin/api.py`의 `_PRECISE` 또는 `_DICT_LANGS`에 등록
4. `_LANG_OVERRIDES`에 NIKL 표기 단어 추가
5. `tests/gold/multi_gold.tsv`에 검증 케이스 추가

## PR 체크리스트

- [ ] `pytest tests/` 통과
- [ ] `python tests/bench_en.py` 회귀 없음 (98%+ 유지)
- [ ] `python tests/bench_multi.py` 회귀 없음 (100% 유지)
- [ ] 새 단어/케이스는 gold corpus에 추가
- [ ] 룰 변경 시 README CHANGELOG에 한 줄

## 릴리즈 프로세스

1. `pyproject.toml`과 `hunmin/__init__.py`의 version 동시 업데이트
2. README CHANGELOG에 변경사항 추가
3. `git tag v1.x.y && git push --tags` — GitHub Actions가 자동 PyPI 배포
4. (수동) `python -m build && twine upload dist/*`도 가능

## 핵심 디자인 원칙

- **순수 룰 기반 default** — ML/외부 API 없이 동작
- **결정적 출력** — 같은 입력은 항상 같은 출력
- **NIKL 외래어 표기법 준수** — 한국 표준 컨벤션
- **rough but mostly right** — 100%는 불가능, 95%+가 목표
