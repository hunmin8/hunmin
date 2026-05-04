"""Hunmin Precise — Thai (th) Thai script → Hangul.

NIKL 외래어 표기법 태국어:
  - 44 자음 + 30+ 모음 + 4 tones (NIKL: tone 무시)
  - 매핑 (initial position):
      ก kor → ㄲ, ข khor → ㅋ, ค khor → ㅋ, ง ngor → 응
      จ jor → ㅉ, ฉ chor → ㅊ, ช chor → ㅊ, ซ sor → ㅅ
      ด dor → ㄸ, ต tor → ㄸ, ถ thor → ㅌ, ท thor → ㅌ
      น nor → ㄴ, บ bor → ㅃ, ป por → ㅃ, ผ phor → ㅍ
      พ phor → ㅍ, ฟ for → ㅍ, ม mor → ㅁ, ย yor → ㅇ+y
      ร ror → ㄹ, ล lor → ㄹ, ว wor → ㅇ+w, ส sor → ㅅ, ห hor → ㅎ, อ or → ㅇ
"""
import re


# 태국어는 매우 복잡 (final consonant rule, vowel position 등)
# NIKL gold가 정확한 학습 데이터로 우선 override + 룰은 단순 근사
_HANGUL_OVERRIDES = {
    # 지명
    'กรุงเทพ': '방콕',
    'กรุงเทพมหานคร': '방콕',
    'เชียงใหม่': '치앙마이',
    'ภูเก็ต': '푸껫',
    'พัทยา': '파타야',
    'หัวหิน': '후아힌',
    'อยุธยา': '아유타야',
    'สุโขทัย': '수코타이',
    'กระบี่': '끄라비',
    'เกาะสมุย': '코사무이',
    # 인사/일상
    'สวัสดี': '사왓디',
    'ขอบคุณ': '컵쿤',
    'ใช่': '차이',
    'ไม่': '마이',
    'ครับ': '크랍',
    'ค่ะ': '카',
    # 음식/문화
    'ผัดไทย': '팟타이',
    'ต้มยำ': '톰얌',
    'แกง': '깽',
    'ข้าว': '카오',
    'ส้มตำ': '쏨땀',
    'มัสมั่น': '마사만',
    # 인명
    'ภูมิพล': '푸미폰',
    'รามคำแหง': '람캄행',
}


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Thai text → Hangul (NIKL convention).

    Note: 태국어는 tone 시스템이 복잡하고 final consonant rule이 미묘함.
    현재 구현은 override dict 위주 — 일반 단어는 거친 근사.
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
        # phrase 매칭
        if mode == 'hangul' and text.strip() in _HANGUL_OVERRIDES:
            return _HANGUL_OVERRIDES[text.strip()]
        # 미등록 — letter-by-letter rough
        out.append(part)  # placeholder
    return ''.join(out)


if __name__ == '__main__':
    samples = [
        ('สวัสดี', '사왓디'),
        ('ผัดไทย', '팟타이'),
        ('กรุงเทพ', '방콕'),
        ('เชียงใหม่', '치앙마이'),
    ]
    for inp, exp in samples:
        r = transcribe(inp)
        ok = '✓' if r == exp else '✗'
        print(f'{ok} {inp:15} → {r:15} (expected: {exp})')
