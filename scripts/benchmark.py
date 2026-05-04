#!/usr/bin/env python3
"""Hunmin throughput benchmark.

3가지 워크로드 측정:
  1. Cache hot (반복 호출, LRU 효과)
  2. Cache miss (unique 단어들)
  3. Async batch (asyncio.gather)

Run:
    python scripts/benchmark.py
    python scripts/benchmark.py --n 10000
"""
from __future__ import annotations
import argparse, time, random, asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hunmin import (
    transcribe, transcribe_batch, atranscribe_batch,
    transcribe_cache_clear, transcribe_cache_info,
)


SAMPLES = [
    *[(w, 'en') for w in ['hello','world','student','computer','airport',
                            'beautiful','wonderful','grateful','communication',
                            'organization','breakfast','sandwich','elevator']],
    *[(w, 'de') for w in ['Mozart','Bach','Wagner','Berlin','Hamburg','München','Köln']],
    *[(w, 'es') for w in ['familia','casa','agua','amor','escuela','restaurante']],
    *[(w, 'fr') for w in ['Bonjour','Merci','Paris','Marseille','baguette']],
    *[(w, 'it') for w in ['pizza','pasta','spaghetti','tiramisu']],
    *[(w, 'ru') for w in ['Москва','Толстой','Чехов','Достоевский']],
    *[(w, 'ja') for w in ['東京','大阪','京都','北海道','寿司']],
    *[(w, 'zh') for w in ['北京','上海','龙','茶','长城']],
]


def bench_cache_hot(n: int):
    """Repeated calls — LRU cache hot."""
    inputs = [random.choice(SAMPLES) for _ in range(n)]
    # Warm
    for w, l in SAMPLES: transcribe(w, l)

    # Sequential
    t0 = time.perf_counter()
    for w, l in inputs:
        transcribe(w, l)
    dt_seq = time.perf_counter() - t0

    # Batch
    t0 = time.perf_counter()
    transcribe_batch(inputs)
    dt_bat = time.perf_counter() - t0

    # Async
    t0 = time.perf_counter()
    asyncio.run(atranscribe_batch(inputs))
    dt_async = time.perf_counter() - t0

    return dt_seq, dt_bat, dt_async


def bench_cache_miss(n: int):
    """Unique words — every call is cache miss."""
    inputs = [(f'word{i:05d}', 'en') for i in range(n)]
    transcribe_cache_clear()

    t0 = time.perf_counter()
    for w, l in inputs:
        transcribe(w, l)
    dt_seq = time.perf_counter() - t0

    transcribe_cache_clear()
    t0 = time.perf_counter()
    transcribe_batch(inputs)
    dt_bat = time.perf_counter() - t0

    return dt_seq, dt_bat


def bench_uncached(n: int):
    """Cache=False forced."""
    inputs = [random.choice(SAMPLES) for _ in range(n)]
    t0 = time.perf_counter()
    for w, l in inputs:
        transcribe(w, l, cache=False)
    return time.perf_counter() - t0


def fmt(name, dt, n):
    rate = n / dt
    return f'{name:30} {dt*1000:8.1f}ms  {rate:>12,.0f} calls/s  {dt/n*1e6:6.2f}µs/call'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    print(f'=== Hunmin Benchmark (n={args.n}) ===\n')

    print('--- Cache hot (반복 호출) ---')
    dt_seq, dt_bat, dt_async = bench_cache_hot(args.n)
    print(fmt('transcribe() sequential', dt_seq, args.n))
    print(fmt('transcribe_batch()', dt_bat, args.n))
    print(fmt('atranscribe_batch()', dt_async, args.n))

    print('\n--- Cache miss (unique words) ---')
    dt_seq, dt_bat = bench_cache_miss(args.n)
    print(fmt('Sequential', dt_seq, args.n))
    print(fmt('Batch', dt_bat, args.n))

    print('\n--- Cache disabled ---')
    dt_uc = bench_uncached(args.n)
    print(fmt('cache=False', dt_uc, args.n))

    print(f'\nFinal cache: {transcribe_cache_info()}')


if __name__ == '__main__':
    main()
