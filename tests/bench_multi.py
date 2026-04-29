#!/usr/bin/env python3
"""Multi-language benchmark."""
from hunmin import transcribe
from collections import defaultdict
import sys


def main(path):
    cases = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split('\t')
            if len(parts) < 3: continue
            cases.append((parts[0], parts[1], parts[2]))

    by_lang = defaultdict(lambda: {'total': 0, 'exact': 0, 'misses': []})
    for word, gold, lang in cases:
        got = transcribe(word, lang)
        is_exact = (got == gold)
        by_lang[lang]['total'] += 1
        if is_exact:
            by_lang[lang]['exact'] += 1
        else:
            by_lang[lang]['misses'].append((word, gold, got))

    total, total_ok = 0, 0
    print(f'{"lang":<5} {"acc":>10} {"misses"}')
    print('-' * 50)
    for lang in sorted(by_lang.keys()):
        s = by_lang[lang]
        ex, tot = s['exact'], s['total']
        total += tot; total_ok += ex
        miss_strs = [f'{w}→{g}({got})' for w,g,got in s['misses'][:3]]
        miss_str = ', '.join(miss_strs) + ('...' if len(s['misses']) > 3 else '')
        print(f'{lang:<5} {ex}/{tot} ({100*ex/tot:.0f}%)  {miss_str}')
    print('-' * 50)
    print(f'Total: {total_ok}/{total} = {100*total_ok/total:.1f}%')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'tests/gold/multi_gold.tsv')
