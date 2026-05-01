"""Regression test for held-out 1000-row gold corpus.

Locks in current rule-only accuracy. If this test fails, either:
  - A rule change caused a regression (fix the rule)
  - Gold data changed (update baselines below)

Run script for full breakdown:
  python scripts/eval_heldout_1000.py --verbose
"""
from pathlib import Path

import pytest

from hunmin import transcribe

GOLD = Path(__file__).parent / 'gold' / 'heldout_1000.tsv'

# Per-language minimum exact-match accuracy (% of gold rows). Set 1-2pp below
# observed values to allow minor downstream improvements without breaking tests.
# v3.24 baseline (2026-05): observed values shown after `:`
MIN_EXACT_PCT = {
    'cs': 65.0,   # observed 67.5
    'de': 58.0,   # observed 60.8
    'en': 58.0,   # observed 60.7
    'es': 96.0,   # observed 98.6 (v3.25 rr→ㄹ, Cl-cluster)
    'fa': 18.0,   # observed 21.1 (Persian short-vowel hard limit)
    'fr': 65.0,   # observed 68.8
    'hr': 65.0,   # observed 67.6
    'hu': 70.0,   # observed 73.3
    'id': 88.0,   # observed 91.3
    'it': 92.0,   # observed 94.7 (v3.25 gemination drop)
    'ja': 92.0,   # observed 96.0
    'nl': 44.0,   # observed 46.9
    'pl': 64.0,   # observed 66.7
    'pt': 68.0,   # observed 70.8 (v3.25 rr→/h/, final-o→ㅜ)
    'ro': 67.0,   # observed 70.3
    'ru': 65.0,   # observed 69.1
    'sk': 76.0,   # observed 80.0
    'sr': 70.0,   # observed 73.5
    'tr': 80.0,   # observed 84.8
    'vi': 40.0,   # observed 43.6 (Vietnamese diacritic edge cases)
    'zh': 90.0,   # observed 94.2
}

MIN_OVERALL_EXACT_PCT = 70.0   # observed 72.6 (v3.25)
MIN_OVERALL_CER_PCT = 84.0     # observed 86.1 (v3.25)


def _edit_distance(a, b):
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


def _char_acc(p, g):
    if not g:
        return 1.0 if not p else 0.0
    return max(0.0, 1.0 - _edit_distance(p, g) / len(g))


def _load():
    rows = []
    with open(GOLD, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                rows.append((parts[0], parts[1], parts[2]))
    return rows


def _evaluate():
    rows = _load()
    by_lang = {}
    for word, expected, lang in rows:
        try:
            pred = transcribe(word, lang)
        except Exception:
            pred = '__ERROR__'
        d = by_lang.setdefault(lang, {'n': 0, 'exact': 0, 'char': 0.0})
        d['n'] += 1
        if pred == expected:
            d['exact'] += 1
        d['char'] += _char_acc(pred, expected)
    return by_lang


@pytest.fixture(scope='module')
def eval_results():
    return _evaluate()


@pytest.mark.parametrize('lang,min_pct', sorted(MIN_EXACT_PCT.items()))
def test_per_language_accuracy(eval_results, lang, min_pct):
    d = eval_results.get(lang)
    assert d is not None, f'No rows found for lang={lang}'
    pct = 100 * d['exact'] / d['n']
    assert pct >= min_pct, (
        f'{lang}: exact match {pct:.1f}% < min {min_pct}% '
        f'({d["exact"]}/{d["n"]} rows)'
    )


def test_overall_exact_accuracy(eval_results):
    n = sum(d['n'] for d in eval_results.values())
    ex = sum(d['exact'] for d in eval_results.values())
    pct = 100 * ex / n
    assert pct >= MIN_OVERALL_EXACT_PCT, (
        f'Overall exact match {pct:.1f}% < min {MIN_OVERALL_EXACT_PCT}% '
        f'({ex}/{n} rows)'
    )


def test_overall_char_accuracy(eval_results):
    n = sum(d['n'] for d in eval_results.values())
    ch = sum(d['char'] for d in eval_results.values())
    pct = 100 * ch / n
    assert pct >= MIN_OVERALL_CER_PCT, (
        f'Overall char accuracy {pct:.1f}% < min {MIN_OVERALL_CER_PCT}% '
        f'({n} rows)'
    )


def test_gold_has_expected_size():
    """Detect accidental gold corpus shrinkage."""
    rows = _load()
    assert len(rows) >= 1000, f'Held-out gold has only {len(rows)} rows'
