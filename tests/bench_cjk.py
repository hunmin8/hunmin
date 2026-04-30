#!/usr/bin/env python3
"""CJK benchmark — large-scale ja/zh accuracy."""
import sys
from collections import defaultdict
from hunmin import transcribe


def main(path, lang):
    cases = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split('\t')
            if len(parts) < 2: continue
            cat = parts[2] if len(parts) > 2 else 'misc'
            cases.append((parts[0], parts[1], cat))

    by_cat = defaultdict(lambda: {'total':0,'exact':0,'misses':[]})
    total, total_ok = 0, 0
    for word, gold, cat in cases:
        got = transcribe(word, lang)
        is_ok = (got == gold)
        by_cat[cat]['total'] += 1
        total += 1
        if is_ok:
            by_cat[cat]['exact'] += 1
            total_ok += 1
        else:
            by_cat[cat]['misses'].append((word, gold, got))

    print(f'=== {lang} bench: {total} words ===')
    print(f'Total: {total_ok}/{total} = {100*total_ok/total:.1f}%')
    print()
    print('By category:')
    for cat in sorted(by_cat.keys()):
        s = by_cat[cat]
        print(f'  {cat:<10} {s["exact"]}/{s["total"]} ({100*s["exact"]/s["total"]:.0f}%)')
    print()
    misses = sum((s['misses'] for s in by_cat.values()), [])
    print(f'Misses ({len(misses)}):')
    for word, gold, got in misses[:40]:
        print(f'  {word:<14} gold={gold:<12} got={got}')


if __name__ == '__main__':
    path = sys.argv[1]
    lang = sys.argv[2]
    main(path, lang)
