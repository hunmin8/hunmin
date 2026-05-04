# PR 요약

(한두 줄로 무엇을 변경했는지)

## 변경 유형

- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 🌐 New language module
- [ ] 📝 Docs / examples
- [ ] ⚡ Performance
- [ ] ♻️ Refactor (no behavior change)
- [ ] 🧪 Tests
- [ ] 🔧 Tooling / CI

## 영향 범위

- 변경된 모듈: `hunmin/...`
- 영향 받는 lang: ...
- API 변경: (없음 / 추가만 / breaking)

## 검증

- [ ] `pytest tests/` 통과
- [ ] `python scripts/eval_heldout_1000.py` → **1015/1015 (100.0%)** 유지
- [ ] `python scripts/eval_all_gold.py` 종합 score 회귀 없음
- [ ] `python -m pytest tests/test_properties.py` 통과 (해당 시)
- [ ] CHANGELOG.md 항목 추가
- [ ] 새 단어/기능에 gold/예시 추가

## 추가 컨텍스트

(스크린샷, 벤치마크, 참고 링크 등)
