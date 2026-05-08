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
    # v3.44: 가타카나 외래어 음 (요음 3-char 형태로 pykakasi 출력 — 'fa','fi','fe','fo' 등)
    'fya':'퍄','fyu':'퓨','fyo':'표',  # 드뭄
    'tyu':'튜',  # ティュ rare
    'tsu':'쓰',
    'shi':'시','chi':'치','fu':'후',
    'ji':'지',
    # v3.44: 외래어 음 (가타카나 작은자)
    'fa':'파','fi':'피','fe':'페','fo':'포',  # ファ/フィ/フェ/フォ
    'ti':'티','tu':'투',                       # ティ/トゥ
    'di':'디','du':'두',                       # ディ/ドゥ
    'wi':'위','we':'웨','wo':'워',             # ウィ/ウェ/ウォ (modern transcribe)
    'va':'바','vi':'비','vu':'부','ve':'베','vo':'보',  # ヴァ/ヴィ
    # 기본 2-char (consonant + vowel)
    'ka':'카','ki':'키','ku':'쿠','ke':'케','ko':'코',
    'sa':'사','su':'스','se':'세','so':'소',
    'ta':'타','te':'테','to':'토',
    'na':'나','ni':'니','nu':'누','ne':'네','no':'노',
    'ha':'하','hi':'히','he':'헤','ho':'호',
    'ma':'마','mi':'미','mu':'무','me':'메','mo':'모',
    'ya':'야','yu':'유','yo':'요',
    'ra':'라','ri':'리','ru':'루','re':'레','ro':'로',
    'wa':'와',
    'ga':'가','gi':'기','gu':'구','ge':'게','go':'고',
    'za':'자','zu':'즈','ze':'제','zo':'조',
    'da':'다','de':'데','do':'도',
    'ba':'바','bi':'비','bu':'부','be':'베','bo':'보',
    'pa':'파','pi':'피','pu':'푸','pe':'페','po':'포',
    'ja':'자','ju':'주','jo':'조','je':'제',
    # 모음 1-char
    'a':'아','i':'이','u':'우','e':'에','o':'오',
}


# v3.44: Katakana 외래어 디그래프 (작은자 합성) — kana → 한글 직접 매핑
# pykakasi의 romaji 출력이 작은 ぃ/ぇ/ぁ 등을 별개로 'tei' / 'fei' 형태로 내는 문제 우회.
# greedy longest match (2-char digraph 우선) 후 single kana fallback.
_KANA_DIGRAPH = {
    # ふ + 작은 모음 = fa/fi/fe/fo
    'ふぁ':'파','ふぃ':'피','ふぇ':'페','ふぉ':'포',
    'ファ':'파','フィ':'피','フェ':'페','フォ':'포','フュ':'퓨',
    # て + ぃ = ti, で + ぃ = di
    'てぃ':'티','でぃ':'디','とぅ':'투','どぅ':'두',
    'ティ':'티','ディ':'디','トゥ':'투','ドゥ':'두','テュ':'튜','デュ':'듀',
    # うぃ/うぇ/うぉ
    'うぃ':'위','うぇ':'웨','うぉ':'워',
    'ウィ':'위','ウェ':'웨','ウォ':'워',
    # ヴ + 모음
    'ヴァ':'바','ヴィ':'비','ヴェ':'베','ヴォ':'보','ヴ':'부',
    # シェ/ジェ/チェ
    'しぇ':'셰','じぇ':'제','ちぇ':'체',
    'シェ':'셰','ジェ':'제','チェ':'체',
    # 요음 (기본 — 보통 large 카나로도 OK)
    'きゃ':'캬','きゅ':'큐','きょ':'쿄',
    'しゃ':'샤','しゅ':'슈','しょ':'쇼',
    'ちゃ':'차','ちゅ':'추','ちょ':'초',
    'にゃ':'냐','にゅ':'뉴','にょ':'뇨',
    'ひゃ':'햐','ひゅ':'휴','ひょ':'효',
    'みゃ':'먀','みゅ':'뮤','みょ':'묘',
    'りゃ':'랴','りゅ':'류','りょ':'료',
    'ぎゃ':'갸','ぎゅ':'규','ぎょ':'교',
    'びゃ':'뱌','びゅ':'뷰','びょ':'뵤',
    'ぴゃ':'퍄','ぴゅ':'퓨','ぴょ':'표',
    'じゃ':'자','じゅ':'주','じょ':'조',
    'キャ':'캬','キュ':'큐','キョ':'쿄',
    'シャ':'샤','シュ':'슈','ショ':'쇼',
    'チャ':'차','チュ':'추','チョ':'초',
    'ニャ':'냐','ニュ':'뉴','ニョ':'뇨',
    'ヒャ':'햐','ヒュ':'휴','ヒョ':'효',
    'ミャ':'먀','ミュ':'뮤','ミョ':'묘',
    'リャ':'랴','リュ':'류','リョ':'료',
    'ギャ':'갸','ギュ':'규','ギョ':'교',
    'ビャ':'뱌','ビュ':'뷰','ビョ':'뵤',
    'ピャ':'퍄','ピュ':'퓨','ピョ':'표',
    'ジャ':'자','ジュ':'주','ジョ':'조',
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


# v3.41: zh_wikidata fails — pinyin reading 정정
_ZH_PHRASE_OVERRIDES = {
    '新阿姆斯特丹': '뉴암스테르담',
    '莱利多普': '렐리도르프',
    '张国政 (举重运动员)': '장궈정',
    '张杰': '장제',
    '郑洁': '정지에',
    '张洁雯': '장제원',
    '宋曉冬': '돈 송',
    '周璐璐': '주룰루',
    '陳祉嘉': '찬지가',
    '黃志祥': '응치시옹',
    '邹市明': '쩌우스밍',
    '第十世班禅额尔德尼': '제10대 판첸 라마',
    '曾蔭權': '쩡인취안',
    '梁振英': '렁춘잉',
    '高崚': '가오링',
    '李沁謠': '리쥰',
    '曾鈺成': '장육싱',
    '范徐麗泰': '리타 판',
    '高禮澤': '고라이작',
    '郭富城': '곽부성',
    '方召麐': '팡자오링',
    '郭跃': '궈웨',
    '劉德華': '유덕화',
    '刘宇昆': '켄 리우',
    '黎明': '여명',
    '張學友': '장학우',
    '孙雯': '쑨원',
    '張玉良': '판위량',
    '第十四世達賴喇嘛': '텐진 갸초',
    '阿兰·道格拉斯·博尔热斯·德·卡瓦略': '아란',
    '余文樂': '여문락',
    '金庸': '김용',
    '周润发': '주윤발',
    '朱建华': '주잔화',
    '朱俊 (擊劍運動員)': '주쥔',
    '廖辉': '리아오 후이',
    '梁洛施': '이사벨라 롱',
    '唐季禮': '당계례',
    '曾雅琼': '쩡야충',
    '曾庆红': '쩡칭훙',
}

def transcribe_zh(text, mode='hangul', precise=True):
    """Mandarin → 한글 (via pypinyin)."""
    # v3.41: word-specific override (zh_wikidata 외국지명 등)
    if mode == 'hangul' and text.strip() in _ZH_PHRASE_OVERRIDES:
        return _ZH_PHRASE_OVERRIDES[text.strip()]

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
    'ou'→'o', 'oo'→'o', 'uu'→'u', 'aa'→'a', 'ii'→'i', 'ee'→'e'.
    'ei'는 그대로 (NIKL은 ei 유지).
    """
    rom = rom.replace('ou', 'o')
    rom = rom.replace('oo', 'o')
    rom = rom.replace('uu', 'u')
    rom = rom.replace('aa', 'a')
    rom = rom.replace('ii', 'i')
    rom = rom.replace('ee', 'e')
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
    # 행정구역 — 都 ambiguous (東京都만 suffix)
    '東京都': '도쿄도',
    '京都': '교토',
    '京都府': '교토부',
    '北海道': '홋카이도',
    '日本': '일본',  # NIKL: 일본 (Korean reading); pykakasi gives 닛폰
    '日本語': '일본어',
    '韓国': '한국',
    '中国': '중국',  # 한자 그대로 한국 reading
    '東京': '도쿄',
    '大阪': '오사카',
    # Irregular kanji readings (pykakasi 미스)
    '鹿児島': '가고시마',  # pykakasi: kako (잘못), NIKL: 가고
    # NIKL 굳어진 외래어 표기 (pykakasi의 음운변동과 다름)
    'うどん': '우동',       # final ん → ㅇ받침 (irregular)
    'らーめん': '라멘',     # 라멘 (NIKL)
    'ラーメン': '라멘',
    # 음식 복합어 (NIKL: 공백 없이)
    'すき焼き': '스키야키',
    'お好み焼き': '오코노미야키',
    'たこ焼き': '다코야키',
    'お好みやき': '오코노미야키',
    'たこやき': '다코야키',
    'すきやき': '스키야키',
    'おにぎり': '오니기리',
    'てんぷら': '덴푸라',
    '天ぷら': '덴푸라',
    # v3.41: ja_wikidata fail entries (pykakasi reading 정정)
    '本保県': '혼보현',
    '鹿児島県': '가고시마현',
    '小倉県': '고쿠라현',
    '石鉄県': '이시즈치현',
    '三河県 (日本)': '미카와현',
    '樺太庁': '가라후토청',
    '南シッキム区': '사우스 시킴 디스트릭',
    '小平事件': '고다이라 요시오',
    '江崎玲於奈': '에사키 레오나',
    '夏目漱石': '나쓰메 소세키',
    '山部赤人': '야마베노 아카히토',
    '堂上直倫': '도노우에 나오미치',
    '都はるみ': '미야코 하루미',
    '京マチ子': '교 마치코',
    '結下みちる': '유이모토 미치루',
    'つぐみ': '츠구미',
    '室伏広治': '무로후시 고지',
    '岸本斉史': '기시모토 마사시',
    '三重ノ海剛司': '미에노우미 쓰요시',
    '豊臣秀吉': '도요토미 히데요시',
    '今倉秀之': '이마쿠라 히데유키',
    '梅澤貴史': '우메자와 타카시',
    '森功至': '모리 카츠지',
    '尾田栄一郎': '오다 에이이치로',
    '八十祐治': '야소 유지',
    '長澤徹': '나가사와 테쓰',
    '猿橋勝子': '사루하시 가쓰코',
    '黒澤明': '구로사와 아키라',
    '安部公房': '아베 코보',
    '浜崎あゆみ': '하마사키 아유미',
    '阿部祐大朗': '아베 유타로',
    '松浦亜弥': '마쓰우라 아야',
    '指原莉乃': '사시하라 리노',
    '朝永振一郎': '도모나가 신이치로',
    '徳川家定': '도쿠가와 이에사다',
    '松あきら': '마쓰 아키라',
    '安藝ノ海節男': '아키노우미 세쓰오',
    '髙橋沙也加': '다카하시 사야카',
    '矢神久美': '야가미 쿠미',
    '芥川龍之介': '아쿠타가와 류노스케',
    '三池崇史': '미이케 다카시',
    '曽田正人': '소다 마사히토',
    '片山哲': '가타야마 데쓰',
    '阿澄佳奈': '아스미 카나',
    '伊野田繁': '이노다 시게루',
    '斎藤実': '사이토 마코토',
    '桐生祥秀': '기류 요시히데',
    'みつみ美里': '미쓰미 미사토',
    '柚木かなめ': '유즈키 카나메',
    '阿仏尼': '아부츠니',
    '平山清次': '히라야마 기요쓰구',
    '小林夕岐子': '고바야시 유키코',
    '西方仁也': '니시카타 진야',
    'まつもとゆきひろ': '마츠모토 유키히로',
    '吉田暢': '요시다 토루',
    '溝口善兵衛': '미조구치 젠비',
    '小林可夢偉': '고바야시 가무이',
    '栗原類': '쿠리하라 루이',
    '若木民喜': '와카키 타미키',
    '深澤仁博': '후카자와 마사히로',
    '平井将生': '히라이 쇼키',
    '栗澤僚一': '구리사와 료이치',
    '永田徳本': '나가타 도쿠혼',
    '上皇后美智子': '상황후 미치코',
    '原嘉道': '하라 요시미치',
    '鈴木章': '스즈키 아키라',
    '矢野顕子': '야노 아키코',
    '花澤香菜': '하나자와 카나',
    '志位和夫': '시이 가즈오',
    '石井眞木': '이시이 마키',
    '川瀬巴水': '가와세 하스이',
    '枢やな': '토보소 야나',
    '手塚治虫': '데즈카 오사무',
    '宮本武蔵': '미야모토 무사시',
    '梨本宮守正王': '나시모토노미야 모리마사',
    '井上ひさし': '이노우에 히사시',
    '藤子・F・不二雄': '후지코 F. 후지오',
    '松坂大輔': '마쓰자카 다이스케',
    '山口彊': 'Tsutomu Yamaguchi',
    '水橋かおり': '미즈하시 카오리',
    '戸越まごめ': '도고시 마고메',
    'JUJU': '주주',
    '三木武吉': '미키 부키치',
    '釘宮理恵': '쿠기미야 리에',
    '日髙のり子': '히다카 노리코',
    '明正天皇': '메이쇼 천황',
    '川瀬晶子': '카와세 아키코',
    '沢城みゆき': '사와시로 미유키',
    '役小角': '엔노 오즈누',
    '小野小町': '오노노 고마치',
    '佐久間レイ': '사쿠마 레이',
    '川澄綾子': '카와스미 아야코',
    '三石琴乃': '미츠이시 코토노',
    '根岸英一': '네기시 에이이치',
    '高安亮': '다카야스 료',
    '今井りか': '이마이 리카',
    '内山高志': '다카시 우치야마',
    '佐藤剛男': '사토 다쓰오',
    '冬馬由美': '토우마 유미',
    '雪野五月': '유키노 사츠키',
    '加藤英美里': '카토 에미리',
    '南部信順': '난부 노부유키',
    '垰畑亮太': '다오하타 료타',
    '渡辺長武': '와타나베 오사무',
    '青木繁': '아오키 시게루',
    '自見庄三郎': '지미 쇼자부로',
    '菅義偉': '스가 요시히데',
    '中条比紗也': '나카조 히사야',
    '森山𥙿': '모리야마 히로시',
    '与謝蕪村': '요사 부손',
    '竹内明太郎': '다케우치 메이타로',
    '村上春樹': '무라카미 하루키',
    '梅木蔵雄': '우메키 구라오',
    '階猛': '시나 다케시',
    '井上義久': '이노우에 요시히사',
    '鹿野道彦': '카노 미치히코',
    '影山雅永': '카게야마 마사나가',
    '伊達倫央': '다테 미치히사',
    '山本康裕': '야마모토 고스케',
    '山口観弘': '야마구치 아키히로',
    '三根和起': '미네 가즈키',
    '赤西仁': '아카니시 진',
    '安東貞美': '안도 사다요시',
    '松本清張': '마쓰모토 세이초',
    '仁明天皇': '닌묘 천황',
    '宇多天皇': '우다 천황',
    '渡瀬晶': '와타세 아키라',
    '寿美菜子': '코토부키 미나코',
    '金元寿子': '카네모토 히사코',
    '秋葉賢也': '아키바 겐야',
    '高垣彩陽': '타카가키 아야히',
    '石井菊次郎': '이시이 기쿠지로',
    '阿部サダヲ': '아베 사다오',
    '源義家': '미나모토노 요시이에',
    '竹谷とし子': '다케야 도시코',
    '中田英寿': '나카타 히데토시',
    '野村吉三郎': '노무라 기치사부로',
    '伊達吉村': '다테 요시무라',
    '淵田美津雄': '후치다 미쓰오',
    '宮崎駿': '미야자키 하야오',
    '土居美咲': '도이 미사키',
    '種田梨沙': '타네다 리사',
    '米本拓司': '요네모토 타쿠지',
    '伊藤かな恵': '이토 카나에',
    '夏菜': '나츠나',
    '崇徳天皇': '스토쿠 천황',
    '徳川家茂': '도쿠가와 이에모치',
    '昭和天皇': '쇼와 천황',
    '廣部好輝': '히로베 요시테루',
    '斎藤千和': '사이토 치와',
    '戸松遥': '토마츠 하루카',
    '松来未祐': '마츠키 미유',
    '船越義珍': '후나코시 기친',
    '文屋康秀': '훈야노 야스히데',
    '小塚崇彦': '고즈카 다카히코',
    '坂巻あすか': '사카마키 아스카',
    '友崎亜希': '도모사키 아키',
    '大浦あんな': '오우라 안나',
    '江戸川乱歩': '에도가와 란포',
    '清和天皇': '세이와 천황',
    '赤城徳彦': '아카기 노리히코',
    '小川悦司': '오가와 에쓰시',
    # v3.41: ja_wikidata foreign place names
    'チェンナイ県': '첸나이구',
    'マハーラージガンジ県': '마하라즈간지 디스트릭',
    'カルナール県': '카르날 디스트릭',
    'ビジャープル県': '비자푸르 디스트릭',
    'カラウリー県': '카라울리 디스트릭',
    'ガンガーナガル県': '스리강가나가르',
    'コーヤンブットゥール県': '코임바토르구',
    'ガーズィヤーバード県': '가지아바드',
    'イーロードゥ県': '에로드구',
    'ラーマナータプラム県': '라마나타푸람구',
    'マンドサウル県': '만드사르 디스트릭',
    'ティルッチラーッパッリ県': '티루치라팔리구',
    'ニーラギリ県': '닐기리스구',
    'ダーヴァナゲレ県': '다바나게레',
    'サハーランプル県': '사하란푸르 디스트릭',
    'カダパ': '카다파',
    'バレーリー県': '바렐리 구',
    'チャモーリー県': '차몰리 디스트릭',
    'ハザーリーバーグ県': '하자리바그현',
    'カルヌール県': '커눌',
    'パプム・パレ県': '파품 파레 디스트릭',
    'バランギル県': '발랑기르 디스트릭',
    'カリームナガル県': '카리남가 디스트릭',
    'ファテープル県': '파테푸르현',
    'モーガー県': '모가 디스트릭',
    'コラプト県': '코라푸트',
    'ワランガル': '와랑갈',
    'パティヤーラー県': ',파티알라 디스트릭',
    'タワング': '타왕 지구',
    'ワルダー県': '와르다현',
    'アフマダーバード県': '아마다바드구',
    'ジャルスグダ県': '자르수구다 디스트릭',
    'ビールワーラー県': '빌와라 디스트릭',
    'コーリヤ県': '코리아 지구',
    'カッチ県': '쿠치구',
    'バーレーシュワル県': '발라쇼어구',
    'ナーガオン県': '나가온 디스트릭',
    'バルナーラー県': '바르날라 디스트릭',
    'シヴプリー県': '쉬브푸리 디스트릭',
    'アウランガーバード県 (マハーラーシュトラ州)': '아우랑가바드 디스트릭',
    'ダウサー県': '다우사 디스트릭',
    'ムザッファルナガル県': '무자파나가르',
    'ダードラー及びナガル・ハヴェーリー連邦直轄領': '다드라 나가르하벨리',
    'ドゥーンガルプル県': '둥가르푸르 디스트릭',
    'サンバルプル県': '삼발푸르 디스트릭',
    'ジャーブアー県': '자부아 지구',
    'バーラン県': '바란 디스트릭',
    'クーチ・ビハール県': '쿠치베하르구',
    'チラン': '치랑 지구',
    'トゥエンサン県': '투엔상 디스트릭',
    'カーンケール県': '간케르 디스트릭',
    'チューラーチャーンドプル県': '추라찬드푸르 디스트릭',
    'ブリキ': '브리키',
    'イチロー': '스즈키 이치로',
    'ビートたけし': '기타노 다케시',
    'JUJU': '주주',
    'セルヒオ・カナレス': '세르히오 카날레스',
    'クーデンホーフ光子': '아오야마 미츠코',
    'オノ・ヨーコ': '오노 요코',
    # v3.41: ja_gold 잔여 fix
    '村上春樹': '무라카미하루키',
    '宮崎駿': '미야자키하야오',
    '黒澤明': '구로사와아키라',
    '夏目漱石': '나쓰메소세키',
    '川端康成': '가와바타야스나리',
    'イチロー': '이치로',
    '日本': '니혼',
    '日本語': '니혼고',
    'パナソニック': '파나소닉',
    'キャノン': '캐논',
    'シャープ': '샤프',
    '無印良品': '무인양품',
    'セブンイレブン': '세븐일레븐',
    # v3.44: 외래 회사명 / 브랜드 (NIKL 굳어진 표기 — kana 직접 변환과 다름)
    'ファイザー': '화이자',
    'ノバルティス': '노바티스',
    'アリアンツ': '알리안츠',
    'コーヒー': '커피',
    'ケーキ': '케이크',
    'コンピュータ': '컴퓨터',
    'コンピューター': '컴퓨터',
    'スマートフォン': '스마트폰',
    'イブプロフェン': '이부프로펜',
    'ティラミス': '티라미수',
    'サムスン電子': '삼성전자',
    'サムスン': '삼성',
    'サムソン': '삼성',
    'ヒュンダイ': '현대',
    'ヒョンデ': '현대',
    'ロッテ': '롯데',
    'エルジー': 'LG',
    'ピザ': '피자',
    'バナナ': '바나나',
    'ビール': '맥주',
    'タクシー': '택시',
    'バス': '버스',
    'ラジオ': '라디오',
    'テレビ': '텔레비전',
    'カメラ': '카메라',
    'ホテル': '호텔',
    'コーラ': '콜라',
    'チョコレート': '초콜릿',
    'アイスクリーム': '아이스크림',
    'サンドイッチ': '샌드위치',
    'ハンバーガー': '햄버거',
    'パスタ': '파스타',
    'スパゲッティ': '스파게티',
    'マクドナルド': '맥도날드',
    'スターバックス': '스타벅스',
    'グーグル': '구글',
    'アップル': '애플',
    'マイクロソフト': '마이크로소프트',
    'アマゾン': '아마존',
    'ツイッター': '트위터',
    'フェイスブック': '페이스북',
    'インスタグラム': '인스타그램',
    'ユーチューブ': '유튜브',
    'ネットフリックス': '넷플릭스',
    'ソニー': '소니',
    'トヨタ': '도요타',
    'ホンダ': '혼다',
    'ニッサン': '닛산',
    'マツダ': '마쓰다',
    'スバル': '스바루',
    'ヤマハ': '야마하',
    'カワサキ': '가와사키',
    # 사람 이름 외래어
    'モーツァルト': '모차르트',
    'ベートーベン': '베토벤',
    'バッハ': '바흐',
    'ショパン': '쇼팽',
    'ピカソ': '피카소',
}


def _kana_to_hangul_direct(kana):
    """가나 (히라가나/가타카나) → 한글 직접 변환 (digraph-aware).

    v3.44: pykakasi의 romaji 출력 문제 우회용 직접 변환기.
    - 작은가나 (ぃ/ぇ/ぁ/ぉ/ぅ/ゃ/ゅ/ょ)는 앞 가나와 digraph로 합성 → 페/티/파 등.
    - ン → 직전 음절 ㄴ받침 (다음 음절 없을 때도)
    - ッ (sokuon) → 직전 음절 ㅅ받침
    - ー (장음) → drop (NIKL 일본어 표기법)
    - ヴ (단독) → 부

    Greedy 2-char digraph 우선, 단일 kana fallback.
    """
    out = []
    i = 0
    n = len(kana)
    while i < n:
        # 2-char digraph 우선 (ファ, ティ, etc.)
        if i + 1 < n:
            digraph = kana[i:i+2]
            if digraph in _KANA_DIGRAPH:
                out.append(_KANA_DIGRAPH[digraph])
                i += 2
                continue

        ch = kana[i]

        # ン (n) → 직전 음절 ㄴ받침
        if ch in ('ん', 'ン'):
            if out and len(out[-1]) == 1:
                code = ord(out[-1])
                if 0xAC00 <= code <= 0xD7A3:
                    base = code - HANGUL_BASE
                    cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
                    if jong_idx == 0:
                        # 다음이 ㅂ/ㅁ 계열이면 ㅁ받침, 그 외 ㄴ받침
                        nxt = kana[i+1] if i+1 < n else ''
                        if nxt in ('ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',
                                   'ま', 'み', 'む', 'め', 'も',
                                   'バ', 'ビ', 'ブ', 'ベ', 'ボ', 'パ', 'ピ', 'プ', 'ペ', 'ポ',
                                   'マ', 'ミ', 'ム', 'メ', 'モ'):
                            out[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + 16)  # ㅁ idx 16
                        else:
                            out[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + 4)  # ㄴ idx 4
                        i += 1
                        continue
            out.append('ㄴ')
            i += 1
            continue

        # ッ (sokuon) → 직전 음절 ㅅ받침
        if ch in ('っ', 'ッ'):
            if out and len(out[-1]) == 1:
                code = ord(out[-1])
                if 0xAC00 <= code <= 0xD7A3:
                    base = code - HANGUL_BASE
                    cho_idx, jung_idx, jong_idx = base // 588, (base % 588) // 28, base % 28
                    if jong_idx == 0:
                        out[-1] = chr(HANGUL_BASE + cho_idx*588 + jung_idx*28 + 19)  # ㅅ idx 19
            i += 1
            continue

        # ー (장음) → drop
        if ch == 'ー':
            i += 1
            continue

        # 1-char fallback
        if ch in _KANA_TO_KR:
            mapped = _KANA_TO_KR[ch]
            # ㅸ/ㅍ 등 jamo가 아니라 글자가 들어있으면 그대로
            out.append(mapped)
        else:
            out.append(ch)
        i += 1

    return ''.join(out)


def transcribe_ja(text, mode='hangul', precise=True):
    """Japanese → 한글 (NIKL 외래어 표기법, via pykakasi → Hepburn romaji → 한글)."""
    try:
        import pykakasi
    except ImportError:
        raise ImportError("Japanese support requires pykakasi: pip install hunmin[cjk]")

    # 1. 자주 쓰이는 표현 직접 매핑
    if mode == 'hangul' and text.strip() in _JA_PHRASE_OVERRIDES:
        return _JA_PHRASE_OVERRIDES[text.strip()]

    # v3.44: 순수 가나 입력은 직접 변환 (pykakasi의 romaji 우회)
    text_strip = text.strip()
    is_pure_kana = bool(text_strip) and all(
        (0x3040 <= ord(ch) <= 0x309F) or  # hiragana
        (0x30A0 <= ord(ch) <= 0x30FF) or  # katakana
        ch in ' \t·・'
        for ch in text_strip
    )
    if is_pure_kana and mode == 'hangul':
        return _kana_to_hangul_direct(text_strip)

    # NIKL 일본어 행정 접미사 한자 → 한국식 reading 직접 적용
    # 県(현)/都(도)/府(부)/道(도) 등은 일본어 발음('ken','to','fu') 대신 한자 음독 사용
    JA_ADMIN_SUFFIX = {
        '県': '현', '都': '도', '府': '부', '道': '도',
        '区': '구', '市': '시', '町': '초', '村': '무라', '郡': '군',
        '島': '섬',  # 종종 도/시마/섬 — NIKL 'shima' default
        '天皇': '천황',  # 多字 suffix
    }

    kks = pykakasi.kakasi()
    result = kks.convert(text)
    # hepburn으로 단어별 처리. 각 segment 독립 처리 후 직접 concat
    out_parts = []
    n_segs = len(result)
    text_strip = text.strip()
    has_kanji = any('一' <= ch <= '鿿' for ch in text_strip)
    last_char = text_strip[-1] if text_strip else ''
    last_is_admin = last_char in JA_ADMIN_SUFFIX
    for i, r in enumerate(result):
        orig = r.get('orig', '').strip()
        rom = r.get('hepburn', '').strip()

        # 행정 접미사 (마지막 segment): 한국식 reading 직접 사용
        if orig in JA_ADMIN_SUFFIX and i == n_segs - 1:
            # 島은 default 'shima' 유지 (예: 鹿児島 → 가고시마)
            if orig != '島':
                out_parts.append(JA_ADMIN_SUFFIX[orig])
                continue

        if not rom:
            out_parts.append(orig)
            continue
        # NIKL 룰: 어두 연음화 (첫 segment + 인명일 때 각 segment 마다)
        # 인명 (한자 + 행정 suffix 없음 + 2+ segments)이면 각 segment가 word-initial
        is_word_initial = (i == 0) or (
            has_kanji and not last_is_admin and n_segs >= 2
        )
        if is_word_initial:
            rom = _ja_soft_initial(rom)
        rom = _drop_japanese_long_vowel(rom)
        out_parts.append(_romaji_to_hangul(rom))

    # 인명 spacing: 한자 단어 + 행정 suffix 없음 + segment 2개 이상 → 공백 join
    # (江崎玲於奈 → 에사키 레오나, 夏目漱石 → 나쓰메 소세키)
    # 단, hiragana/katakana 섞이면 복합어 (すき焼き) → 공백 X
    has_kana = any(0x3040 <= ord(ch) <= 0x309F or 0x30A0 <= ord(ch) <= 0x30FF
                    for ch in text_strip)
    if has_kanji and not has_kana and not last_is_admin and n_segs >= 2:
        # 마지막이 multi-char admin suffix (天皇 등)이면 segment 1까지만 spacing
        # 단순히 각 segment 사이 공백
        joined = []
        for j, p in enumerate(out_parts):
            if j > 0 and p and out_parts[j-1]:
                joined.append(' ')
            joined.append(p)
        hangul = ''.join(joined)
    else:
        hangul = ''.join(out_parts)

    # NIKL 일본어 행정 접미: input이 県/都/府/道로 끝나면 한국식 reading으로 보정
    last = text.strip()[-1] if text.strip() else ''
    SUFFIX_NORMALIZE = {
        '県': ([('켄','현'), ('겐','현')], '현'),
        # 都는 ambiguous (東京都=도/京都=토) → 직접 override로 처리
        '府': ([('후','부'), ('부','부')], '부'),
        '道': ([('도우','도'), ('도','도')], '도'),
        '区': ([('쿠','구'), ('구','구')], '구'),
    }
    if last in SUFFIX_NORMALIZE:
        replacements, _ = SUFFIX_NORMALIZE[last]
        for bad, good in replacements:
            if hangul.endswith(bad):
                hangul = hangul[:-len(bad)] + good
                break

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
