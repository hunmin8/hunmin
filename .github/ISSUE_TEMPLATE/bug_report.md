---
name: 🐛 Bug report
about: 잘못된 한글 변환 / crash / 예상과 다른 동작
title: "[Bug] "
labels: bug
---

## 재현 코드

```python
from hunmin import transcribe
transcribe('...', 'xx')
```

## 기대 출력

`...`

## 실제 출력

`...`

## 환경

- Python: (`python --version`)
- hunmin: (`pip show hunmin | grep Version`)
- OS: (macOS/Linux/Windows)
- Optional deps: pykakasi/pypinyin/hanja/epitran 설치 여부

## NIKL 외래어 표기 근거

- 표준국어대사전 등재형: ...
- 또는 출처 (외래어 표기법 항목):  ...

(NIKL 컨벤션과 다른 출력이라면 출처를 적어주세요)

## 재현 빈도

- [ ] 항상 (deterministic)
- [ ] 가끔
- [ ] 한 번만
