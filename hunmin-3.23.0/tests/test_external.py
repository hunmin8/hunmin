"""External UHPS-full evaluation (v3.21).

NIKL 의존 없는 평가 — UHPS-full 출력이 IPA 음소를 정확히 보존하는지 측정.
phoneme-level audit (test_uhps_spec.py)와 다름: 실제 단어 입력에서 expected 출력 비교.
"""
import json
import pytest
from pathlib import Path
from hunmin.core.universal import transcribe_universal


GOLD_PATH = Path(__file__).parent / 'gold' / 'uhps_external.jsonl'


def load_gold():
    with open(GOLD_PATH) as f:
        return [json.loads(l) for l in f if l.strip() and not l.startswith('#')]


GOLD = load_gold()


@pytest.mark.parametrize("entry", GOLD, ids=[f"{e['id']}-{e['text']}" for e in GOLD])
def test_uhps_full_preservation(entry):
    """Each IPA → UHPS-full should preserve phonemes per spec."""
    ipa = entry['ipa']
    expected = entry['uhps_full_expected']
    out = transcribe_universal(ipa, 'ipa', uhps='full',
                                tone_style='middledot', safe_fonts=False)
    assert out == expected, (
        f"\n  Test: {entry['test']}\n"
        f"  IPA:      {ipa!r}\n"
        f"  Expected: {expected!r}\n"
        f"  Got:      {out!r}"
    )


def test_total_count():
    assert len(GOLD) >= 30, f"External gold too small: {len(GOLD)}"


def test_phoneme_preservation_summary():
    """Summary: % of entries where output exactly matches expected."""
    total = len(GOLD)
    correct = 0
    for e in GOLD:
        out = transcribe_universal(e['ipa'], 'ipa', uhps='full',
                                    tone_style='middledot', safe_fonts=False)
        if out == e['uhps_full_expected']:
            correct += 1
    accuracy = correct / total * 100
    # 60% 미만이면 spec 회귀 (실제 천장은 90%+)
    assert accuracy >= 60, f'UHPS-full external accuracy regressed: {accuracy:.1f}%'
