# Hunmin 2.2.1 Public Release Check

Date: 2026-04-30

## Summary

`hunmin==2.2.1` is published and usable for the public package goal, with one important packaging/documentation distinction:

- `pip install hunmin` works for the dependency-free core languages plus direct `lang="ipa"` mode.
- CJK examples require `pip install hunmin[cjk]`.
- Universal/epitran mode requires `pip install hunmin[universal]` and works for many mapped languages, but the "100+ languages" claim should remain "optional/experimental universal mode" unless the full mapping is smoke-tested.

## Verified Public Links

- PyPI: https://pypi.org/project/hunmin/2.2.1/
- GitHub: https://github.com/meshpop/hunmin
- Hugging Face Space: https://huggingface.co/spaces/foolsai/hunmin

GitHub `main` checked at:

```text
47e60c54f627ce9b87488c988063fd27f002eb5d refs/heads/main
```

## Clean Install Smoke Tests

Environment:

```bash
python3 -m venv /tmp/hunmin221_check
/tmp/hunmin221_check/bin/python -m pip install hunmin==2.2.1
```

Results:

```text
version 2.2.1
supported_languages() -> 14 codes:
['de', 'en', 'es', 'fr', 'id', 'it', 'ja', 'ko', 'nl', 'pl', 'pt', 'ru', 'tr', 'zh']

student/en -> 스튜던트
hello/en -> 헬로
button/en -> 버튼
father/en level=3 -> ㆄ아더
vine/en level=3 -> ㅸ아인
zoo/en level=3 -> ㅿ우
familia/es level=3 -> ㆄ아밀리아
Москва/ru level=4 -> ㅁㅗㅅㅋㅸㅏ
ɲaɲa/ipa -> ㅥ아ㅥ아
θɪŋk/ipa level=3 -> ㅼ이ㆁ크
```

Default install CJK behavior:

```text
東京/ja -> ImportError: Japanese support requires pykakasi: pip install hunmin[cjk]
中国/zh -> ImportError: Chinese support requires pypinyin: pip install hunmin[cjk]
大韓民國/ko -> 大韓民國
```

This is acceptable only if docs make clear that CJK requires the `cjk` extra.

## CJK Extra Smoke Test

Environment:

```bash
/tmp/hunmin221_check/bin/python -m pip install 'hunmin[cjk]==2.2.1'
```

Results:

```text
東京/ja -> 도쿄
中国/zh -> 중궈
こんにちは/ja -> 곤니치와
大阪/ja -> 오사카
京都府/ja -> 교토부
大韓民國/ko -> 대한민국
中国/zh level=4 -> ㅈㅜㅇㄱㅝ
東京/ja level=4 -> ㄷㅗㅋㅛ
```

Local test suite under the CJK-enabled venv:

```text
103 passed in 0.70s
```

Base environment without `hanja`:

```text
102 passed, 1 failed
failed: 大韓民國/ko expected 대한민국 but got 大韓民國
```

This confirms the failure is an optional dependency issue, not the CJK-enabled package path.

## Universal Extra Smoke Test

Environment:

```bash
python3 -m venv /tmp/hunmin221_universal_check
/tmp/hunmin221_universal_check/bin/python -m pip install 'hunmin[universal]==2.2.1'
```

Results:

```text
cy helo -> 헤로
fr bonjour -> 봉주르
hi नमस्ते -> 넘스테
th สวัสดี -> 사왙디
vi xin chào -> 신 아으
ipa ɲaɲa -> ㅥ아ㅥ아
el Γεια -> ValueError unsupported language 'el'
```

Universal mode is usable, but not all README-listed examples should be treated as verified until a full language-code test is added.

## Public Readiness

Usable:

- Yes, as a public Python package for rule-based transcription.
- Yes, for direct IPA input mode.
- Yes, for CJK if users install `hunmin[cjk]`.
- Yes, for universal mode as optional/experimental.

Not yet ideal:

- README quick-start shows CJK calls near default examples; users may expect `pip install hunmin` to run them.
- `supported_languages()` returns only 14 codes and omits `ipa` and universal-mode codes.
- Universal code comments/docs mention Greek/`ell`, but public `lang="el"` currently fails.
- The "7,000+ languages" phrase should be worded as "any language can be represented if IPA is provided", not automatic orthography-to-Hangul support.
- Level 3/UHPS output uses extended/old Hangul glyphs; rendering depends on font/client.

## Recommended Next Patch

For `2.2.2` or docs-only update:

1. Split README quick start into:
   - default install examples
   - CJK extra examples
   - universal extra examples
   - direct IPA examples
2. Add `ipa` to public capability reporting, or add a separate `supported_modes()`.
3. Export `supported_universal_languages()` at package top level.
4. Add a universal smoke-test script that verifies every `_ISO_TO_EPITRAN` mapping can initialize.
5. Add CI jobs:
   - base install
   - `.[cjk]`
   - `.[universal]`

