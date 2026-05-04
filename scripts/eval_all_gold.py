#!/usr/bin/env python3
"""모든 gold corpus에 대한 종합 검증 (heldout_1000 + en/ja/zh/multi).

각 corpus의 형식이 다르므로 별도 파싱.
"""
from __future__ import annotations
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from hunmin import transcribe  # noqa


def edit_distance(a, b):
    if not a: return len(b)
    if not b: return len(a)
    dp = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            dp[j] = prev if ca == cb else 1 + min(prev, dp[j], dp[j-1])
            prev = cur
    return dp[-1]


def char_acc(p, g):
    return max(0.0, 1.0 - edit_distance(p, g)/len(g)) if g else (1.0 if not p else 0.0)


def load_2col(path, lang):
    """word<TAB>gold (lang fixed)"""
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) < 2: continue
        rows.append((parts[0], parts[1], lang))
    return rows


def load_3col(path, default_lang=None):
    """word<TAB>gold<TAB>(lang|category)"""
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) < 2: continue
        word = parts[0]; gold = parts[1]
        third = parts[2] if len(parts) >= 3 else ''
        # 3rd column: lang code or category
        lang = third if third in ('en','ja','zh','ko','fr','de','es','it','ru','pt','nl','pl','vi','hu','tr','id','ro','cs','sk','hr','sr','fa','bs','mk') else default_lang
        if lang is None:
            continue
        rows.append((word, gold, lang))
    return rows


CORPUS = [
    ('heldout_1000', 'tests/gold/heldout_1000.tsv', None),  # 4-col with lang
    ('en_gold', 'tests/gold/en_gold.tsv', 'en'),
    ('en_heldout', 'tests/gold/en_heldout.tsv', 'en'),
    ('en_heldout_diverse', 'tests/gold/en_heldout_diverse.tsv', 'en'),
    ('ja_gold', 'tests/gold/ja_gold.tsv', 'ja'),
    ('ja_wikidata', 'tests/gold/ja_wikidata.tsv', 'ja'),
    ('zh_wikidata', 'tests/gold/zh_wikidata.tsv', 'zh'),
    ('multi_gold', 'tests/gold/multi_gold.tsv', None),
    ('multi_heldout', 'tests/gold/multi_heldout.tsv', None),
]


def main():
    total_n = 0
    total_exact = 0
    total_char = 0.0
    grand_lang = defaultdict(lambda: [0, 0, 0.0])

    print(f'{"corpus":24} {"N":>5} {"exact":>7} {"exact%":>8} {"CER%":>8}')
    print('-' * 60)
    for name, path, default_lang in CORPUS:
        path = ROOT / path
        if not path.exists():
            continue
        if default_lang is None:
            # 4-col: word\tgold\tlang\tcat
            rows = []
            for line in open(path, encoding='utf-8'):
                line = line.rstrip('\n')
                if not line or line.startswith('#'): continue
                parts = line.split('\t')
                if len(parts) < 3: continue
                rows.append((parts[0], parts[1], parts[2]))
        else:
            rows = load_2col(path, default_lang)
        n = len(rows)
        ex = 0
        ca = 0.0
        for word, gold, lang in rows:
            try:
                pred = transcribe(word, lang)
            except Exception:
                pred = ''
            grand_lang[lang][0] += 1
            if pred == gold:
                ex += 1
                grand_lang[lang][1] += 1
            ac = char_acc(pred, gold)
            ca += ac
            grand_lang[lang][2] += ac
        total_n += n; total_exact += ex; total_char += ca
        print(f'{name:24} {n:>5} {ex:>7} {100*ex/n:>7.1f}% {100*ca/n:>7.1f}%')

    print('-' * 60)
    print(f'{"ALL":24} {total_n:>5} {total_exact:>7} {100*total_exact/total_n:>7.1f}% {100*total_char/total_n:>7.1f}%')

    print()
    print(f'{"lang":6} {"N":>5} {"exact":>7} {"exact%":>8} {"CER%":>8}')
    print('-' * 40)
    for lang in sorted(grand_lang):
        n, ex, ca = grand_lang[lang]
        print(f'{lang:6} {n:>5} {ex:>7} {100*ex/n:>7.1f}% {100*ca/n:>7.1f}%')

if __name__ == '__main__':
    main()
