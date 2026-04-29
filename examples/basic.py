"""Basic Hunmin examples."""
from hunmin import transcribe, Hunmin, supported_languages

# 1. Simple
print(transcribe("student", "en"))      # 스튜던트
print(transcribe("Paris", "fr"))         # 파리
print(transcribe("中国", "zh"))           # 중구어

# 2. All levels
for level in [1, 2, 3, 4]:
    print(f"Level {level}:", transcribe("father", "en", level=level))

# 3. Class-based (faster for many calls — single instance)
h = Hunmin()
words = [("student", "en"), ("familia", "es"), ("Schule", "de"),
         ("Москва", "ru"), ("中国", "zh"), ("東京", "ja")]
for w, lang in words:
    print(f"  {w:<10} ({lang}) → {h.transcribe(w, lang)}")

# 4. Inspect supported langs
print("\nSupported:", supported_languages())
