"""Korean pronunciation learning quiz generator.

외국어 학습자에게 외국어 단어와 한글 발음을 묻는 quiz 생성.
또는 한국어 학습자에게 한글 단어를 보여주고 영문 표기를 묻는 reverse quiz.

Modes:
    - 'forward': 외국어 → 한글 발음 맞히기
    - 'reverse': 한글 → 영문 발음 맞히기
    - 'multiple_choice': 4지선다

Usage:
    from hunmin.quiz import make_quiz, run_cli_quiz

    questions = make_quiz(['Mozart', 'familia', 'Bonjour'], lang='auto', n=10)
    for q in questions:
        print(q['prompt'], '?')
        # input('답: ')
        # check answer

    # Or interactive CLI:
    run_cli_quiz(lang='en', n=5)
"""
from __future__ import annotations
import random
import re
from typing import Iterable


# 학습용 자주 쓰이는 단어 dataset (lang → words)
_DEFAULT_WORDS = {
    'en': [
        'computer', 'internet', 'coffee', 'restaurant', 'pizza',
        'phone', 'movie', 'music', 'website', 'email',
        'school', 'library', 'park', 'hospital', 'airport',
        'mountain', 'ocean', 'beach', 'forest', 'river',
        'breakfast', 'lunch', 'dinner', 'shopping', 'travel',
    ],
    'es': [
        'familia', 'casa', 'agua', 'amor', 'amigo',
        'escuela', 'libro', 'mesa', 'fiesta', 'gracias',
    ],
    'it': [
        'pizza', 'pasta', 'spaghetti', 'tiramisu', 'gelato',
        'cappuccino', 'espresso', 'risotto', 'lasagna', 'mozzarella',
    ],
    'fr': [
        'bonjour', 'merci', 'café', 'croissant', 'baguette',
        'fromage', 'restaurant', 'amour', 'soleil', 'voyage',
    ],
    'de': [
        'Mozart', 'Schule', 'Bahnhof', 'Volkswagen', 'Kindergarten',
        'Wagner', 'Beethoven', 'Berlin', 'München', 'Hamburg',
    ],
    'ja': [
        '東京', '京都', '大阪', '北海道', '寿司',
        'ラーメン', 'うどん', '富士山', 'こんにちは', 'ありがとう',
    ],
    'zh': [
        '中国', '北京', '上海', '功夫', '太极',
        '春节', '面条', '饺子', '茶', '龙',
    ],
}


def make_quiz(
    words: Iterable[str] | None = None,
    lang: str = 'en',
    n: int = 10,
    mode: str = 'forward',
    multiple_choice: bool = False,
    seed: int | None = None,
) -> list[dict]:
    """Quiz 문제 생성.

    Args:
        words: 단어 list (None이면 default dataset 사용).
        lang: 언어 코드 (auto면 단어별 추정).
        n: 생성할 문제 수.
        mode: 'forward' (외→한) 또는 'reverse' (한→영).
        multiple_choice: True면 4지선다 (오답 3개 자동 생성).
        seed: random seed.

    Returns:
        list of dict — {prompt, answer, lang, mode, choices (선택)}.

    Examples:
        >>> qs = make_quiz(['Mozart', 'pizza'], lang='en', n=2, seed=42)
        >>> len(qs)
        2
        >>> qs[0]['mode']
        'forward'
    """
    from . import transcribe, hangul_to_rr
    rng = random.Random(seed)
    if words is None:
        words = _DEFAULT_WORDS.get(lang, _DEFAULT_WORDS['en'])
    pool = list(words)
    rng.shuffle(pool)
    pool = pool[:n]

    out = []
    for w in pool:
        if mode == 'forward':
            try:
                hangul = transcribe(w, lang)
            except Exception:
                continue
            q = {'prompt': w, 'answer': hangul, 'lang': lang, 'mode': mode}
        elif mode == 'reverse':
            # 외국어 단어를 한글 표기로 → 그 한글로부터 다시 영문 발음 맞히기
            try:
                hangul = transcribe(w, lang)
                roman = hangul_to_rr(hangul)
            except Exception:
                continue
            q = {'prompt': hangul, 'answer': roman, 'lang': lang, 'mode': mode,
                 'hint': f'(원본: {w})'}
        else:
            raise ValueError(f'Unknown mode: {mode!r}')

        if multiple_choice:
            # 다른 단어들로부터 distractor 생성
            distractors = []
            other_pool = [p for p in pool if p != w][:50]
            rng.shuffle(other_pool)
            for d in other_pool:
                try:
                    if mode == 'forward':
                        d_ans = transcribe(d, lang)
                    else:
                        d_ans = hangul_to_rr(transcribe(d, lang))
                    if d_ans != q['answer'] and d_ans not in distractors:
                        distractors.append(d_ans)
                    if len(distractors) >= 3:
                        break
                except Exception:
                    continue
            choices = [q['answer']] + distractors
            rng.shuffle(choices)
            q['choices'] = choices

        out.append(q)
    return out


def run_cli_quiz(lang: str = 'en', n: int = 5, mode: str = 'forward',
                 multiple_choice: bool = True) -> None:
    """터미널 quiz 실행."""
    print(f'\n=== Hunmin Quiz ({lang}, {n} 문제) ===\n')
    questions = make_quiz(lang=lang, n=n, mode=mode, multiple_choice=multiple_choice)
    correct = 0
    for i, q in enumerate(questions, 1):
        print(f"문제 {i}/{len(questions)}: {q['prompt']}")
        if 'hint' in q:
            print(f"  힌트: {q['hint']}")
        if 'choices' in q:
            for j, c in enumerate(q['choices'], 1):
                print(f"  {j}. {c}")
            try:
                ans = input('답 (번호): ').strip()
                idx = int(ans) - 1
                user_answer = q['choices'][idx]
            except (ValueError, IndexError, EOFError, KeyboardInterrupt):
                user_answer = ''
        else:
            try:
                user_answer = input('답: ').strip()
            except (EOFError, KeyboardInterrupt):
                user_answer = ''

        if user_answer == q['answer']:
            print(f"  ✅ 정답!")
            correct += 1
        else:
            print(f"  ❌ 정답: {q['answer']}")
        print()

    print(f'=== 결과: {correct}/{len(questions)} ({100*correct/max(len(questions),1):.0f}%) ===')


if __name__ == '__main__':
    run_cli_quiz()
