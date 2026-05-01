"""Hunmin Precise — Serbian (sr) Cyrillic → Hangul.

전략: Vuk Karadžić의 키릴 알파벳은 Gaj의 크로아티아 라틴 알파벳과 1:1 대응
(Vukov azbuka). Cyrillic을 Latin으로 변환 후 Croatian 룰 재사용.

매핑:
  А-a Б-b В-v Г-g Д-d Ђ-đ Е-e Ж-ž З-z И-i Ј-j К-k Л-l Љ-lj М-m
  Н-n Њ-nj О-o П-p Р-r С-s Т-t Ћ-ć У-u Ф-f Х-h Ц-c Ч-č Џ-dž Ш-š
"""
from .croatian import transcribe as _transcribe_hr


CYR_TO_LAT = {
    'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Ђ':'Đ','Е':'E','Ж':'Ž',
    'З':'Z','И':'I','Ј':'J','К':'K','Л':'L','Љ':'Lj','М':'M','Н':'N',
    'Њ':'Nj','О':'O','П':'P','Р':'R','С':'S','Т':'T','Ћ':'Ć','У':'U',
    'Ф':'F','Х':'H','Ц':'C','Ч':'Č','Џ':'Dž','Ш':'Š',
    'а':'a','б':'b','в':'v','г':'g','д':'d','ђ':'đ','е':'e','ж':'ž',
    'з':'z','и':'i','ј':'j','к':'k','л':'l','љ':'lj','м':'m','н':'n',
    'њ':'nj','о':'o','п':'p','р':'r','с':'s','т':'t','ћ':'ć','у':'u',
    'ф':'f','х':'h','ц':'c','ч':'č','џ':'dž','ш':'š',
}


def transcribe(text, mode='hangul', precise=False, phonetic=False):
    """Serbian Cyrillic → Hangul (via Croatian rules)."""
    # Convert each char
    latin = ''.join(CYR_TO_LAT.get(c, c) for c in text)
    return _transcribe_hr(latin, mode=mode, precise=precise, phonetic=phonetic)
