"""Hunmin core — per-language transcribers."""
from .spanish import transcribe_es
from .italian import transcribe_it
from .german import transcribe_de
from .russian import transcribe_ru
from .french import transcribe_fr
from .portuguese import transcribe_pt
from .dutch import transcribe_nl
from .polish import transcribe_pl
from .turkish import transcribe_tr
from .indonesian import transcribe_id
from .english import transcribe_en
from .hungarian import transcribe as transcribe_hu
from .slovak import transcribe as transcribe_sk
from .czech import transcribe as transcribe_cs
from .romanian import transcribe as transcribe_ro
from .cjk import transcribe_cjk, transcribe_ja, transcribe_zh, transcribe_ko, hangul_to_jamo

__all__ = [
    'transcribe_es', 'transcribe_it', 'transcribe_de', 'transcribe_ru',
    'transcribe_fr', 'transcribe_pt', 'transcribe_nl', 'transcribe_pl',
    'transcribe_tr', 'transcribe_id', 'transcribe_en', 'transcribe_hu',
    'transcribe_sk', 'transcribe_cs', 'transcribe_ro',
    'transcribe_ja', 'transcribe_zh', 'transcribe_ko', 'transcribe_cjk',
    'hangul_to_jamo',
]
