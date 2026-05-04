"""Hunmin CLI — `hunmin "Mozart" --lang de` or `cat words.txt | hunmin --lang en`."""
import argparse
import sys
from . import transcribe, Hunmin, __version__


def main():
    ap = argparse.ArgumentParser(
        prog='hunmin',
        description='Universal phonetic Hangul transcription. Converts any language to readable Korean Hangul.',
        epilog="""Examples:
  hunmin "Mozart" --lang de              # 모차르트
  hunmin "中国" --lang zh                 # 중국 (with override)
  hunmin "familia" --lang es --mode uhps_full   # 옛한글
  cat words.txt | hunmin --lang en       # stdin pipe
  echo "Bonjour" | hunmin --lang fr -v   # views
  hunmin --demo
  hunmin --list-langs

Supported languages:
  Latin: en/es/it/de/fr/pt/nl/pl/tr/id/hu/sk/cs/ro/hr/bs/vi (17)
  Cyrillic: ru/sr/mk
  Arabic-script: fa
  CJK (pykakasi/pypinyin/hanja 필요): ja/zh/ko
  IPA: 'ipa' lang으로 IPA 직접 입력
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('input', nargs='?', help='Input text (또는 --text 또는 stdin)')
    ap.add_argument('--text', help='Input text (대안: positional argument 또는 stdin)')
    ap.add_argument('--lang', '-l', help='Language code')
    ap.add_argument('--mode', '-m', choices=['hunmin_nikl','hunmin_phonetic','uhps_core','uhps_jamo','uhps_full'],
                    help='Output mode (level 대신 mode 사용 권장)')
    ap.add_argument('--level', type=int, default=1, choices=[1, 2, 3, 4, 5],
                    help='1: kid-friendly, 2: natural, 3: UHPS-core, 4: jamo seq, 5: UHPS-full')
    ap.add_argument('--tokens', action='store_true',
                    help='Output abstract token sequence instead of Hangul (ML use). '
                         'Implies routing through IPA pipeline. See UHPS_SPEC §6.')
    ap.add_argument('--views', action='store_true',
                    help='Output multi-view dict (text/ipa/uhps_core/uhps_full/hunmin/meaning). '
                         'See UHPS_SPEC §1.0.')
    ap.add_argument('--meaning', help='Optional meaning anchor (used with --views)')
    ap.add_argument('--auto', action='store_true',
                    help='Auto-routing transcribe (mixed-script, digits, symbols → 100% UHPS).')
    ap.add_argument('--digits', choices=['sino', 'native', 'read', 'keep'],
                    default='sino', help='--auto: 5→오/다섯/파이브/5')
    ap.add_argument('--symbols', choices=['kor', 'drop', 'keep'],
                    default='kor', help='--auto: $→달러/(omit)/$')
    ap.add_argument('--strict', action='store_true',
                    help='--auto: fail on unencoded char (vs pass-through)')
    ap.add_argument('--format', choices=['text', 'json', 'jsonl'], default='text',
                    help='Output format (default text). json/jsonl works with --tokens or --views.')
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

    # v3.42: positional input || --text || stdin
    text = args.input or args.text
    if text is None and not sys.stdin.isatty():
        # stdin pipe 입력
        text = sys.stdin.read().rstrip('\n')
    if text is not None:
        args.text = text

    # --auto는 --lang 없어도 OK (primary_lang default='en')
    if not args.text or (not args.lang and not args.auto):
        ap.print_help()
        return

    # mode가 지정되었으면 mode 우선, 아니면 level 사용

    # v3.42: --mode이 있으면 mode 사용, 없으면 level 사용
    transcribe_kwargs = {'mode': args.mode} if args.mode else {'level': args.level}

    if args.tokens:
        toks = transcribe(args.text, args.lang, level=args.level, return_tokens=True)
        if args.format == 'json':
            import json
            print(json.dumps([list(t) for t in toks], ensure_ascii=False))
        elif args.format == 'jsonl':
            import json
            print(json.dumps({
                'text': args.text, 'lang': args.lang, 'level': args.level,
                'tokens': [list(t) for t in toks],
            }, ensure_ascii=False))
        else:
            for t in toks:
                print('\t'.join(str(x) for x in t))
        return

    if args.auto:
        from . import transcribe_auto
        out = transcribe_auto(args.text, primary_lang=args.lang or 'en',
                                digits=args.digits, symbols=args.symbols,
                                strict=args.strict)
        print(out)
        return

    if args.views:
        from . import views as get_views
        v = get_views(args.text, args.lang, meaning=args.meaning)
        if args.format in ('json', 'jsonl'):
            import json
            print(json.dumps(v, ensure_ascii=False))
        else:
            for k, val in v.items():
                if val is not None:
                    print(f'{k:12s} {val}')
        return

    # 다중 라인 입력은 라인별 변환
    lines = args.text.split('\n')
    for line in lines:
        if line.strip():
            print(transcribe(line, args.lang, **transcribe_kwargs))
        else:
            print()


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
