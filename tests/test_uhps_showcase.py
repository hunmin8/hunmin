"""UHPS-full hand-curated showcase test (v3.31).

40 hand-curated entries showing every UHPS-full feature with rationale.
Each entry's expected output is verified against the spec, NOT auto-generated.

If a test fails: either the engine deviates from spec (fix engine) or
the spec interpretation needs adjustment (update entry rationale).

This is the canonical "what UHPS-full is" — the primary product test.
"""
import json
from pathlib import Path

import pytest

from hunmin.core.universal import transcribe_universal

GOLD = Path(__file__).parent / 'gold' / 'uhps_showcase.jsonl'


def load_showcase():
    with open(GOLD, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip() and not l.startswith('#')]


SHOWCASE = load_showcase()


@pytest.mark.parametrize(
    'entry', SHOWCASE,
    ids=[f"{e['id']}-{e['feature'][:30].replace(' ','_')}" for e in SHOWCASE]
)
def test_showcase_entry(entry):
    """Each showcase IPA → UHPS-full output matches hand-curated expected."""
    ipa = entry['ipa']
    expected = entry['uhps_full_expected']
    out = transcribe_universal(
        ipa, 'ipa', uhps='full',
        tone_style='middledot', safe_fonts=False,
    )
    # Tone bars use 'arrow' style by default for tone bar input
    if any(c in ipa for c in '˩˨˧˦˥'):
        out = transcribe_universal(
            ipa, 'ipa', uhps='full',
            tone_style='arrow', safe_fonts=False,
        )
    assert out == expected, (
        f"\n  Feature: {entry['feature']}"
        f"\n  IPA:     {ipa!r}"
        f"\n  Got:     {out!r}"
        f"\n  Expect:  {expected!r}"
        f"\n  Why:     {entry['rationale']}"
    )


def test_showcase_count():
    """Sanity: showcase has substantive coverage."""
    assert len(SHOWCASE) >= 30, f"Showcase only has {len(SHOWCASE)} entries"


def test_showcase_features_unique():
    """Each entry should have unique feature label (no duplicates)."""
    features = [e['feature'] for e in SHOWCASE]
    # Allow some duplicate variants (e.g. multiple /f/ tests) but warn
    duplicates = [f for f in set(features) if features.count(f) > 2]
    assert not duplicates, f"Too many duplicate features: {duplicates}"
