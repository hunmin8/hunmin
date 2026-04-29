"""Hunmin CLI — `hunmin --text "student" --lang en --level 1`."""
import argparse
from . import transcribe, Hunmin, __version__


def main():
    ap = argparse.ArgumentParser(
        prog='hunmin',
        description='Universal phonetic Hangul transcription. Converts any language to readable Korean Hangul.',
        epilog="""Examples:
  hunmin --text "student" --lang en
  hunmin --text "中国" --lang zh --level 4
  hunmin --text "familia" --lang es --level 3
  hunmin --demo

Supported languages:
  Latin/Cyrillic: en, es, it, de, ru, fr, pt, nl, pl, tr, id
  CJK (needs pykakasi/pypinyin/hanja): ja, zh, ko
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--text', help='Input text')
    ap.add_argument('--lang', help='Language code')
    ap.add_argument('--level', type=int, default=1, choices=[1, 2, 3, 4],
                    help='1: kid-friendly, 2: natural, 3: precise (old Hangul), 4: UHPS jamo')
    ap.add_argument('--demo', action='store_true', help='Run text demo with 14 languages')
    ap.add_argument('--web', action='store_true', help='Launch Gradio web demo (requires hunmin[demo])')
    ap.add_argument('--list-langs', action='store_true', help='List supported languages')
    ap.add_argument('--version', action='version', version=f'hunmin {__version__}')
    args = ap.parse_args()

    if args.list_langs:
        h = Hunmin()
        print(' '.join(sorted(h.supported())))
        return

    if args.web:
        run_web()
        return

    if args.demo:
        run_demo()
        return

    if not args.text or not args.lang:
        ap.print_help()
        return

    out = transcribe(args.text, args.lang, level=args.level)
    print(out)


def run_demo():
    samples = [
        ('en', 'student'), ('en', 'father'), ('en', 'beautiful'),
        ('es', 'familia'), ('es', 'México'),
        ('it', 'ciao'), ('it', 'pizza'),
        ('de', 'Schule'), ('de', 'Mädchen'),
        ('ru', 'Москва'), ('ru', 'спасибо'),
        ('fr', 'bonjour'), ('fr', 'Paris'),
        ('pt', 'obrigado'),
        ('nl', 'Amsterdam'),
        ('pl', 'Warszawa'),
        ('tr', 'merhaba'),
        ('id', 'selamat'),
        ('ja', 'こんにちは'), ('ja', '東京'),
        ('zh', '中国'), ('zh', '北京'),
        ('ko', '학교'), ('ko', '대한민국'),
    ]
    h = Hunmin()
    print(f'{"lang":<5} {"text":<22} {"L1 (kid)":<14} {"L3 (precise)":<14} {"L4 (jamo)":<22}')
    print('=' * 90)
    for lang, text in samples:
        try:
            l1 = h.transcribe(text, lang, level=1)
            l3 = h.transcribe(text, lang, level=3)
            l4 = h.transcribe(text, lang, level=4)
            print(f'{lang:<5} {text:<22} {l1:<14} {l3:<14} {l4:<22}')
        except Exception as e:
            print(f'{lang:<5} {text:<22} [ERROR: {e}]')


def run_web():
    """Launch Gradio web demo."""
    try:
        import gradio  # noqa: F401
    except ImportError:
        print("Gradio가 설치되지 않았습니다. 설치:")
        print("  pip install hunmin[demo]")
        print("또는:")
        print("  pip install gradio")
        return
    # Inline minimal version (avoid demo/ folder import dependency)
    import gradio as gr
    h = Hunmin()
    LANG_LABELS = {
        'en': 'English', 'es': 'Español', 'it': 'Italiano',
        'de': 'Deutsch', 'ru': 'Русский', 'fr': 'Français',
        'pt': 'Português', 'nl': 'Nederlands', 'pl': 'Polski',
        'tr': 'Türkçe', 'id': 'Bahasa', 'ja': '日本語',
        'zh': '中文', 'ko': '한국어',
    }
    inv = {v: k for k, v in LANG_LABELS.items()}

    def fn(text, label):
        lang = inv.get(label, label)
        if not text.strip():
            return '', '', '', ''
        try:
            return (h.transcribe(text, lang, level=1),
                    h.transcribe(text, lang, level=2),
                    h.transcribe(text, lang, level=3),
                    h.transcribe(text, lang, level=4))
        except Exception as e:
            return f'Error: {e}', '', '', ''

    examples = [
        ['student', 'English'], ['hello', 'English'],
        ['firebase', 'English'], ['LSTM', 'English'],
        ['Москва', 'Русский'], ['Versailles', 'Français'],
        ['pizza', 'Italiano'], ['Mozart', 'Deutsch'],
        ['東京', '日本語'], ['中国', '中文'],
    ]
    with gr.Blocks(title='Hunmin', theme=gr.themes.Soft()) as app:
        gr.Markdown('# 🎼 Hunmin\n### Universal phonetic Hangul transcription')
        with gr.Row():
            text_in = gr.Textbox(label='Text', lines=2, scale=2)
            lang_in = gr.Dropdown(choices=list(LANG_LABELS.values()),
                                  value='English', label='Language', scale=1)
        btn = gr.Button('Transcribe', variant='primary')
        with gr.Row():
            l1 = gr.Textbox(label='Level 1 — 아이용', interactive=False)
            l2 = gr.Textbox(label='Level 2 — 자연 발음', interactive=False)
        with gr.Row():
            l3 = gr.Textbox(label='Level 3 — 옛한글 (ㆄ/ㅸ/ㅿ)', interactive=False)
            l4 = gr.Textbox(label='Level 4 — UHPS jamo', interactive=False)
        btn.click(fn, [text_in, lang_in], [l1, l2, l3, l4])
        text_in.submit(fn, [text_in, lang_in], [l1, l2, l3, l4])
        gr.Examples(examples=examples, inputs=[text_in, lang_in])
    app.launch(server_name='0.0.0.0', share=False)


if __name__ == '__main__':
    main()
