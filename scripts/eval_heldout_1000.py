#!/usr/bin/env python3
"""Evaluate hunmin against held-out gold 1000-row corpus.

Usage:
  python scripts/eval_heldout_1000.py [--verbose] [--lang LANG]
  python scripts/eval_heldout_1000.py --json  # output JSON for CI

Reports:
  - Exact match accuracy per language
  - Char-level edit-distance accuracy (CER-style)
  - Per-category breakdown (common/place/food)
  - Top-10 mismatches per language (with --verbose)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from hunmin import transcribe  # noqa: E402

GOLD_PATH = REPO_ROOT / 'tests' / 'gold' / 'heldout_1000.tsv'


def load_gold():
    rows = []
    with open(GOLD_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 3:
                continue
            word, expected, lang = parts[0], parts[1], parts[2]
            cat = parts[3] if len(parts) >= 4 else 'common'
            rows.append((word, expected, lang, cat))
    return rows


def edit_distance(a, b):
    """Levenshtein distance (chars)."""
    if not a:
        return len(b)
    if not b:
        return len(a)
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            if ca == cb:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j-1])
            prev = cur
    return dp[-1]


def char_accuracy(pred, gold):
    """1 - CER, clamped to [0, 1]."""
    if not gold:
        return 1.0 if not pred else 0.0
    return max(0.0, 1.0 - edit_distance(pred, gold) / len(gold))


def evaluate(rows, lang_filter=None):
    by_lang = defaultdict(lambda: {'total': 0, 'exact': 0, 'char_acc': 0.0,
                                    'mismatches': [], 'by_cat': defaultdict(lambda: [0, 0])})
    for word, expected, lang, cat in rows:
        if lang_filter and lang != lang_filter:
            continue
        try:
            pred = transcribe(word, lang)
        except Exception as e:
            pred = f'ERROR:{e}'
        b = by_lang[lang]
        b['total'] += 1
        ca = char_accuracy(pred, expected)
        b['char_acc'] += ca
        if pred == expected:
            b['exact'] += 1
            b['by_cat'][cat][0] += 1
        else:
            b['mismatches'].append((word, expected, pred, ca))
        b['by_cat'][cat][1] += 1
    return by_lang


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verbose', '-v', action='store_true')
    ap.add_argument('--lang', help='filter to single lang code')
    ap.add_argument('--json', action='store_true', help='emit JSON')
    ap.add_argument('--top-mismatches', type=int, default=10)
    args = ap.parse_args()

    rows = load_gold()
    by_lang = evaluate(rows, args.lang)

    if args.json:
        out = {}
        for lang, b in by_lang.items():
            out[lang] = {
                'total': b['total'],
                'exact': b['exact'],
                'exact_pct': round(100 * b['exact'] / b['total'], 1) if b['total'] else 0,
                'char_acc_pct': round(100 * b['char_acc'] / b['total'], 1) if b['total'] else 0,
            }
        total_n = sum(b['total'] for b in by_lang.values())
        total_exact = sum(b['exact'] for b in by_lang.values())
        total_char = sum(b['char_acc'] for b in by_lang.values())
        out['__overall__'] = {
            'total': total_n,
            'exact': total_exact,
            'exact_pct': round(100 * total_exact / total_n, 1) if total_n else 0,
            'char_acc_pct': round(100 * total_char / total_n, 1) if total_n else 0,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print(f'\n=== Hunmin held-out gold evaluation (1015 rows, 21 langs) ===\n')
    print(f'{"lang":6} {"N":>5} {"exact":>7} {"exact%":>8} {"CER%":>8}')
    print('-' * 40)
    total_n = 0
    total_exact = 0
    total_char = 0.0
    for lang in sorted(by_lang):
        b = by_lang[lang]
        if not b['total']:
            continue
        ex_pct = 100 * b['exact'] / b['total']
        ca_pct = 100 * b['char_acc'] / b['total']
        print(f'{lang:6} {b["total"]:>5} {b["exact"]:>7} {ex_pct:>7.1f}% {ca_pct:>7.1f}%')
        total_n += b['total']
        total_exact += b['exact']
        total_char += b['char_acc']
    print('-' * 40)
    overall_ex = 100 * total_exact / total_n if total_n else 0
    overall_ca = 100 * total_char / total_n if total_n else 0
    print(f'{"ALL":6} {total_n:>5} {total_exact:>7} {overall_ex:>7.1f}% {overall_ca:>7.1f}%')

    if args.verbose:
        print('\n=== Top mismatches per language ===')
        for lang in sorted(by_lang):
            b = by_lang[lang]
            if not b['mismatches']:
                continue
            print(f'\n--- {lang} ({len(b["mismatches"])} mismatches) ---')
            sorted_m = sorted(b['mismatches'], key=lambda x: x[3])
            for word, exp, pred, ca in sorted_m[:args.top_mismatches]:
                print(f'  {word:25} expected: {exp:25} got: {pred:25} (char_acc={ca:.2f})')


if __name__ == '__main__':
    main()
