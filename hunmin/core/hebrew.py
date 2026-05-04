"""Hunmin Precise — Hebrew (he) Hebrew script → Hangul.

NIKL 외래어 표기법 히브리어:
  - RTL script. 22 자모. 모음은 niqqud (점) — 보통 unmarked.
  - Modern Hebrew pronunciation 기준
  - 매핑:
      א (alef) → silent / 모음 carrier
      ב (bet) → ㅂ / ㅸ
      ג (gimel) → ㄱ
      ד (dalet) → ㄷ
      ה (he) → ㅎ
      ו (vav) → ㅂ / ㅜ (vowel)
      ז (zayin) → ㅈ
      ח (chet) → ㅎ
      ט (tet) → ㅌ
      י (yod) → ㅇ + y / ㅣ (vowel)
      כ (kaf) → ㅋ
      ל (lamed) → ㄹ
      מ (mem) → ㅁ
      נ (nun) → ㄴ
      ס (samekh) → ㅅ
      ע (ayin) → silent
      פ (peh) → ㅍ
      צ (tsadi) → ㅊ
      ק (qof) → ㅋ
      ר (resh) → ㄹ
      ש (shin) → ㅅ (palatal)
      ת (tav) → ㅌ
"""
import re

CONS_MAP = {
    'ב':'ㅂ','ג':'ㄱ','ד':'ㄷ','ה':'ㅎ',
    'ז':'ㅈ','ח':'ㅎ','ט':'ㅌ','כ':'ㅋ','ך':'ㅋ',  # final kaf
    'ל':'ㄹ','מ':'ㅁ','ם':'ㅁ',  # final mem
    'נ':'ㄴ','ן':'ㄴ','ס':'ㅅ',  # final nun, samekh
    'פ':'ㅍ','ף':'ㅍ',  # final peh
    'צ':'ㅊ','ץ':'ㅊ',  # final tsadi
    'ק':'ㅋ','ר':'ㄹ','ש':'ㅅ','ת':'ㅌ',
}


# 자주 쓰는 히브리어 단어 (NIKL 표기 — table-driven)
_HANGUL_OVERRIDES = {
    # 지명
    'ירושלים': '예루살렘',
    'תל אביב': '텔아비브',
    'חיפה': '하이파',
    'אילת': '에일라트',
    'נצרת': '나사렛',
    'בית לחם': '베들레헴',
    'ים המלח': '사해',
    'גליל': '갈릴리',
    # 인사/일상
    'שלום': '샬롬',
    'תודה': '토다',
    'בוקר טוב': '보케르토브',
    'לילה טוב': '라일라토브',
    # 종교/문화
    'תורה': '토라',
    'תלמוד': '탈무드',
    'כיפה': '키파',
    'בר מצוה': '바르미츠바',
    # 인명
    'דוד': '다윗',
    'אברהם': '아브라함',
    'יעקב': '야곱',
    'משה': '모세',
    'שלמה': '솔로몬',
}


def _phonemize(word, precise=False):
    """Hebrew → 한글 (rough). 모음 없음 → 단순 자음 sequence."""
    out = []
    for c in word:
        if c in CONS_MAP:
            out.append(CONS_MAP[c] + '으')  # default schwa
        elif c == 'א':
            pass  # silent or vowel carrier
        elif c == 'ע':
            pass  # silent in modern Hebrew
        elif c == 'ו':
            out.append('우')
        elif c == 'י':
            out.append('이')
        else:
            out.append(c)
    return ''.join(out)


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Hebrew text → Hangul (NIKL convention).

    Note: Hebrew niqqud (모음 부호) 없으면 룰만으론 정확도 낮음.
    Override dict 우선 사용. 미등록 단어는 거친 근사.
    """
    parts = re.split(r'(\s+|[,.!?;:])', text)
    out = []
    for part in parts:
        if not part: continue
        if part.isspace() or re.match(r'[,.!?;:]', part):
            out.append(part); continue
        if mode == 'hangul' and not precise and not phonetic and part in _HANGUL_OVERRIDES:
            out.append(_HANGUL_OVERRIDES[part])
            continue
        # 다중 단어 phrase는 합쳐서 검색
        if mode == 'hangul' and text.strip() in _HANGUL_OVERRIDES:
            return _HANGUL_OVERRIDES[text.strip()]
        out.append(_phonemize(part))
    return ''.join(out)


if __name__ == '__main__':
    samples = [
        ('שלום', '샬롬'),
        ('ירושלים', '예루살렘'),
        ('תורה', '토라'),
        ('דוד', '다윗'),
    ]
    for inp, exp in samples:
        r = transcribe(inp)
        ok = '✓' if r == exp else '✗'
        print(f'{ok} {inp:15} → {r:15} (expected: {exp})')
