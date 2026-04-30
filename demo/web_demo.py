"""Hunmin web demo via Gradio.

Install:  pip install hunmin[demo]
Run:      python -m demo.web_demo

Or directly: python web_demo.py
"""
import gradio as gr
from hunmin import Hunmin

h = Hunmin()

LANG_LABELS = {
    'en': 'English',
    'es': 'Spanish (Español)',
    'it': 'Italian (Italiano)',
    'de': 'German (Deutsch)',
    'ru': 'Russian (Русский)',
    'fr': 'French (Français)',
    'pt': 'Portuguese (Português)',
    'nl': 'Dutch (Nederlands)',
    'pl': 'Polish (Polski)',
    'tr': 'Turkish (Türkçe)',
    'id': 'Indonesian (Bahasa)',
    'ja': 'Japanese (日本語)',
    'zh': 'Chinese (中文)',
    'ko': 'Korean (한국어)',
}
LANG_CHOICES = [(label, code) for code, label in LANG_LABELS.items()]

LEVEL_DESCRIPTIONS = {
    1: '아이용 — 외래어 표기법 (Children-friendly Hangul)',
    2: '자연 발음 — 연음 (Natural connected speech)',
    3: '옛한글 정밀 — ㆄ/ㅸ/ㅿ 포함 (Precise with Old Hangul)',
    4: 'UHPS jamo — 자모 시퀀스 (For ML / research)',
}

EXAMPLES = [
    # English — full pipeline showcase
    ['student', 'en', 1],
    ['hello', 'en', 1],
    ['firebase', 'en', 1],
    ['LSTM', 'en', 1],
    ['anthropic', 'en', 1],
    ['father', 'en', 3],
    ['vine', 'en', 3],
    ['student', 'en', 4],
    # Other languages
    ['familia', 'es', 1],
    ['paella', 'es', 1],
    ['Schule', 'de', 1],
    ['Mozart', 'de', 1],
    ['bonjour', 'fr', 1],
    ['Versailles', 'fr', 1],
    ['Москва', 'ru', 1],
    ['Толстой', 'ru', 1],
    ['ciao', 'it', 1],
    ['pizza', 'it', 1],
    ['merhaba', 'tr', 1],
    ['Amsterdam', 'nl', 1],
    ['Warszawa', 'pl', 1],
    ['obrigado', 'pt', 1],
    ['selamat', 'id', 1],
    # CJK
    ['東京', 'ja', 1],
    ['こんにちは', 'ja', 1],
    ['中国', 'zh', 1],
    ['北京', 'zh', 4],
    ['대한민국', 'ko', 4],
]


def transcribe_all_levels(text, lang_label):
    """Show all 4 levels at once."""
    lang = LANG_LABELS_INV.get(lang_label, lang_label)
    if not text.strip():
        return '', '', '', ''
    try:
        l1 = h.transcribe(text, lang, level=1)
        l2 = h.transcribe(text, lang, level=2)
        l3 = h.transcribe(text, lang, level=3)
        l4 = h.transcribe(text, lang, level=4)
        return l1, l2, l3, l4
    except Exception as e:
        return f'Error: {e}', '', '', ''


LANG_LABELS_INV = {label: code for code, label in LANG_LABELS.items()}


with gr.Blocks(title='Hunmin — Phonetic Hangul Transcription', theme=gr.themes.Soft()) as app:
    gr.Markdown("""
# 🎼 Hunmin
### Universal phonetic Hangul transcription

> Convert any language into a readable phonetic Hangul score.
> 외국어를 한글 발음 악보로 — 아이도 읽으면 그 언어 소리가 납니다.
""")

    with gr.Row():
        with gr.Column(scale=2):
            text_in = gr.Textbox(label='Text', placeholder='student / 中国 / familia / ...', lines=2)
        with gr.Column(scale=1):
            lang_in = gr.Dropdown(
                choices=[label for code, label in LANG_LABELS.items()],
                value='English',
                label='Language',
            )

    btn = gr.Button('Transcribe', variant='primary')

    with gr.Row():
        l1_out = gr.Textbox(label='Level 1 — 아이용 (Hangul)', interactive=False)
        l2_out = gr.Textbox(label='Level 2 — 자연 발음', interactive=False)
    with gr.Row():
        l3_out = gr.Textbox(label='Level 3 — 옛한글 정밀 (ㆄ/ㅸ/ㅿ)', interactive=False)
        l4_out = gr.Textbox(label='Level 4 — UHPS jamo seq', interactive=False)

    btn.click(transcribe_all_levels, [text_in, lang_in], [l1_out, l2_out, l3_out, l4_out])
    text_in.submit(transcribe_all_levels, [text_in, lang_in], [l1_out, l2_out, l3_out, l4_out])

    gr.Examples(
        examples=[[ex[0], LANG_LABELS[ex[1]]] for ex in EXAMPLES],
        inputs=[text_in, lang_in],
    )

    gr.Markdown("""
---
### About the levels

| Level | Description |
|---|---|
| **1** | Children-friendly Hangul. Read it as a Korean. |
| **2** | Natural pronunciation (linked syllables). |
| **3** | Precise — uses Old Hangul: **ㆄ** for /f/, **ㅸ** for /v/, **ㅿ** for /z/. |
| **4** | UHPS jamo sequence — for ML and audio research. |

### Supported

**Latin/Cyrillic (rule-based):** en, es, it, de, ru, fr, pt, nl, pl, tr, id
**Logographic (dictionary):** ja, zh, ko

---
[GitHub](https://github.com/meshpop/hunmin) · [PyPI](https://pypi.org/project/hunmin/) · MIT License
""")


if __name__ == '__main__':
    app.launch(server_name='0.0.0.0', share=False)
