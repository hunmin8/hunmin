#!/usr/bin/env python3
"""English transcription benchmark."""
from hunmin import transcribe
from collections import defaultdict
import sys

def char_match(a, b):
    """char-level accuracy (longest common subseq)."""
    n, m = len(a), len(b)
    if n == 0 and m == 0: return 1.0
    if n == 0 or m == 0: return 0.0
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1):
        for j in range(1, m+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[n][m] / max(n, m)


def main(path):
    cases = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 2: continue
            word, gold = parts[0], parts[1]
            cat = parts[2] if len(parts) > 2 else 'misc'
            cases.append((word, gold, cat))

    total = len(cases)
    exact = 0
    char_total = 0.0
    by_cat = defaultdict(lambda: {'total':0,'exact':0,'char':0.0})
    misses = []

    for word, gold, cat in cases:
        got = transcribe(word, 'en')
        is_exact = (got == gold)
        char = char_match(got, gold)
        if is_exact:
            exact += 1
            by_cat[cat]['exact'] += 1
        else:
            misses.append((word, gold, got, cat))
        char_total += char
        by_cat[cat]['total'] += 1
        by_cat[cat]['char'] += char

    print(f'=== Overall: {total} words ===')
    print(f'  Exact:    {exact}/{total} = {100*exact/total:.1f}%')
    print(f'  Char-acc: {char_total/total*100:.1f}%')
    print()
    print(f'=== By category ===')
    for cat, s in sorted(by_cat.items()):
        ex = s['exact']; tot = s['total']
        print(f'  {cat:<10} exact={ex}/{tot}={100*ex/tot:.0f}%  char={s["char"]/tot*100:.0f}%')
    print()
    print(f'=== Misses (first 30) ===')
    for word, gold, got, cat in misses[:30]:
        print(f'  [{cat:<8}] {word:<14} gold={gold:<12} got={got}')
    if len(misses) > 30:
        print(f'  ... +{len(misses)-30} more')


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'tests/gold/en_gold.tsv'
    main(path)
