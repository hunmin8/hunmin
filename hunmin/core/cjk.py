"""Self-contained CJK transcription (ja/zh/ko).

ja: pykakasi → hiragana → 한글
zh: pypinyin  → pinyin   → 한글 (via pinyin_to_kr.json, ~410 syllables)
ko: hanja library for 한자→한자음, native 한글 그대로
"""
import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent / 'data'

# === Pinyin → 한글 (Mandarin Chinese) ===
with open(_DATA_DIR / 'pinyin_to_kr.json', encoding='utf-8') as f:
    _PINYIN_TO_KR = json.load(f)['syllables']


# === Romaji → 한글 (Japanese, Hepburn) ===
# 요음 (3-char) > 기본 (2-char) > 모음 (1-char). Greedy longest match.
_ROMAJI_TO_KR = {
    # 요음 3-char
    'kya':'캬','kyu':'큐','kyo':'쿄',
    'sha':'샤','shu':'슈','sho':'쇼','she':'셰',
    'cha':'차','chu':'추','cho':'초','che':'체',
    'nya':'냐','nyu':'뉴','nyo':'뇨',
    'hya':'햐','hyu':'휴','hyo':'효',
    'mya':'먀','myu':'뮤','myo':'묘',
    'rya':'랴','ryu':'류','ryo':'료',
    'gya':'갸','gyu':'규','gyo':'교',
    'bya':'뱌','byu':'뷰','byo':'뵤',
    'pya':'퍄','pyu':'퓨','pyo':'표',
    'tsu':'츠',
    'shi':'시','chi':'치','fu':'후',
    'ji':'지',
    # 기본 2-char (consonant + vowel)
    'ka':'카','ki':'키','ku':'쿠','ke':'케','ko':'코',
    'sa':'사','su':'스','se':'세','so':'소',
    'ta':'타','te':'테','to':'토',
    'na':'나','ni':'니','nu':'누','ne':'네','no':'노',
    'ha':'하','hi':'히','he':'헤','ho':'호',
    'ma':'마','mi':'미','mu':'무','me':'메','mo':'모',
    'ya':'야','yu':'유','yo':'요',
    'ra':'라','ri':'리','ru':'루','re':'레','ro':'로',
    'wa':'와','wo':'오',
    'ga':'가','gi':'기','gu':'구','ge':'게','go':'고',
    'za':'자','zu':'즈','ze':'제','zo':'조',
    'da':'다','de':'데','do':'도','di':'디','du':'두',
    'ba':'바','bi':'비','bu':'부','be':'베','bo':'보',
    'pa':'파','pi':'피','pu':'푸','pe':'페','po':'포',
    'va':'바','vi':'비','vu':'부','ve':'베','vo':'보',
    'ja':'자','ju':'주','jo':'조','je':'제',
    # 모음 1-char
    'a':'아','i':'이','u':'우','e':'에','o':'오',
}


# (legacy 매핑, 단순 hira 모드 fallback용)
_KANA_TO_KR = {
    # 기본 50음
    'あ':'아','い':'이','う':'우','え':'에','お':'오',
    'か':'카','き':'키','く':'쿠','け':'케','こ':'코',
    'さ':'사','し':'시','す':'스','せ':'세','そ':'소',
    'た':'타','ち':'치','つ':'츠','て':'테','と':'토',
    'な':'나','に':'니','ぬ':'누','ね':'네','の':'노',
    'は':'하','ひ':'히','ふ':'후','へ':'헤','ほ':'호',
    'ま':'마','み':'미','む':'무','め':'메','も':'모',
    'や':'야','ゆ':'유','よ':'요',
    'ら':'라','り':'리','る':'루','れ':'레','ろ':'로',
    'わ':'와','ゐ':'이','ゑ':'에','を':'오','ん':'ㄴ',
    # 탁음 (가/자/다/바)
    'が':'가','ぎ':'기','ぐ':'구','げ':'게','ご':'고',
    'ざ':'자','じ':'지','ず':'즈','ぜ':'제','ぞ':'조',
    'だ':'다','ぢ':'지','づ':'즈','で':'데','ど':'도',
    'ば':'바','び':'비','ぶ':'부','べ':'베','ぼ':'보',
    # 반탁음 (파)
    'ぱ':'파','ぴ':'피','ぷ':'푸','ぺ':'페','ぽ':'포',
    # 작은 글자 (촉음/요음)
    'っ':'ㅅ',  # 촉음 (sokuon) → 받침 ㅅ
    'ゃ':'ㅑ','ゅ':'ㅠ','ょ':'ㅛ',
    'ぁ':'아','ぃ':'이','ぅ':'우','ぇ':'에','ぉ':'오',
    # 가타카나 (대응)
    'ア':'아','イ':'이','ウ':'우','エ':'에','オ':'오',
    'カ':'카','キ':'키','ク':'쿠','ケ':'케','コ':'코',
    'サ':'사','シ':'시','ス':'스','セ':'세','ソ':'소',
    'タ':'타','チ':'치','ツ':'츠','テ':'테','ト':'토',
    'ナ':'나','ニ':'니','ヌ':'누','ネ':'네','ノ':'노',
    'ハ':'하','ヒ':'히','フ':'후','ヘ':'헤','ホ':'호',
    'マ':'마','ミ':'미','ム':'무','メ':'메','モ':'모',
    'ヤ':'야','ユ':'유','ヨ':'요',
    'ラ':'라','リ':'리','ル':'루','レ':'레','ロ':'로',
    'ワ':'와','ヰ':'이','ヱ':'에','ヲ':'오','ン':'ㄴ',
    'ガ':'가','ギ':'기','グ':'구','ゲ':'게','ゴ':'고',
    'ザ':'자','ジ':'지','ズ':'즈','ゼ':'제','ゾ':'조',
    'ダ':'다','ヂ':'지','ヅ':'즈','デ':'데','ド':'도',
    'バ':'바','ビ':'비','ブ':'부','ベ':'베','ボ':'보',
    'パ':'파','ピ':'피','プ':'푸','ペ':'페','ポ':'포',
    'ッ':'ㅅ',
    'ャ':'ㅑ','ュ':'ㅠ','ョ':'ㅛ',
    'ァ':'아','ィ':'이','ゥ':'우','ェ':'에','ォ':'오',
    'ヴ':'브',
    'ー':'',  # 장음 (drop)
}


# === Hangul jamo decomposition (Level 4 jamo mode) ===
HANGUL_BASE = 0xAC00
INITIALS = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
            'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
VOWELS_J = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ',
            'ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
FINALS = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ',
          'ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
          'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


def hangul_to_jamo(text):
    """한글 syllable → UHPS jamo seq.

    초성 ㅇ는 모음 단독 음절 placeholder → skip.
    """
    out = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            base = code - HANGUL_BASE
            cho = INITIALS[base // 588]
            jung = VOWELS_J[(base % 588) // 28]
            jong = FINALS[base % 28]
            if cho == 'ㅇ':
                out.append(jung)
            else:
                out.append(cho)
                out.append(jung)
            if jong:
                out.append(jong)
        else:
            out.append(ch)
    return ''.join(out)


# === Public API ===

def transcribe_zh(text, mode='hangul', precise=True):
    """Mandarin → 한글 (via pypinyin)."""
    try:
        from pypinyin import lazy_pinyin
    except ImportError:
        raise ImportError("Chinese support requires pypinyin: pip install hunmin[cjk]")

    syllables = lazy_pinyin(text)
    out = []
    for s in syllables:
        clean = ''.join(c for c in s.lower() if not c.isdigit())
        if clean in _PINYIN_TO_KR:
            out.append(_PINYIN_TO_KR[clean])
        else:
            out.append(s)

    hangul = ''.join(out)
    if mode == 'hangul':
        return hangul
    elif mode == 'jamo':
        return hangul_to_jamo(hangul)
    elif mode == 'spaced':
        return ' '.join(hangul_to_jamo(hangul))
    else:
        raise ValueError(f"Unknown mode: {mode}")


def _romaji_to_hangul(s):
    """Hepburn romaji → 한글 (요음/촉음/n받침 처리)."""
    s = s.lower()
    out = []
    i = 0
    n = len(s)
    while i < n:
        # 촉음 (sokuon): doubled consonant kk/pp/ss/tt → 앞 syllable에 받침 ㅅ
        if i+1 < n and s[i] == s[i+1] and s[i] in 'kpst':
            if out and len(out[-1]) == 1:
                code = ord(out[-1])
                if 0xAC00 <= code <= 0xD7A3:
                    base = code - HANGUL_BASE
                    cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
                    if jong_idx == 0:
                        # ㅅ받침 (idx 19)
                        out[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + 19)
            i += 1  # skip first; next will be processed normally
            continue

        # n 단독 (n + 자음 또는 n + end 또는 nn) → ㄴ받침 + 다음
        if s[i] == 'n':
            nxt = s[i+1] if i+1 < n else ''
            if nxt not in 'aeiouy' or nxt == '':
                # ㄴ받침 to last
                if out and len(out[-1]) == 1:
                    code = ord(out[-1])
                    if 0xAC00 <= code <= 0xD7A3:
                        base = code - HANGUL_BASE
                        cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
                        if jong_idx == 0:
                            out[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + 4)  # ㄴ idx 4
                            i += 1
                            continue
                out.append('ㄴ')
                i += 1
                continue

        # Greedy match (3 → 2 → 1)
        matched = False
        for ln in [3, 2, 1]:
            chunk = s[i:i+ln]
            if chunk in _ROMAJI_TO_KR:
                out.append(_ROMAJI_TO_KR[chunk])
                i += ln
                matched = True
                break
        if not matched:
            out.append(s[i])
            i += 1
    return ''.join(out)


def _drop_japanese_long_vowel(rom):
    """NIKL 일본어 표기법: 장음 표기 안 함.
    'ou'→'o', 'oo'→'o', 'uu'→'u', 'aa'→'a', 'ii'→'i'.
    'ei'는 그대로 (NIKL은 ei 유지).
    """
    rom = rom.replace('ou', 'o')
    rom = rom.replace('oo', 'o')
    rom = rom.replace('uu', 'u')
    rom = rom.replace('aa', 'a')
    rom = rom.replace('ii', 'i')
    return rom


# NIKL 일본어 표기법: 어두 k/t/p/ch → 연음 g/d/b/j (어중은 그대로 ㅋ/ㅌ/ㅍ/ㅊ)
_JA_SOFT_PREFIX = [
    # 3-char (요음)
    ('kya', 'gya'), ('kyu', 'gyu'), ('kyo', 'gyo'),
    ('pya', 'bya'), ('pyu', 'byu'), ('pyo', 'byo'),
    ('cha', 'ja'),  ('chu', 'ju'),  ('cho', 'jo'),  ('che', 'je'), ('chi', 'ji'),
    # 2-char (k/t/p + 모음)
    ('ka', 'ga'),   ('ki', 'gi'),   ('ku', 'gu'),   ('ke', 'ge'), ('ko', 'go'),
    ('ta', 'da'),   ('te', 'de'),   ('to', 'do'),
    ('pa', 'ba'),   ('pi', 'bi'),   ('pu', 'bu'),   ('pe', 'be'), ('po', 'bo'),
]


def _ja_soft_initial(rom):
    """어두 k/t/p/ch 연음화."""
    for src, dst in _JA_SOFT_PREFIX:
        if rom.startswith(src):
            return dst + rom[len(src):]
    return rom


# 자주 쓰이는 일본어 표현 (조사 처리 등)
_JA_PHRASE_OVERRIDES = {
    'こんにちは': '곤니치와',
    'こんばんは': '곤방와',
    'おはよう': '오하요',
    'さようなら': '사요나라',
    'ありがとう': '아리가토',
    'すみません': '스미마센',
    'お疲れ様': '오쓰카레사마',
    'お疲れさま': '오쓰카레사마',
}


def transcribe_ja(text, mode='hangul', precise=True):
    """Japanese → 한글 (NIKL 외래어 표기법, via pykakasi → Hepburn romaji → 한글)."""
    try:
        import pykakasi
    except ImportError:
        raise ImportError("Japanese support requires pykakasi: pip install hunmin[cjk]")

    # 1. 자주 쓰이는 표현 직접 매핑
    if mode == 'hangul' and text.strip() in _JA_PHRASE_OVERRIDES:
        return _JA_PHRASE_OVERRIDES[text.strip()]

    kks = pykakasi.kakasi()
    result = kks.convert(text)
    # hepburn으로 단어별 처리
    out_parts = []
    for r in result:
        rom = r.get('hepburn', '').strip()
        if not rom:
            out_parts.append(r.get('orig', ''))
            continue
        # NIKL 룰 적용: 어두 연음화 + 장음 드롭
        rom = _ja_soft_initial(rom)
        rom = _drop_japanese_long_vowel(rom)
        out_parts.append(_romaji_to_hangul(rom))
    hangul = ' '.join(out_parts) if len(out_parts) > 1 else (out_parts[0] if out_parts else '')

    if mode == 'hangul':
        return hangul
    elif mode == 'jamo':
        return hangul_to_jamo(hangul)
    elif mode == 'spaced':
        return ' '.join(hangul_to_jamo(hangul))
    else:
        raise ValueError(f"Unknown mode: {mode}")


def transcribe_ko(text, mode='hangul', precise=True):
    """Korean → 한글. 한자는 한자음으로."""
    try:
        import hanja
        text_ko = hanja.translate(text, 'substitution')
    except ImportError:
        text_ko = text

    if mode == 'hangul':
        return text_ko
    elif mode == 'jamo':
        return hangul_to_jamo(text_ko)
    elif mode == 'spaced':
        return ' '.join(hangul_to_jamo(text_ko))
    else:
        raise ValueError(f"Unknown mode: {mode}")


def transcribe_cjk(text, lang, mode='hangul', precise=True):
    if lang == 'ja': return transcribe_ja(text, mode, precise)
    if lang == 'zh': return transcribe_zh(text, mode, precise)
    if lang == 'ko': return transcribe_ko(text, mode, precise)
    raise ValueError(f"Unknown CJK lang: {lang}")


if __name__ == '__main__':
    cases = [('zh', '中国'), ('zh', '北京'), ('zh', '你好'),
             ('ja', 'こんにちは'), ('ja', '東京'), ('ja', 'コンピューター'),
             ('ko', '학교'), ('ko', '한국'), ('ko', '大韓民國')]
    for lang, text in cases:
        try:
            h = transcribe_cjk(text, lang, mode='hangul')
            j = transcribe_cjk(text, lang, mode='jamo')
            print(f'{lang} {text:<14} h={h:<10} j={j}')
        except Exception as e:
            print(f'{lang} {text:<14} ERROR: {e}')
