"""Basic Hunmin examples."""
from hunmin import transcribe, Hunmin, supported_languages

# 1. Simple
print(transcribe("student", "en"))       # 스튜던트
print(transcribe("hello",   "en"))       # 헬로
print(transcribe("Paris",   "fr"))       # 파리
print(transcribe("中国",     "zh"))       # 중구어

# 2. All levels
for level in [1, 2, 3, 4]:
    print(f"Level {level}:", transcribe("father", "en", level=level))

# 3. English advanced — 합성어 / 약어 / phonics
print(transcribe("typescript", "en"))    # 타이프스크립트  (합성어 분해)
print(transcribe("LSTM",       "en"))    # 엘에스티엠       (약어)
print(transcribe("anthropic",  "en"))    # 앤스라픽         (CMU 미수록 → phonics)
print(transcribe("history",    "en"))    # 히스토리         (ER+'or' spelling-aware)
print(transcribe("rock",       "en"))    # 록             (AA+'o' → ㅗ)

# 4. Class-based (faster for many calls — single instance)
h = Hunmin()
words = [("student", "en"), ("familia", "es"), ("Schule", "de"),
         ("Москва", "ru"), ("中国", "zh"), ("東京", "ja")]
for w, lang in words:
    print(f"  {w:<10} ({lang}) → {h.transcribe(w, lang)}")

# 5. Inspect supported langs
print("\nSupported:", supported_languages())
