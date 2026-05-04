# API Stability Policy

Hunmin은 [Semantic Versioning](https://semver.org/)을 따릅니다 (`MAJOR.MINOR.PATCH`).

## 보증 수준

### 🟢 Tier 1 — Stable Public API (semver 적용)

다음은 **MINOR 버전에선 깨지지 않습니다**:

```python
from hunmin import (
    transcribe,                # 핵심 변환 함수
    transcribe_batch,          # 배치 변환 (v3.42+)
    atranscribe,               # async (v3.42+)
    atranscribe_batch,         # async batch (v3.42+)
    views,                     # multi-view dict
    supported_languages,       # 언어 목록
    transcribe_cache_info,     # 캐시 상태
    transcribe_cache_clear,    # 캐시 클리어
    to_romanization,           # Hangul → roman/IPA (v3.42+)
    hangul_to_rr,
    hangul_to_ipa,
)

# Mode 상수
HUNMIN_NIKL, HUNMIN_PHONETIC, UHPS_CORE, UHPS_JAMO, UHPS_FULL
```

이 함수들의:
- **Signature** (positional 파라미터 순서, 이름)
- **반환 타입** (str, dict, list)
- **에러 동작** (TypeError/ValueError)

는 MAJOR 변경 없이는 깨지지 않습니다.

### 🟡 Tier 2 — Internal but exposed

```python
from hunmin import Hunmin
h = Hunmin()
h.transcribe(...)  # 직접 사용 비권장
```

`Hunmin` class는 내부 인스턴스라 메서드 시그니처가 PATCH 버전에서도 변할 수 있습니다.

### 🔴 Tier 3 — Internal (변경 가능)

다음은 언제든 변경/제거될 수 있습니다:
- `hunmin.api._LANG_OVERRIDES` (private dict)
- `hunmin.api._COMMON_OVERRIDES`
- `hunmin.core._HANGUL_OVERRIDES` 등 (각 모듈 내부)
- `hunmin.api._hangul_inner` 등 underscore 함수
- 모든 underscore-prefix 식별자

## 출력 안정성

### 🟢 NIKL gold (heldout_1000) — **100% 유지 보증**
1015/1015 entries는 MINOR 버전에서 회귀 안 됨. CI가 강제 (PR이 깨면 자동 fail).

### 🟡 휴리스틱 / 룰 출력 — 개선 가능
gold에 없는 단어의 출력은 정확도 향상을 위해 **MINOR 버전에서 변경 가능**합니다.

예: `transcribe('xenophobia', 'en')`이 `'제너포비아'` (v3.40) → `'제노포비아'` (v3.41)로 바뀌었음. 이런 변화는 changelog에 명시되지만 정상.

### 🟢 _LANG_OVERRIDES에 등록된 단어 — 보장됨
명시적으로 override된 단어는 변하지 않음.

## 의존성 정책

### 🟢 Required (코어)
- Python 3.8+
- 표준 라이브러리만 (외부 deps 0개)

### 🟡 Optional
- `pykakasi`, `pypinyin`, `hanja` — CJK 지원 (`pip install hunmin[cjk]`)
- `epitran` — Universal IPA fallback (`pip install hunmin[universal]`)
- `gradio` — Web UI (`pip install hunmin[demo]`)
- `fastapi`, `uvicorn` — REST API (`hunmin/server.py`)

이런 optional deps는 자유롭게 추가/변경됩니다. 단, 코어 동작에 영향 없음.

## Deprecation 정책

기능 제거 시:
1. **MINOR 버전**: `DeprecationWarning` 추가, 1+ MINOR 사이클 유지
2. **MAJOR 버전**: 실제 제거

예: `level` 파라미터 (legacy) → `mode` 파라미터 권장. `level`도 계속 동작.

## Breaking changes (역대)

| Version | 변경 |
|---------|------|
| v1.0.0 | Initial public API |
| v3.0.0 | API 재설계 (mode constants 도입) |
| (향후 v4.0.0) | TBD |

## 의문 사항

API 변경이 깨지는지 불확실하면 [GitHub Issue](https://github.com/meshpop/hunmin/issues)로 문의.
