# Performance

Hunmin은 순수 Python (zero-dep core)이지만 매우 빠릅니다.

## 측정 결과 (`scripts/benchmark.py --n 10000`)

```
=== Hunmin Benchmark (n=10000) ===

--- Cache hot (반복 호출) ---
transcribe() sequential        ~ 1.4ms     ~7,000,000 calls/s   0.14µs/call
transcribe_batch()             ~ 1.5ms     ~6,500,000 calls/s   0.15µs/call
atranscribe_batch()            ~  68ms     ~  150,000 calls/s   6.7µs/call

--- Cache miss (unique words) ---
Sequential                     ~ 26ms     ~  390,000 calls/s
Batch                          ~ 24ms     ~  410,000 calls/s

--- Cache disabled ---
cache=False                    ~  4ms     ~2,500,000 calls/s
```

## 분석

### LRU 캐시 효과

| 워크로드 | 처리량 | 분석 |
|---------|-------|------|
| Cache hit (1µs) | **7M calls/s** | dict lookup + return — 거의 free |
| Cache miss (rule) | **400K calls/s** | rule module 실행 |
| `cache=False` | **2.5M calls/s** | wrapper overhead 없이 direct call |

→ 반복 호출이 많은 워크로드 (예: 사전 정렬, 검색 보조)는 **LRU 캐시 hit이 결정적**.

### Sync vs Async

**Async가 sync보다 느림** — CPU-bound 작업이라 asyncio overhead만 추가.

권장: **CPU-bound = sync 사용**. async는 IO와 섞일 때만 의미.

### Batch overhead

Batch와 sequential 거의 동일 — Python list comprehension이 이미 최적. Batch는 **편의성 + skip_errors** 정도 이점.

## 사용 가이드

### 단일 호출
```python
from hunmin import transcribe
transcribe('Mozart', 'de')  # 0.14µs (cache hit) 또는 ~10µs (cache miss)
```

### 대량 처리
```python
from hunmin import transcribe_batch
words = [...]  # 100,000개
results = transcribe_batch(words, lang='en')
# 약 25ms (cache miss 가정), 0.7ms (cache hit 가정)
```

### 캐시 관리
```python
from hunmin import transcribe_cache_info, transcribe_cache_clear

# 상태 조회
info = transcribe_cache_info()
print(info)  # CacheInfo(hits=..., misses=..., maxsize=2048, ...)

# 메모리 회수 (long-running 서비스에서 주기적)
transcribe_cache_clear()
```

### 캐시 비활성화 (memory-constrained)
```python
transcribe('Mozart', 'de', cache=False)
```

## 병목 분석

### 핫스팟 (rule 호출 시)
1. CMU dict lookup (en) — ~100ns
2. `_align_phonemes` — ~3µs
3. `_assemble` (jamo composition) — ~2µs
4. Override dict 검사 — ~50ns

### CJK
pykakasi/pypinyin 호출이 ~1ms — 외부 라이브러리 의존.

## 최적화 로드맵 (장기)

### 1. Rust/PyO3 핵심 모듈 (`P5.16`)
- CMU lookup + alignment를 Rust로
- 예상 5-10x speedup
- 별도 프로젝트 (장기)

### 2. WASM build (`P5.17`)
- 브라우저 사용 — 서버 없이 hunmin 동작
- pyodide 또는 pure JS port
- 별도 프로젝트 (장기)

### 3. 메모리
- 현재 부팅 시 CMU dict ~135K entries 로드 (수십 MB)
- mmap 또는 lazy load 가능 (현재는 단순 dict)

## 측정 환경
- Apple M1, Python 3.10
- 단일 thread, 단일 core
- `transcribe_cache_clear()` 후 warmup 1회

다른 환경에서 다를 수 있음.
