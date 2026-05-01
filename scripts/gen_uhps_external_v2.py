#!/usr/bin/env python3
"""Generate expanded UHPS-full external eval (v3.27).

Builds tests/gold/uhps_external_v2.jsonl with diverse IPA→UHPS-full pairs.
Categories: phonemes (f/v/θ/ð/z/ʒ/ʃ/x/ʁ/ɲ/ɔ/ɑ/ŋ), prosody (ː/ˈ/ˌ/tones),
diphthongs, clusters, multilingual examples.

Each entry's `uhps_full_expected` is computed by the current engine and
serves as the regression baseline (locked behavior).
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hunmin.core.universal import transcribe_universal  # noqa: E402

# (text, lang, ipa, test_description) — uhps_full_expected computed below
CASES = [
    # === Old Hangul phonemes (the heart of UHPS-full) ===
    ('fish', 'en', 'fɪʃ', '/f/=ㆄ /ʃ/=ᄾ'),
    ('fan', 'en', 'fæn', '/f/=ㆄ /æ/=ㅐ'),
    ('coffee', 'en', 'ˈkɔːfi', '/f/ between vowels'),
    ('phantom', 'en', 'ˈfæntəm', '/f/ word-init'),
    ('photo', 'en', 'ˈfoʊtoʊ', '/f/=ㆄ initial'),
    ('very', 'en', 'ˈvɛri', '/v/=ㅸ initial'),
    ('valve', 'en', 'vælv', '/v/=ㅸ both ends'),
    ('seven', 'en', 'ˈsɛvən', '/v/ medial'),
    ('victory', 'en', 'ˈvɪktəri', '/v/ initial'),
    ('vodka', 'ru', 'ˈvotkə', '/v/=ㅸ Russian'),
    ('thin', 'en', 'θɪn', '/θ/=ㅼ initial'),
    ('three', 'en', 'θriː', '/θ/+/r/'),
    ('thunder', 'en', 'ˈθʌndər', '/θ/+/ʌ/'),
    ('thought', 'en', 'θɔːt', '/θ/+/ɔː/'),
    ('thaw', 'en', 'θɔː', '/θ/+/ɔː/ short'),
    ('this', 'en', 'ðɪs', '/ð/=ㅽ initial'),
    ('that', 'en', 'ðæt', '/ð/=ㅽ +/æ/'),
    ('mother', 'en', 'ˈmʌðər', '/ð/ medial'),
    ('breathe', 'en', 'briːð', '/ð/ word-final'),
    ('weather', 'en', 'ˈwɛðər', '/ð/ medial schwa'),
    ('zero', 'en', 'ˈziːroʊ', '/z/=ㅿ initial'),
    ('zoo', 'en', 'zuː', '/z/+/uː/'),
    ('lazy', 'en', 'ˈleɪzi', '/z/ medial'),
    ('zone', 'en', 'zoʊn', '/z/+/oʊ/ diphthong'),
    ('zip', 'en', 'zɪp', '/z/+/ɪ/'),
    ('measure', 'en', 'ˈmɛʒər', '/ʒ/=ᄶ medial'),
    ('vision', 'en', 'ˈvɪʒən', '/ʒ/ medial'),
    ('genre', 'en', 'ˈʒɑːnrə', '/ʒ/ initial'),
    ('garage', 'en', 'ɡəˈrɑːʒ', '/ʒ/ final'),
    ('rouge', 'fr', 'ʁuːʒ', 'fr /ʁ//ʒ/'),
    ('shop', 'en', 'ʃɑːp', '/ʃ/=ᄾ initial'),
    ('show', 'en', 'ʃoʊ', '/ʃ/+diphthong'),
    ('fish-2', 'en', 'fɪʃ', '/ʃ/ final'),
    ('cash', 'en', 'kæʃ', '/ʃ/ final + /æ/'),
    ('Berlin', 'de', 'bɛɐˈliːn', 'de schwa-r'),

    # === German /x/ → ㆅ ===
    ('Bach', 'de', 'bax', '/x/=ㆅ word-final → ㅡ-syll'),
    ('Buch', 'de', 'buːx', '/x/ + length'),
    ('ich', 'de', 'ɪç', '/ç/ palatal — currently ㆅ'),
    ('nacht', 'de', 'naxt', '/x/ before stop'),

    # === French /ʁ/ → ᄛ ===
    ('Paris', 'fr', 'paʁi', 'fr /ʁ/=ᄛ'),
    ('rouge-2', 'fr', 'ʁuːʒ', 'fr word-init /ʁ/'),
    ('frère', 'fr', 'fʁɛːʁ', 'fr /f//ʁ//ʁ/'),
    ('arbre', 'fr', 'aʁbʁ', 'fr cluster'),
    ('grand', 'fr', 'ɡʁɑ̃', 'fr /ʁ/ + nasal /ɑ̃/'),

    # === Spanish /ɲ/ → ㅥ (palatal nasal) ===
    ('mañana', 'es', 'maˈɲana', '/ɲ/=ㅥ medial'),
    ('niño', 'es', 'ˈniɲo', '/ɲ/ medial'),
    ('señor', 'es', 'seˈɲor', '/ɲ/=ㅥ before /o/'),
    ('cañón', 'es', 'kaˈɲon', '/ɲ/ stress'),

    # === /ɔ/ → ㆎ open-o ===
    ('caught', 'en', 'kɔːt', '/ɔː/=ㆎ + length'),
    ('hot', 'en', 'hɔt', '/ɔ/=ㆎ short'),
    ('boss', 'en', 'bɔs', '/ɔ/+/s/'),
    ('coffee-2', 'en', 'ˈkɔːfi', '/ɔː/ stress + length'),
    ('saw', 'en', 'sɔː', '/ɔː/ word-final'),

    # === /ɑ/ → ㆍ open-a ===
    ('father-2', 'en', 'ˈfɑːðər', '/ɑː/=ㆍ stressed length'),
    ('palm', 'en', 'pɑːm', '/ɑː/ + /m/'),
    ('arm', 'en', 'ɑːrm', '/ɑːr/ pre-r'),
    ('father-stress', 'en', 'ˈfɑðər', '/ɑ/ no length'),

    # === /ŋ/ → ㆁ받침 ===
    ('sing', 'en', 'sɪŋ', '/ŋ/ final'),
    ('king', 'en', 'kɪŋ', '/ŋ/ final'),
    ('long', 'en', 'lɔːŋ', '/ŋ/ + /ɔː/'),
    ('thank', 'en', 'θæŋk', '/θ//ŋ/'),
    ('ring', 'en', 'rɪŋ', '/ŋ/ final'),

    # === Length /ː/ ===
    ('see', 'en', 'siː', '/iː/ length'),
    ('moon', 'en', 'muːn', '/uː/ + /n/'),
    ('pool', 'en', 'puːl', '/uː/ + /l/'),
    ('road', 'en', 'roʊd', 'diphthong /oʊ/'),
    ('aid', 'en', 'eɪd', 'diphthong /eɪ/'),

    # === Stress markers ===
    ('record-noun', 'en', 'ˈrɛkərd', 'primary stress on 1st'),
    ('record-verb', 'en', 'rɪˈkɔːrd', 'primary stress on 2nd'),
    ('photograph', 'en', 'ˈfoʊtəˌɡræf', 'primary + secondary'),
    ('information', 'en', 'ˌɪnfərˈmeɪʃən', 'sec then prim'),
    ('communication', 'en', 'kəˌmjuːnɪˈkeɪʃən', '/ə/ prim+sec'),

    # === Mandarin tones ===
    ('mā', 'zh', 'ma˥', 'M tone1 high'),
    ('má', 'zh', 'ma˧˥', 'M tone2 rising'),
    ('mǎ', 'zh', 'ma˨˩˦', 'M tone3 dipping'),
    ('mà', 'zh', 'ma˥˩', 'M tone4 falling'),

    # === Vietnamese tones (with tone bars) ===
    ('má-vi', 'vi', 'ma˧˥', 'vi tone sắc'),
    ('mà-vi', 'vi', 'ma˨˩', 'vi tone huyền'),
    ('mạ', 'vi', 'ma˨˩˧', 'vi tone nặng'),

    # === Multilingual diphthongs ===
    ('aikido', 'ja', 'aɪkiˈdoʊ', 'ja /aɪ/ /oʊ/'),
    ('Tokyo', 'ja', 'toːkjoː', 'ja length /oː/'),
    ('Mozart', 'de', 'ˈmoːtsaʁt', 'de /oː/ + /tsa/ + /ʁ/'),
    ('Bonjour', 'fr', 'bɔ̃ʒuʁ', 'fr nasal /ɔ̃/'),
    ('Madrid', 'es', 'maˈðɾið', 'es /ð/=ㅽ + /ɾ/'),
    ('familia', 'es', 'faˈmilja', 'es /f/=ㆄ'),
    ('schöne', 'de', 'ˈʃøːnə', 'de /ø/'),
    ('Hochschule', 'de', 'hoːxˈʃuːlə', 'de /oːx/'),

    # === Russian palatal/special ===
    ('здравствуй', 'ru', 'ˈzdrastvʊj', 'ru /z/+cluster'),
    ('душа', 'ru', 'duˈʃa', 'ru /ʃ/'),

    # === Korean / IPA roundtrip ===
    ('한국', 'ko', 'hanɡuk', 'ko /h/+/n/+/g/'),

    # === Edge: empty/punct (leak 0 verification) ===
    ('a', 'en', 'a', 'single vowel'),
    ('i', 'en', 'i', 'single vowel'),

    # === Long words with multiple features ===
    ('phenomenon', 'en', 'fɪˈnɑːmənɑːn', '/f/+stress+/ɑː/'),
    ('unusual', 'en', 'ʌnˈjuːʒuəl', '/ʒ/ medial'),
    ('thirteen', 'en', 'θɜːˈtiːn', '/θ/+stress'),
    ('measurement', 'en', 'ˈmɛʒərmənt', '/ʒ/+/r/'),
    ('shopping', 'en', 'ˈʃɑːpɪŋ', '/ʃ/+/ɑː/+/ŋ/'),
    ('television', 'en', 'ˈtɛləˌvɪʒən', 'sec stress + /ʒ/'),
    ('beautiful', 'en', 'ˈbjuːtɪfəl', 'glide+length+/f/'),

    # === Spanish features ===
    ('Argentina', 'es', 'aɾxenˈtina', 'es /x/+/n/'),
    ('viernes', 'es', 'ˈbjeɾnes', 'es /j/+/r/'),

    # === French nasals ===
    ('vingt', 'fr', 'vɛ̃', 'fr /ɛ̃/ nasal'),
    ('un', 'fr', 'œ̃', 'fr /œ̃/ nasal'),
    ('blanc', 'fr', 'blɑ̃', 'fr /ɑ̃/'),

    # === Italian features ===
    ('chiesa', 'it', 'ˈkjɛːza', 'it /j/+/ɛː/+/z/'),
    ('zucchero', 'it', 'ˈtsukːero', 'it /ts/'),

    # === Arabic features (epitran might fail, use IPA direct) ===
    ('habibi', 'ar', 'ħaˈbiːbi', 'ar /ħ/'),
    ('Allah', 'ar', 'ʔaɫˈɫaːh', 'ar /ɫ/+/ʔ/'),
]


def main():
    out_path = REPO / 'tests' / 'gold' / 'uhps_external_v2.jsonl'
    entries = []
    next_id = 36  # continue from existing 35
    for text, lang, ipa, test_desc in CASES:
        try:
            uhps_full = transcribe_universal(
                ipa, 'ipa', uhps='full',
                tone_style='middledot', safe_fonts=False,
            )
        except Exception as e:
            uhps_full = f'__ERROR__:{e}'
        entries.append({
            'id': next_id,
            'text': text,
            'lang': lang,
            'ipa': ipa,
            'uhps_full_expected': uhps_full,
            'phonemes': list(ipa),
            'test': test_desc,
        })
        next_id += 1

    with open(out_path, 'w', encoding='utf-8') as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    print(f'Wrote {len(entries)} entries to {out_path}')

    # Show sample
    print('\nSample entries:')
    for e in entries[:5] + entries[-3:]:
        print(f'  {e["text"]:20} ipa={e["ipa"]:25} → {e["uhps_full_expected"]}')


if __name__ == '__main__':
    main()
